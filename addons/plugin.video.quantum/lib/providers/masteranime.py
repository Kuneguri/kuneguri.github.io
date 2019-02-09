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
import re
import json

# Quantum
import lib.core.quantum as core
import lib.core.cache as cache
import lib.utils.net as net

# Masteranime
import lib.parsers.masteranime as parser
import lib.settings.masteranime as settings

# Globals
logger = core.log.getLogger(__name__)
db = cache.QCache(settings.providerId)
db.createTable(settings.mediaTable, settings.mainDbData)


####################################################################################
### SCREEN HANDLERS
def main(params):
    path = params.get('path')
    mediaId = params.get('mediaId')
    episodeId = params.get('episodeId')

    # Playing!!!
    if params.get('action') == 'play' and episodeId and mediaId:
        playVideo(params)

    # Anime Episode
    elif episodeId: # and mediaId
        episodeMenu(params)

    # Anime
    elif mediaId:   # and not episodeId
        mediaMenu(params)

    # Main Screen
    elif not path:
        # Displays main screen
        mainMenu(params)
    # If path == 'genres' -> Genres menu... For now, it is the only option
    elif path == 'genres':
        genresMenu(params)
    elif path == 'releases':
        releasesMenu(params)
    elif path == 'trending':
        trendingMenu(params)
    else:
        msg = 'Invalid path: {0}'.format(params)
        logger.warn(msg)
        raise ValueError(msg)

def releasesMenu(params):
    data = net.get(settings._releasesURL)
    if not data:
        msg = 'Network error getting releases data from: {0}'.format(settings._releasesURL)
        logger.debug(msg)
        core.popupError('Network error', msg)
        return
    if data.status_code == 200:
        try:
            releases = json.loads(data.text)
        except:
            msg = 'Error reading json data: {0}'.format(data.text)
            logger.debug(msg)
            core.popupError('JSON error', msg)
            return
        animeList = list()
        for anime in releases:
            if anime not in animeList:
                animeList.append( anime.get('anime').get('slug') )
        total = len(animeList)
        count = 0
        line1 = 'Loading: ...'
        pDialog = core.pDialog
        pDialog.create('Loading animes...', line1)
        pDialog.update(0)
        for anime in animeList:
            if pDialog.iscanceled():
                break
            count += 1
            addAnimeItem(anime, params)
            pct = int(float(count) / float(total) * 100)
            pDialog.update(pct, 'Loading: {0}'.format(anime))
        pDialog.close()
    else:
        msg = 'HTTP error getting data from: {0}'.format(settings._releasesURL)
        logger.debug(msg)
        core.popupError('HTTP Error', msg)

def trendingMenu(params):
    data = net.get(settings._trendingURL)
    if not data:
        msg = 'Network error getting trending data from: {0}'.format(settings._trendingURL)
        logger.debug(msg)
        core.popupError('Network error', msg)
        return
    if data.status_code == 200:
        try:
            trendingDict = json.loads(data.text)
        except:
            msg = 'Error reading json data: {0}'.format(data.text)
            logger.debug(msg)
            core.popupError('JSON error', msg)
            return
        animeList = list()
        for anime in trendingDict.get('being_watched'):
            animeList.append( anime.get('slug') )
        for anime in trendingDict.get('popular_today'):
            if anime.get('slug') not in animeList:
                animeList.append( anime.get('slug') )
        total = len(animeList)
        count = 0
        line1 = 'Loading: ...'
        pDialog = core.pDialog
        pDialog.create('Loading animes...', line1)
        pDialog.update(0)
        for anime in animeList:
            if pDialog.iscanceled():
                break
            count += 1
            addAnimeItem(anime, params)
            pct = int(float(count) / float(total) * 100)
            pDialog.update(pct, 'Loading: {0}'.format(anime))
        pDialog.close()
    else:
        msg = 'HTTP error getting data from: {0}'.format(settings._trendingURL)
        logger.debug(msg)
        core.popupError('HTTP Error', msg)


