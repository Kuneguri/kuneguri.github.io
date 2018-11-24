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
# Module dependencies
import re # Tests only
import requests
try:
    # python3
    from html.parser import HTMLParser
except(ImportError):
    # python2
    from HTMLParser import HTMLParser

class QHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._firstPass = False
        self._recording = 0
        self._currenttag = None
        self._filtertag = dict()
        self._filterattrs = list()
        #self._filterattrs = set()
        self._matches = list()
        self._filteroccur = 1
        self._occur = 0
        self._voids = [ 'comment', 'img', 'link' ]

    def isSubList(self, l1, l2):
        for i in l1:
            if i not in l2:
                return False
        return True

    def getVoidTags(self):
        return self._voids

    def addVoidTag(self, tag):
        self._voids.append(tag)

    def removeVoidTag(self, tag):
        self._voids.remove(tag)

    def setFilter(self, filter, occur=1):
        QHTMLParser.__init__(self)
	self._filtertag = filter.get('tag')
        self._filterattrs = set(filter.get('attrs'))
        self._filteroccur = occur
        self._matches = list()

    def htmloutput(self):
        # TODO: Doesnt work properly.. needs the proper closing-tag order
        #       - fix comment ?
        output = ''
        comment = False
        for i in self._matches:
            if i.get('tag') == 'comment':
                comment = True
                output += '<!-- '
            output += '<' + i.get('tag')
            for attrs in i.get('attrs'):
                if isinstance(attrs, tuple):
                    for attr, value in i.get('attrs'):
                            output += ' ' + attr + '="' + value + '"'
            output += '>' + str(i.get('data')) + '</' + i.get('tag') + '>'
            if comment:
                    output += ' -->'
                    comment = False
        return output

    def handle_starttag(self, tag, attrs):
        self._currenttag = tag
        self._firstPass = True
        if self._recording > 0:
            self._matches.append( { 'tag' : tag, 'attrs' : dict(list(attrs)), 'data' : '' } )
            if tag not in self._voids:
                self._recording += 1
            return
        elif tag != self._filtertag:
            return

        #print(attrs)
        #if self._filtertag == tag and set(self._filterattrs) == set(attrs):
        if self._filtertag == tag and self.isSubList(self._filterattrs, attrs):
            self._occur += 1
            if self._occur == self._filteroccur:
                self._matches.append( { 'tag' : tag, 'attrs' : dict(list(attrs)), 'data' : '' } )
                self._recording = 1

    def handle_data(self, data):
        if self._recording > 0 and self._currenttag not in self._voids:
            self._matches[-1]['data'] += data

    def handle_endtag(self, tag):
        self._currenttag = tag
        if self._recording > 0 and tag not in self._voids:
            self._recording -= 1
        self._firstPass = False

    def handle_comment(self, data):
        self._currenttag = 'comment'
        if self._recording > 0:
            self._matches.append( { 'tag' : 'comment', 'attrs' : '', 'data' : data } )

    def getTags(self):
        #return self._matches
        for i in self._matches:
            yield i

