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
import sys
import os
import shutil

# Quantum
import lib.core.quantum as core
from lib.controllers import controllers

def main(params):
    params = dict(core.parse_qsl(params))
    logger.debug(params)

    if params.get('action') == 'test':
        vid = core.dialog.browseSingle(type=1, heading='Select the video:', shares='files', mask='.m3u8|.m3u|.avi|.flv|.wmv', defaultt=core.tmpDataPath)
        if vid != core.tmpDataPath:
            core.execbuiltin('PlayMedia("{path}")'.format(path=vid))
        return

    if not params:
        mainMenu()
    elif params.get('media') == 'tools':
        toolsMenu(params)
    else:
        delegate(params)
    core.endOfDirectory(core.handle, cacheToDisc=True)

def delegate(params):
    media = params.get('media')

    if media in controllers.mediaControllers.keys():
        mediaController = controllers.mediaControllers.get(media)
        mediaController(params)
    else:
        msg = 'Invalid media parameter: {0} - {1}'.format(media, params)
        logger.warn(msg)
        raise ValueError(msg)

def mainMenu():
    for mediaType, mediaId in controllers.mediaTypes.items():
        params = { 'media': mediaId }
        url = core.getURL(params)
        listItem = core.listItem(label=mediaType)
        listItem.setArt( core.defaultArt )
        isFolder = True
        core.addDirectoryItem(core.handle, url, listItem, isFolder)
    core.addSeparator()
    addTools()

    url = core.getURL( { 'action': 'test' } )
    listItem = core.listItem('Play from Temp')
    core.addDirectoryItem(core.handle, url, listItem, False)

def toolsMenu(params):
    action = params.get('action')
    localParams = dict(params)

    if action == 'list':
        # View Logfile
        localParams =  { 'media': 'tools', 'action': 'read', 'file': core.logPath }
        url = core.getURL(localParams)
        listItem = core.listItem(label='View Log - {0}'.format(core.logFile))
        core.addDirectoryItem(core.handle, url, listItem, False)
        # Clear log
        localParams= { 'media': 'tools', 'action': 'clear-log', 'file': core.logPath }
        url = core.getURL(localParams)
        listItem = core.listItem(label='Clear Log - {0}'.format(core.logFile))
        core.addDirectoryItem(core.handle, url, listItem, False)
        # Clear temp dir
        localParams = { 'media': 'tools', 'action': 'clear-temp', 'tempdir': core.tmpDataPath }
        url = core.getURL(localParams)
        fileNum = len(os.listdir(core.tmpDataPath))
        listItem = core.listItem(label='Clear Temp Dir - {0} files'.format(fileNum))
        core.addDirectoryItem(core.handle, url, listItem, False)
        # Clear search history
        for media in controllers.mediaControllers.keys():
            localParams = { 'media': 'tools', 'action': 'clear-search', 'histfile': media }
            url = core.getURL(localParams)
            listItem = core.listItem(label='Clear search history for: {0}'.format(media.capitalize()))
            core.addDirectoryItem(core.handle, url, listItem, False)

    elif action == 'clear-search':
        histfile = core.getSearchFile(params.get('histfile'))
        if os.path.exists(histfile):
            os.unlink(histfile)
        core.execbuiltin('Notification("Search cleared", "{0} cleared")'.format(params.get('histfile')))

    elif action == 'read':
        filePath = params.get('file')
        core.displayTextFile(core.logFile, filePath)

    elif action == 'clear-temp':
        tmpDir = localParams.get('tempdir')
        count = 0
        for f in os.listdir(tmpDir):
            count += 1
            fullPath = os.path.join(tmpDir, f)
            if os.path.isdir( fullPath ):
                shutil.rmtree( fullPath )
            else:
                os.unlink( fullPath )
        core.execbuiltin('Notification("TempDir cleared", "{0} files removed")'.format(count))

    elif action == 'clear-log':
        filePath = params.get('file')
        with open(filePath, 'w') as f:
            f.write('')
        core.execbuiltin('Notification("Log cleared", "The logfile has been truncated")')
    return

def addTools():
    localParams = { 'action': 'list', 'media': 'tools' }
    url = core.getURL(localParams)
    listItem = core.listItem(label='Quantum Tools')
    listItem.setArt( core.defaultArt )
    core.addDirectoryItem(core.handle, url, listItem, True)

if __name__ == '__main__':
    logger = core.log.getLogger(core.addonId)
    main(sys.argv[2][1:])