def mainMenu(params):
    localParams = dict(params)
    # Add a search
    core.addSearch(localParams)
    core.addSeparator()
    # Genres option
    localParams.update( { 'action': 'list', 'path': 'genres' } )
    url = core.getURL(localParams)
    listItem = core.listItem(label='Genres')
    core.addDirectoryItem(core.handle, url, listItem, True)
    # Trending option
    localParams.update( { 'action': 'list', 'path': 'trending' } )
    url = core.getURL(localParams)
    listItem = core.listItem(label='Trending')
    core.addDirectoryItem(core.handle, url, listItem, True)
    # Releases option
    localParams.update( { 'action': 'list', 'path': 'releases' } )
    url = core.getURL(localParams)
    listItem = core.listItem(label='Releases')
    core.addDirectoryItem(core.handle, url, listItem, True)

def genresMenu(params):
    localParams = dict(params)
    localParams.update( { 'action': 'list' } ) # cosmetic...
    genre = localParams.get('genre')

    if genre:
        genreMenu(params)
    else:
        for genre in settings._genreList:
            localParams.update( { 'genre': genre } )
            url = core.getURL(localParams)
            listItem = core.listItem(label=genre.capitalize())
            core.addDirectoryItem(core.handle, url, listItem, True)
    core.endOfDirectory(core.handle, cacheToDisc=True)

def genreMenu(params):
    genre = params.get('genre')
    if not genre:
        msg = 'Invalid call for empty genre: {0}'.format(params)
        logger.error(msg)
        raise ValueError(msg)
    data = net.get(settings._genreURL.format(genre=genre))
    if not data:
        return
    if data.status_code == 200:
        animes = parser.parseAnimesInGenre(data.text)
        count = 0
        total = len(animes)
        pDialog = core.pDialog
        line1 = 'Loading: ...'
        pDialog.create('Loading animes...', line1)
        pDialog.update(0)
        for anime in core.sortDictList(animes, 'title'):
            if pDialog.iscanceled():
                break
            count += 1
            animeId = getAnimeIdFromURL(anime.pop('link'))
            percentage = int(float(count) / float(total) * 100)
            line1 = 'Loading: {0}'.format(anime.get('title').encode('utf8'))
            line2 = 'Completed {0} of {1}'.format(count, total)
            pDialog.update(percentage, line1, line2)
            addAnimeItem(animeId, params)
        pDialog.close()
    else:
        msg = 'Network failure loading Genre page: {0}'.format(settings._genreURL.format(genre=genre))
        logger.error(msg)
        core.popupError('Network error', msg)

def latestMenu(params):
    pass

####################################################################################
### Media handler (play, list episodes, whatever)
def mediaMenu(params):
    localParams = dict(params)

    # Pre-populate a dict with info about the Anime for the header and plot
    animeId = params.get('mediaId')
    listItemDict = { 'mediatype': 'video', 'mediaId': animeId, 'title': '', 'plot': '', 'thumb': '', 'icon': '', 'fanart': '', 'year': '', 'genre': '', 'aired': '' }
    db.updateDict(settings.mediaTable, listItemDict)
    mediaAired = listItemDict.pop('aired')
    mediaPlot = listItemDict.get('plot') + '\n{0}'.format(mediaAired)
    if not listItemDict.get('year'):
        listItemDict.pop('year')
    header = core.listItem(label='--- [B][COLOR springgreen]{0}[/B][/COLOR]:'.format(listItemDict.get('title')))
    core.addDirectoryItem(core.handle, None, header, False)

    ret = list()
    episodeList = getEpisodeList(animeId)
    for ep in episodeList:
        # Update the anime (with images, plot, etc) with data for the episode
        listItemDict.update( ep )

        # Setup and add item to the directory/menu
        listItem = core.listItem(label=listItemDict.get('title'))
        localParams.update( { 'mediaId': animeId, 'episodeId': listItemDict.get('episodeId'), 'action': 'list' } )
        url = core.getURL(localParams)
        listItem.setInfo( 'video', listItemDict )
        listItem.setArt( listItemDict )
        core.addDirectoryItem(core.handle, url, listItem, True)
        #count += 1