if __name__ == '__main__':
    #data = requests.get('https://masteranime.es/anime/info/sword-art-online-alicization-sub.87310')
    data = requests.get('https://masteranime.es/anime/info/idol-time-pripara')
    import os
    text = ''
    if not os.path.exists('test'):
        with open('test', 'w') as f:
            #data = requests.get('https://masteranime.es/genre/action')
            #data = requests.get('https://masteranime.es/anime/watch/danmachi-gaiden-sword-oratoria/137641')
            f.write(data.text.encode('utf8'))
            text = data.text.encode('utf8')
    else:
        with open('test', 'r') as f:
            text = f.read()
    parser = QHTMLParser()
    #parser.setFilter( { 'tag': 'div', 'filter': [ (u'class', u'ui container grid'), (u'id', u'main') ] } )
    #parser.setFilter( { 'tag' : 'i', 'filter' : [ (u'class', u'close icon') ] }, 1)
    #parser.setFilter( { 'tag' : 'div', 'filter' : [ (u'class', u'cell cover') ] })
    #parser.setFilter( { 'tag' : 'div', 'filter' : [ (u'class', u'sixteen wide mobile six wide tablet four wide computer column'), (u'id', u'details') ] })

    # Plot
    parser.setFilter( { 'tag' : 'div', 'attrs' : [ (u'class', u'sixteen wide column synopsis') ] } )
    # Anime Info Genres
    parser.setFilter( {
        'tag' : 'div',
        'attrs' : [ ( u'class', u'ui tag horizontal list' ) ]
    } )
    # Episodes
    parser.setFilter( {
        'tag' : 'div',
        'attrs' : [ ( u'class', u'sixteen wide column episodes' ) ]
    } )
    # Episode link
    parser.setFilter( {
        'tag' : 'div',
        'attrs' : [ ( u'class', u'video-js vjs-default-skin vjs-big-play-centered player_html5-dimensions vjs-controls-enabled vjs-workinghover vjs-v6 vjs-has-started vjs-paused vjs-user-inactive' ) ]
    } )

    # Genre page
    parser.setFilter( {
        'tag' : 'div',
        'attrs' : [ ( u'class', u'filter-result' ) ]
    } )

    # Stats
    parser.setFilter( { 'tag' : 'div', 'attrs' : [ (u'class', u'ui info list') ] } )

    # Tests
    parser.setFilter( { 'tag' : 'div', 'attrs' : [ (u'class', u'sixteen wide column synopsis') ] } )
    parser.feed(text)
    print('PLOT!!!!!!!!!!!')
    for tag in parser.getTags():
        if tag.get('tag') == 'p' or tag.get('tag') == 'span':
            if tag.get('data'):
                print('Plot:\n{0}\n').format(tag.get('data'))


    # Anime Info Genres
    parser.setFilter( {
        'tag' : 'div',
        'attrs' : [ ( u'class', u'ui tag horizontal list' ) ]
    } )
    parser.feed(text)
    print('INFO GENRES')
    genres = list()
    for tag in parser.getTags():
        if tag.get('tag') == 'a':
            genres.append(tag.get('attrs').get('title', ''))
    print ' - '.join(genres)
    print('\n\n')

    # Stats
    print('STATS!!!!!!')
    parser.setFilter( { 'tag' : 'div', 'attrs' : [ (u'class', u'ui info list') ] } )
    parser.feed(text)
    ret = list()
    for tag in parser.getTags():
        value = re.sub('[^A-Za-z0-9\.\s]', '', tag.get('data').strip())
        if value:
            ret.append(value)
    values = { 'score': '', 'favorites': '', 'totalViews': '', 'status': '', 'episodes': '', 'aired': '' }
    print(ret)
    try:
        ret.remove('Avg. Score')
        values['totalViews'] = ret.pop(0)
        values['favorites'] = ret.pop(0)
        values['score'] = ret.pop(0)
        values['status'] = ret.pop(0)
        values['episodes'] = ret.pop(0)
        values['aired'] = ret.pop(0)
    except IndexError as ex:
        print('INDEX ERROR 1')
    print(values)

#{'tag': 'img', 'data': '', 'attrs': {'src': 'https://static.animecdn.stream/static/img/placeholder/default_poster.png', 'alt': 'Placeholder', 'class': 'placeholder'}}
#{'tag': 'img', 'data': '', 'attrs': {'src': 'https://static.animecdn.stream/media/imagesv2/2018/01/Gintama-Shirogane-no-Tamashii-hen.jpg', 'alt': 'Gintama Season 7', 'class': 'image'}}

#    for i in parser.getTags():
#        if i.get('tag') == 'img':
#            for attr, value in i.get('attrs'):
#                if attr == 'src':
#                    print(value)




