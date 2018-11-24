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

# Constants
NEWSEARCH = '___NewSearch___'

def getURL(params):
    return '{pluginURL}?{params}'.format(pluginURL=pluginURL, params=urlencode(params))

def addSeparator():
    item = listItem('-' * 30)
    addDirectoryItem(handle, None, item, False)

def addSearch(params):
    localParams = dict(params)     # Needs to create a new instance of the dict, otherwise it will modify the original pointer o.0... crazy stuff
    provider = localParams.get('provider', 'allproviders')
    localParams.update( { 'action': 'search', 'provider': provider } )
    item = listItem(label='Search: {0}'.format(provider.capitalize()))
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

def getTempFilePath(name):
    return os.path.join( tmpDataPath, name )

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
    response = net.get(url)
    localFile = None
    if response.status_code == 200:
        tempFile = 'playlist-{0}.m3u8'.format(str(time.time()))
        localFile = getTempFilePath(tempFile)
        with open(localFile, 'w') as f:
            f.write(response.text)
    else:
        msg = 'Error downloading the m3u8 file from: {0}'.format(url)
        logger.debug(msg)
        popupError('Playlist download error (m3u8)', msg)
        return
    return localFile