def episodeMenu(params):
    mediaId = params.get('mediaId')
    episodeId = params.get('episodeId')
    localParams = dict(params)

    # Just to setup images, plot and such on the links as well.. 
    mediaDict = getAnimeData(mediaId)
    episodeDict = getEpisodeData(mediaId, episodeId)
    if not episodeDict.get('plot'):
        # If we have a plot for the episode page => update the DB. Note: It doesn't seem that episodes have different plots, so this is just duplicating the anime one.. 
        episodeDict.update( { 'plot': mediaDict.get('plot') } )
    mediaDict.pop('year'); mediaDict.pop('aired')
    mediaDict.update( episodeDict )
    # setArt fails with the servers object... dumb stuff
    mediaDict.pop('servers')
    for server in episodeDict.get('servers'):
        ### List servers
        localParams.update( { 'streamId': server, 'action': 'play' } )
        url = core.getURL(localParams)
        listItem = core.listItem(server.upper())
        listItem.setInfo( 'video', mediaDict )
        listItem.setArt( mediaDict )
        #listItem.setProperty( 'IsPlayable', 'true' )        ### NEED CONFIRMATION
        core.addDirectoryItem(core.handle, url, listItem, False)

def getValidSession():
    headers = {
            'Origin': 'https://masteranime.es',
            'Referer': 'https://masteranime.es',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
            }
    s = net.QuantumSession(headers)
    response = s.HEAD(settings._rootURL)
    if response:
        if response.status_code == 200 and response.cookies.get('__cfduid'):
            return s
        else:
            logger.debug('Error getting valid cookie session')
            core.popupError('Network error', 'Error getting session cookie')
            return None

def getAuthURL(session, episodeId, server):
    url = settings._videoAuthURL.format(server=server)
    postData = { 'episode_id': episodeId }
    response = session.POST(url, postData)
    if response:
        if response.status_code == 200:
            try:
                statusDict = json.loads(response.text)
            except Exception as ex:
                msg = 'Error parsing AuthURL JSON message: {0}'.format(ex)
                logger.error(msg)
                core.popupError('JSON Error', msg)
                return
        else:
            msg = 'HTTP error with AuthURL: {0}'.format(response)
            logger.error(msg)
            core.popupError('HTTP Error', msg)
            return
        if not statusDict.get('status'):
            msg = 'AuthURL "status": {0}'.format(statusDict.get('status'))
            logger.debug(msg)
            core.popupError('Video Status...', msg)
        if statusDict.get('value') and '<iframe' not in statusDict.get('value'):
            return statusDict.get('value')
        elif '<iframe' in statusDict.get('value'):
            valueURL = re.search('src="([^"]+)" ', statusDict.get('value'))
            if valueURL:
                valueURL = valueURL.group(1)
                return valueURL

def getVideoPlaylist(session, url):
    response = session.GET(url)
    playlist = None
    if response:
        if response.status_code == 200:
            try:
                playlistDict = json.loads(response.text)
            except ValueError as ex:
                try:
                    playlistStr = parser.parseVideoURL(response.text)
                    playlist = json.loads(playlistStr)
                    for i in playlist:
                        if i.get('src'):
                            i.update( { 'file': i.get('src') } )
                except ValueError as ex:
                    msg = 'Error parsing AuthURL JSON message: {0}'.format(ex)
                    logger.error(msg)
                    core.popupError('JSON Error', msg)
                    return
        else:
            msg = 'HTTP error with AuthURL: {0}'.format(response)
            logger.error(msg)
            core.popupError('HTTP Error', msg)
            return
        if not playlist:
            playlist = playlistDict.get('playlist')
        if not playlist:
            msg = 'Missing object "playlist" from response... {0}'.format(playlistDict)
            logger.debug(msg)
            core.popupError('Missing playlist', msg)
            return

        for i in playlist:
            sources = i.get('sources')
            if sources:
                return sources
            #elif i.get('file'):
            else:
                return playlist
        msg = 'Neither "sources" nor "file" found on playlist: {0}'.format(playlist)
        logger.debug(msg)
        core.popupError('Invalid playlist format', msg)
        return None

