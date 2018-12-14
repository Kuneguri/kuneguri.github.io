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

# Quantum
import lib.utils.qhtmlparser as qhp
import lib.core.quantum as core

# Globals
logger = core.log.getLogger(__name__)
parser = qhp.QHTMLParser()
placeholder = '__PLACEHOLDER__'

####################################################################################
###################### MASTERANIME HTML PARSERS ####################################
####################################################################################
### HTML PARSERS
def parseAnimeMedia(htmldata):
    parser.setFilter( { 'tag' : 'div', 'attrs' : [ (u'class', u'cover') ] } )
    parser.feed(htmldata)
    img = placeholder
    title = placeholder
    for tag in parser.getTags():
        if tag.get('tag') == 'img':
            img = tag.get('attrs').get('src')
            title = tag.get('attrs').get('alt')
            break
    if img:
        item = { 'thumb': img, 'icon': img, 'fanart': img, 'title': title }
    else:
        item = { 'thumb': placeholder, 'icon': placeholder, 'fanart': placeholder, 'title': placeholder }
    return item

def parseAnimeGenres(htmldata):
    # Genre list
    parser.setFilter( { 'tag' : 'div', 'attrs' : [ ( u'class', u'ui tag horizontal list' ) ] } )
    parser.feed(htmldata)
    genres = list()
    for tag in parser.getTags():
        if tag.get('tag') == 'a':
            genres.append(tag.get('attrs').get('title', '').strip())
    if len(genres) < 1:
        genres = [ placeholder ]
    return '|'.join(genres).encode('utf8')

def parseAnimeStats(htmldata):
    # Anime Stats (rating, status, aired, playcount)
    parser.setFilter( { 'tag' : 'div', 'attrs' : [ (u'class', u'ui info list') ] } )
    parser.feed(htmldata)
    ret = list()
    for tag in parser.getTags():
        value = re.sub('[^A-Za-z0-9\.\s]', '', tag.get('data').strip())
        if value:
            ret.append(value)
    values = { 'rating': float(0.0), 'votes': placeholder, 'playcount': placeholder, 'status': placeholder, 'episodes': placeholder, 'aired': placeholder }
    try:
        ret.remove('Avg. Score')
        values['playcount'] =  ret.pop(0).encode('utf8')
        values['votes'] = ret.pop(0).encode('utf8')
        values['rating'] = ret.pop(0).encode('utf8')    ### FLOAT
        values['status'] = ret.pop(0).encode('utf8')
        values['episodes'] = ret.pop(0).encode('utf8')
        values['aired'] = ret.pop(0).encode('utf8')
    except IndexError as ex:
        logger.warn('WARN: Error retriving Anime Stats...\n{0}'.format(ex))
    except:
        raise
    return values

def parseAnimePlot(htmldata):
    # Plot
    parser.setFilter( { 'tag' : 'div', 'attrs' : [ (u'class', u'sixteen wide column synopsis') ] } )
    parser.feed(htmldata)
    plot = ''
    for tag in parser.getTags():
        if tag.get('tag') == 'p' or tag.get('tag') == 'span':
            text = tag.get('data').strip()
            if text:
                # PYTHON 2 - YOU SUCK!!!!!!!!!!!!!!!!!!!!!!!!!!!! CRAP DECODING SHIT
                plot = re.sub('[\x7f-\xff]', '_', text.encode('utf8', errors='replace'))
    if not plot:
        plot = placeholder
        logger.warn('Error parsing info page for "plot": {0}'.format(text))
    return plot

