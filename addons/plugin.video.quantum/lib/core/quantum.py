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
# Native
import time
import sys
import os
import re
from threading import Thread
from Queue import Queue

# Kodi
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from urllib import urlencode
from urlparse import parse_qsl

# Quantum
from lib.utils.logger import Logger

# Definitions
addonId = 'Quantum'
handle = int(sys.argv[1])

# URLs
pluginId = xbmcaddon.Addon().getAddonInfo('Id')
#pluginURL = 'plugin://' + pluginId + '/'
pluginURL = sys.argv[0]
pluginProfile = xbmcaddon.Addon().getAddonInfo('profile')

# Paths
addonPath = xbmcaddon.Addon().getAddonInfo('path')
logFile = addonId.lower() + '.log'
logPath = os.path.join(addonPath, 'logs', logFile)
userDataPath = xbmc.translatePath(pluginProfile).encode('utf8')
if not os.path.exists(userDataPath):
    xbmcvfs.mkdir(userDataPath)
defaultArt = {  'thumb': os.path.join( addonPath, 'resources/images/icon.png' ),
                'fanart': os.path.join( addonPath, 'resources/images/fanart.png' ),
                'icon': os.path.join( addonPath, 'resources/images/icon.png' )
            }

# Create cache path
cacheDataPath = os.path.join(userDataPath, 'cache')
if not os.path.exists(cacheDataPath):
    xbmcvfs.mkdir(cacheDataPath)
cacheMediaPath = os.path.join(cacheDataPath, 'media')
if not os.path.exists(cacheMediaPath):
    xbmcvfs.mkdir(cacheMediaPath)
tmpDataPath = os.path.join(userDataPath, 'temp')
if not os.path.exists(tmpDataPath):
    xbmcvfs.mkdir(tmpDataPath)

# Properties
log = Logger(logPath)
logger = log.getLogger(__name__)

# Functions
INPUT_ALPHANUM = xbmcgui.INPUT_ALPHANUM
dialog = xbmcgui.Dialog()
pDialog = xbmcgui.DialogProgress()
pDialogBG = xbmcgui.DialogProgressBG
listItem = xbmcgui.ListItem
addDirectoryItem = xbmcplugin.addDirectoryItem
endOfDirectory = xbmcplugin.endOfDirectory
execbuiltin = xbmc.executebuiltin
m3uQueue = Queue()
m3uMaxThreads = 20

# Constants
NEWSEARCH = '___NewSearch___'

def getURL(params):
    return '{pluginURL}?{params}'.format(pluginURL=pluginURL, params=urlencode(params))

def addSeparator():
    item = listItem('-' * 30)
    item.setArt( defaultArt )
    addDirectoryItem(handle, None, item, False)

def addSearch(params):
    localParams = dict(params)     # Needs to create a new instance of the dict, otherwise it will modify the original pointer o.0... crazy stuff
    provider = localParams.get('provider', 'allproviders')
    localParams.update( { 'action': 'search', 'provider': provider } )
    item = listItem(label='Search: {0}'.format(provider.capitalize()))
    item.setArt( defaultArt )
    url = getURL(localParams)
    addDirectoryItem(handle, url, item, True)

def getSearchFile(fileName):
    return os.path.join(cacheDataPath, fileName)

def getCachePath(fileName):
    return os.path.join(cacheDataPath, fileName + '.db')

def sortDictList(dictList, sortby='title'):
    return sorted(dictList, key=lambda k: k.get(sortby))

def popupError(heading, msg):
    heading = '[B][COLOR red] - ' + heading + '[/B][/COLOR]'
    execbuiltin('Notification("{heading}", "{msg}")'.format(heading=heading, msg=msg))
    # Too annoying?
    #errDialog = dialog.textviewer(heading, msg)
    #del errDialog

def getTempFilePath(name, makedir=False):
    path = os.path.join( tmpDataPath, name )
    if makedir:
        os.mkdir(path)
    return path

def searchHistory(params):
    media = params.get('media')
    file = getSearchFile(media)
    newSearch = dict(params)
    newSearch.update( { 'query': NEWSEARCH } )
    url = getURL(newSearch)
    item = listItem(label='New search...')
    addDirectoryItem(handle, url, item, True)
    if os.path.exists(file):
        localParams = dict(params)
        with open(file, 'r') as f:
            for line in f.xreadlines():
                value = line.strip()
                localParams.update( { 'query': value } )
                url = getURL(localParams)
                item = listItem(label=value)
                addDirectoryItem(handle, url, item, True)

def addSearchHistory(media, query):
    file = getSearchFile(media)
    new = True
    if os.path.exists(file):
        with open(file, 'r') as fr:
            if '{0}\n'.format(query.lower()) in fr.read():
                new = False
    if new:
        with open(file, 'a') as fw:
            fw.write('{0}\n'.format(query))