def playVideo(params):
    mediaId = params.get('mediaId')
    episodeId = params.get('episodeId')
    streamId = params.get('streamId')

    sess = getValidSession()
    authURL = getAuthURL(sess, episodeId, streamId)
    playlist = getVideoPlaylist(sess, authURL)

    #logger.debug(playlist)
    if not playlist:
        return
    vidURL = selectVidQuality(playlist)
    if vidURL:
        core.execbuiltin('PlayMedia("{0}")'.format(vidURL))
        return
        #core.execbuiltin('Action(Fullscreen)')
    else:
        # User canceled the quality menu
        return

def selectVidQuality(playlist):
    qualityList = list()
    fileList = list()
    for i in playlist:
        if i.get('label'):
            qualityList.append( i.get('label') )
        elif i.get('file'):
            fileList.append( i.get('file') )

    vidURL = None
    if qualityList:
        if len(qualityList) > 1:
            choice = core.dialog.select('Select the video quality:', qualityList)
            if choice == -1:
                return None
            else:
                quality = qualityList[ choice ]
        elif len(qualityList) == 1:
            quality = qualityList[0]
        for i in playlist:
            if quality == i.get('label'):
                vidURL = i.get('file')

    elif fileList:
        if len(fileList) > 1:
            choice = core.dialog.select('Select the video link:', fileList)
            if choice != -1:
                file = fileList[ choice ]
        elif len(fileList) == 1:
            file = fileList[0]
        vidURL = file

    if not vidURL:
        msg = 'No "file" object found for qualit {1}: {0}'.format(playlist, quality)
        logger.debug(msg)
        core.popupError('No vidURL found', msg)
        return

    if 'm3u8' in vidURL:
        #core.execbuiltin('Notification("Downloading m3u8", "Note: m3u8 streams suck")')
        vidURL = core.m3uDownload(vidURL)

    return vidURL


####################################################################################
### CACHE / CONTENT HANDLERS
def getAnimeData(animeId):
    animeDict = { 'mediaId': animeId, 'mediatype': 'video' }
    thumb, icon, fanart, genre, year, rating, title, plot, status, aired, votes = None, None, None, None, None, None, None, None, None, None, None
    cur = db.sql('SELECT thumb, icon, fanart, genre, year, rating, title, plot, status, aired, votes FROM {mediaTable} where mediaId=?'.format(mediaTable=settings.mediaTable), (animeId, ))
    res = cur.fetchone()
    if res:
        thumb, icon, fanart, genre, year, rating, title, plot, status, aired, votes = res

    if not (plot and title and fanart and genre):
        animeDict = updateAnimeData(animeId)
    else:
        animeDict.update( { 'thumb': thumb, 'icon': icon, 'fanart': fanart, 'genre': genre, 'year': year, 'rating': rating, 'title': title, 'plot': plot, 'status': status, 'aired': aired, 'votes': votes } )
    return animeDict

def updateAnimeData(animeId):
    animeDict = { 'mediaId': animeId }
    data = net.get(settings._animeURL.format(animeId=animeId))
    if not data:
        logger.error('NETWORK ERROR - {0} - {1}'.format(animeId, data))
        return None
    if data.status_code == 200:
        animeDict.update( parser.parseAnimeMedia(data.text) )
        animeDict.update( { 'plot': '\n' + parser.parseAnimePlot(data.text) } )
        animeDict.update( { 'genre': parser.parseAnimeGenres(data.text) } )
        statsDict = parser.parseAnimeStats(data.text)
        animeDict.update(statsDict)
        year = re.search('[0-9]{4}', animeDict.get('aired'))
        if year:
            animeDict.update( { 'year': year.group() } )
        else:
            animeDict.update( { 'year': '' } )

        db.updateDb(settings.mediaTable, animeDict)
    return animeDict