def parseAnimesInGenre(htmldata):
    parser.setFilter( { 'tag' : 'div', 'attrs' : [ ( u'class', u'filter-result' ) ] } )
    parser.feed(htmldata)
    result = list()
    item = dict()
    for tag in parser.getTags():
        if tag.get('tag') == 'img' and tag.get('attrs').get('class') == 'image':
            img = tag.get('attrs').get('src')
            item = { 'thumb' : img, 'icon' : img, 'fanart' : img }
            title = tag.get('attrs').get('alt')
            item['title_img'] = title
        elif tag.get('tag') == 'a' and tag.get('attrs').get('class') == 'title':
            item['link'] = tag.get('attrs').get('href')
            title = tag.get('attrs').get('title')
            item['title'] = title
        if item.get('link') and item.get('thumb'):
            if item not in result:
                if item.get('title_img') != item.get('title'):
                    msg = '--- Title mismatch (img: {0} vs. a: {1})'.format(item.get('title_img'), item.get('title'))
                    logger.warn(msg)
                    raise ValueError (msg)
                else:
                    item.pop('title_img')
                result.append(item)
    return result

def parseAnimeEpisodes(htmldata):
    # Episode list
    parser.setFilter( { 'tag' : 'div', 'attrs' : [ ( u'class', u'sixteen wide column episodes' ) ] } )
    parser.feed(htmldata)
    episodes = list()
    ep = dict()
    for tag in parser.getTags():
        if tag.get('tag') == 'a':
            alt = tag.get('attrs').get('title').encode('utf8')
            ep.update( {
                'title' : alt,
                'link' : tag.get('attrs').get('href')
            } )
        if tag.get('tag') == 'path':
            title = tag.get('data').strip()
            if title:
                ep.update( { 'title': title } )
            if ep not in episodes:
                episodes.append(ep)
                ep = dict()

    episodes.reverse()
    count = 1
    for ep in episodes:
        if 'TRAILER' in ep.get('title', '').upper():
            count = 0
        ep.update( { 'episodeNumber': '{count:>03}'.format(count=count) } )
        count += 1
    return episodes

def parseEpisodeData(htmldata):
    parser.setFilter( { 'tag': 'p', 'attrs': [ (u'class', u'desc' ) ] } )
    parser.feed(htmldata)
    episodeData = dict()
    for tag in parser.getTags():
        episodeData.update( { 'plot': tag.get('data').strip().encode('utf8') } )

    parser.setFilter( { 'tag': 'span', 'attrs': [ ( u'class', u'current-ep' ) ] } )
    parser.feed(htmldata)
    for tag in parser.getTags():
        epText = tag.get('data').strip()
        epNum = re.search('[0-9]+', epText)
        if epNum:
            episodeData.update( { 'episodeNumber': epNum.group() } )
        else:
            episodeData.update( { 'episodeNumber': 9999 } )
            logger.warn('Error getting episode number...')
        if epText:
            episodeData.update( { 'title': epText.encode('utf8') } )
        else:
            episodeData.update( { 'title': placeholder } )
            logger.warn('Error getting episode text...')
    return episodeData

def parseEpisodePlot(htmldata):
    # Get Plot
    parser.setFilter( { 'tag': 'p', 'attrs': [ (u'class', u'desc' ) ] } )
    parser.feed(htmldata)
    plot = ''
    for tag in parser.getTags():
        plot += tag.get('data').strip().encode('utf8')
    return plot

def parseEpisodeServers(htmldata):
    # Get Episode Servers
    parser.setFilter( { 'tag': 'select', 'attrs': [ ( u'id', u'selectServer' ) ] } )
    parser.feed(htmldata)
    serverList = list()
    for tag in parser.getTags():
        if tag.get('tag') == 'option':
            serverList.append(tag.get('data').strip().lower())
    return serverList

def parseVideoURL(htmldata):
    parser.setFilter( {
        'tag' : 'script',
        'attrs' : [ ( u'type', u'text/javascript' ) ]
    } )
    parser.feed(htmldata)
    for tag in parser.getTags():
        txt = re.sub('\n', ' ', tag.get('data'))
        txt = re.search('\$\(document\)\.ready.*function', txt).group()
        if 'setPlayerHTML5' in txt:
            m = re.findall('setPlayerHTML5\(([^\)]+)', txt)
            m = re.search('\[[^\]]+\]', m[0])
            ret = m.group()
        else:
            m = re.search('.*src=["\']([^\'"]+)["\']', txt)
            ret = '[ { "src": "{link}" } ]'.format(link = m.group(1))
    return ret
