#-*- coding: UTF-8 -*-
#    This file is part of 'Quantum Video Add-on'.
#
#    'Quantum Video Add-on' is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    'Quantum Video Add-on' is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with 'Quantum Video Add-on'.  If not, see <https://www.gnu.org/licenses/>.
import sqlite3
import re
import hashlib
import os

# Quantum
import lib.core.quantum as core
import lib.utils.net as net

class QCache(object):
    def __init__(self, fileName):
        filePath = core.getCachePath(fileName)
        self._fileName = filePath
        self._conn = sqlite3.connect(self._fileName)
        self._logger = core.log.getLogger(__name__)

    def createTable(self, tableName, columnList):
        createCommand = 'CREATE TABLE IF NOT EXISTS {table} ('
        cols = [ '{0} {1}'.format(column, params) for column, params in columnList ]
        createCommand += ', '.join(cols) + ')'
        createCommand = createCommand.format(table=tableName)
        cur = self._conn.cursor()
        cur.execute(createCommand)
        self._conn.commit()
        return cur

    def sql(self, command, values=None):
        cur = self._conn.cursor()
        if values:
            cur.execute(command, values)
        else:
            cur.execute(command)
        self._conn.commit()
        return cur

    def close(self):
        self._conn.commit()
        self._conn.close()

    def _createCacheStorage(self, urlHash):
        prefix = urlHash[0:2]
        dirPath = os.path.join(core.cacheMediaPath, prefix)
        if not os.path.exists(dirPath):
            core.xbmcvfs.mkdir(dirPath)
        return os.path.join(dirPath, urlHash)

    def getCachePath(self, url):
        urlHash = hashlib.sha256(url).hexdigest()
        path = self._createCacheStorage(urlHash)
        if os.path.exists(path):
            return path
        else:
            success = self._downloadToCache(url, path)
        if success:
            return path
        else:
            return url

    def _downloadToCache(self, link, localPath):
        data = net.get(link)
        if not data:
            return False
        success = False
        if data.status_code == 200:
            with open(localPath, 'wb') as f:
                for chunk in data.iter_content(4096):
                    f.write(chunk)
            success = True
        else:
           self._logger.error('Failed downloading: {0}'.format(link))
           raise net.requests.ConnectionError(msg)
        return success

    def updateDb(self, table, dictData, replace=True):
        for media in [ 'thumb', 'icon', 'fanart' ]:
            path = dictData.get(media)
            if path:
                if not os.path.exists(path):
                    localPath = self.getCachePath(dictData.get(media))
                    dictData.update( { media: localPath })
        ### Python 2 is so dumb... It decodes the string before encoding, and it fails decoding unicode chars...
        for key in dictData.keys():
            if isinstance(dictData.get(key), str):
                safeText = re.sub('[\x7f-\xff]', '_', dictData.get(key)).encode('utf8', errors='replace')
                dictData.update( { key: safeText } )
        if replace:
            cmd = 'REPLACE INTO {table} ('.format(table=table)
        else:
            cmd = 'INSERT INTO {table} ('.format(table=table)
        cmd += ', '.join(dictData.keys())
        cmd += ') VALUES ('
        cmd += ', '.join( [ '?' for x in dictData.values() ] )
        cmd += ')'
        self.sql(cmd, tuple(dictData.values()))


    def updateDict(self, table, dataDict):
        mediaId = dataDict.get('mediaId')
        episodeId = dataDict.get('episodeId')
        for key in dataDict.keys():
            if not dataDict.get(key):
                if mediaId and episodeId:
                    cur = self.sql('SELECT {key} FROM {table} WHERE mediaId=? and episodeId=?'.format(key=key, table=table), (mediaId, episodeId))
                elif mediaId:
                    cur = self.sql('SELECT {key} FROM {table} WHERE mediaId=?'.format(key=key, table=table), (mediaId, ))
                res = cur.fetchone()
                if res:
                    dataDict.update( { key : res[0] } )
        return dataDict