def getEpisodeList(mediaId):
    url = settings._animeURL.format(animeId=mediaId)
    data = net.get(url)
    if not data:
        msg = 'Network error collecting episodes for {0}'.format(animeId)
        logger.error(msg)
        core.popupError('Network error...', msg)
        return

    episodeList = parser.parseAnimeEpisodes(data.text)
    for ep in episodeList:
        episodeId = getEpisodeIdFromURL(ep.get('link'))
        ep.update( { 'episodeId': episodeId, 'mediaId': mediaId } )
        #ep.pop('link')

    return episodeList


####################################################################################
### HELPERS
def getEpisodeData(mediaId, episodeId, headers=None):
    url = settings._episodeURL.format(animeId=mediaId, episodeId=episodeId)
    data = net.get(url)
    if not data:
        msg = 'Network error downloading episode URL: {0}'.format(url)
        logger.error(msg)
        core.popupError('Network error', msg)
        return
    if data.status_code == 200:
        episodeDict = dict()
        plot = parser.parseEpisodePlot(data.text)
        if plot:
            episodeDict.update( { 'plot' : plot } )
        else:
            episodeDict.update( { 'plot' : '' } )
        servers = parser.parseEpisodeServers(data.text)
        episodeDict.update( { 'servers' : servers } )
        return episodeDict
    else:
        msg = 'HTTP error from url: {0}\nError: {1}'.format(url, data)
        logger.error(msg)
        core.popupError('HTTP Error', msg)
        return

def getAnimeIdFromURL(url):
    animeId = re.sub('.*/', '', url)
    return animeId

def getEpisodeIdFromURL(url):
    animeId = re.sub('.*/', '', url)
    return animeId

def addAnimeItem(animeId, params):
    localParams = dict(params)
    localParams.update( { 'mediaId' : animeId } )
    animeData = getAnimeData(animeId)
    if animeData:
        url = core.getURL(localParams)
        animeData.update( { 'mediatype': 'video' } )
        listItem = core.listItem(label=animeData.get('title'))
        animeData.pop('aired')
        if not animeData.get('year'):
            animeData.pop('year')
        listItem.setInfo('video', animeData)
        listItem.setArt(animeData)
        core.addDirectoryItem(core.handle, url, listItem, True)
    else:
        msg = 'Error loading anime data: {0}. Check logs'.format(animeId)
        logger.error(msg)
        core.popupError('Error loading anime data', msg)

def doSearch(query):
    url = settings._searchURL.format(query=query)
    data = net.get(url)
    if not data:
        return None
    pdialog = core.pDialog
    heading = '[B][COLOR springgreen]{0}[/B][/COLOR] - Searching for "{1}"...'.format(settings.providerId.capitalize(), query)
    pdialog.create(heading, 'Total matches: ?')
    if data.status_code == 200:
        result = None
        try:
            result = json.loads(data.text)
        except Exception as ex:
            msg = 'Error on json response. Exception: \n{ex}'.format(ex=ex)
            core.popupError('JSON Parsing error...', msg)
            logger.error(msg)
            return None
        ret = list()
        total = len(result)
        count = 0
        for i in result:
            if pdialog.iscanceled():
                break
            animeId = i.get('slug')
            count += 1
            line1 = 'Total matches: {0}'.format(total)
            line2 = 'Loading {count:>02}: {title}'.format(count=count, title=i.get('title'))
            pct = int(float(count) / float(total) * 100)
            pdialog.update(pct, line1, line2)
            animeDict = getAnimeData(animeId)
            if animeDict:
                animeDict.update( { 'mediaId': animeId, 'media': 'anime' } )
                ret.append(animeDict)
            else:
                msg = 'Error loading anime data for: {0}. Check logs.'.format(animeId)
                logger.error(msg)
                core.popupError('Error loading anime data.', msg)
        pdialog.close()
        return ret
    else:
        pdialog.close()
        msg = 'Network failure searching on: {0}'.format(url)
        logger.error(msg)
        raise net.requests.ConnectionError(msg)