def displayTextFile(title, filePath):
    if os.path.exists(filePath):
        with open(filePath, 'r') as f:
            dialog.textviewer(title, f.read())
    else:
        msg = 'Invalid call: File not found - {0}'.format(filePath)
        logger.error(msg)
        raise FileNotFoundError(msg)

def m3uDownload(url):
    import lib.utils.net as net
    tempFile = 'playlist-{0}.m3u8'.format(str(time.time()))
    options = [ 'Download & Play', 'Stream Online' ]
    sel = dialog.select('Select the play mode:', options)
    downloadToDisk = False
    if sel == 0:
        downloadToDisk = True
    if downloadToDisk:              # Works on OSX, but not on windows (demuxer error)
        localPath = getTempFilePath(tempFile, makedir=True)
        localFile = os.path.join( localPath, tempFile )
        data = net.get(url)
        url2 = None
        with open(localFile, 'w') as fw:
            for line in data.text.splitlines():
                #if 'http' in line[0:10]:
                if 'http' in line[0:10] and '.m3u' in line:
                    url2 = line
                    line = re.sub('.*/', '{0}/'.format(localPath), line)
                fw.write('{0}\n'.format(line))
        if url2:
            data = net.get(url2)
            urlList = list()
            streamRoot = re.search( '.*/', url2 )
            indexFile = re.sub('.*/', '', url2)
            indexFile = os.path.join( localPath, indexFile )
            if streamRoot:
                streamRoot = streamRoot.group()
            else:
                popupError('Error 01', 'Error getting streamRoot url')
                return
            with open(indexFile, 'w') as fw:
                total = 0
                for line in data.text.splitlines():
                    if '#' not in line[0:10]:
                        #urlList.append( '{streamRoot}{indexFile}'.format(streamRoot=streamRoot, indexFile=line) )
                        m3uQueue.put( '{streamRoot}{indexFile}'.format(streamRoot=streamRoot, indexFile=line) )
                        total += 1
                    # For whatever reason.. I can't play from local files using jpg but .ts works fine
                    fw.write('{0}\n'.format(line.replace('.jpg', '.ts')))
        pd = pDialog
        pd.create('Downloading chunks', 'Loading...')
        pd.update(0)
        for thread in range(m3uMaxThreads):
            #count += 1
            #if pd.iscanceled():
            #    return
            #pct = int( float(count) / float(total) * 100 )
            #pd.update(pct, 'Downloading chunk {0} of {1}'.format(count, total))
            t = Thread(target=downloaderThread, args=(localPath, pd, total))
            #t.daemon = True
            t.start()
            #t.join()
        m3uQueue.join()
        if pd.iscanceled():
            pd.close()
            popupError('Canceled', 'Download canceled')
            return
        pd.close()
        return localFile
        #return indexFile
    else:
        localFile = getTempFilePath(tempFile)
        response = net.get(url)
        if response.status_code == 200:
            with open(localFile, 'w') as f:
                f.write(response.text)
        else:
            msg = 'Error downloading the m3u8 file from: {0}'.format(url)
            logger.debug(msg)
            popupError('Playlist download error (m3u8)', msg)
            return
        return localFile

def downloaderThread(dstPath, pDlg, total):
    import lib.utils.net as net
    url = m3uQueue.get()
    while url:
        if pDlg.iscanceled():
            m3uQueue.task_done()
            while not m3uQueue.empty():
                url = m3uQueue.get()
                m3uQueue.task_done()
            return
        qsize = m3uQueue.qsize()
        #logger.debug('Initiated thread. Queue size: {0}'.format(qsize))
        #url = m3uQueue.get()
        fileName = re.sub('.*/', '', url).replace('.jpg', '.ts')
        filePath = os.path.join(dstPath, fileName)
        data = net.get(url, timeout=10)
        if data and data.status_code == 200:
            pct = 100 - qsize if qsize < 100 else 0
            pDlg.update(pct, 'Remaining chunks: {0}'.format(qsize))
            with open(filePath, 'wb') as fw:
                for chunk in data.iter_content(4096):
                    fw.write(chunk)
            m3uQueue.task_done()
        else:
            m3uQueue.task_done()
            m3uQueue.put(url)
        url = m3uQueue.get()


class M3uDownloader(Thread):
    def __init__(self, urlList, dstPath):
        super(M3uDownloader, self).__init__(self)
        self._urlList = urlList
        self._dstPath = dstPath

    def run(self):
        import lib.utils.net as net
        #logger.debug('Initiated thread')
        for url in self._urlList:
            fileName = re.sub('.*/', '', url)
            filePath = os.path.join(self._dstPath, fileName)
            data = net.get(url, timeout=10)
            with open(filePath, 'wb') as fw:
                for chunk in data.iter_content(4096):
                    fw.write(chunk)






