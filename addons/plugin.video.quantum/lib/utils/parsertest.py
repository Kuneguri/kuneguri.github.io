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
    headers = {     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:63.0) Gecko/20100101 Firefox/63.0',
                    'Referer': 'https://masteranime.es'
            }
    url = 'https://embed.streamx.me/?k=d12ce96fc0c1e1b87d698ce3fe5533b3c5b9a57d46a47275428b48c157528e4c&li=115946&tham=1543636518&lt=fb&qlt=720p&spq=p&prv=bWVkaWEvdGh1bWIvMTcwMTA2XzA3MDg0NC9Td29yZC1BcnQtT25saW5lLUR1Yi1FcGlzb2RlLTAyNS5qcGc7bWVkaWEvdGh1bWIvMTcwMTA2XzA3MDg0NC9Td29yZC1BcnQtT25saW5lLUR1Yi1FcGlzb2RlLTAyNV9tb2JpbGUuanBn&key=3dfaffb37c856959519505ed78b879cf&h=1543636518&cc=AU'
    url = 'https://embed.streamx.me/?k=98be312fd839a679bcafe3a851c33eb426626d269d3a47b0fcb2326efbc07ae8&li=148027&tham=1543637312&lt=fb&qlt=720p&spq=p&prv=&key=c3ef73095535beffef90ea9a73863c06&h=1543637312&cc=AU&_=1543637307572'
    import os
    text = ''
    if not os.path.exists('test'):
        with open('test', 'w') as f:
            print('Online request')
            #data = requests.get('https://masteranime.es/genre/action')
            data = requests.get(url, headers=headers)
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
    # Anime Info Genres
    parser.setFilter( {
        'tag' : 'script',
        'attrs' : [ ( u'type', u'text/javascript' ) ]
    } )
    parser.feed(text)
    for tag in parser.getTags():
        txt = re.sub('\n', ' ', tag.get('data'))
        txt = re.search('\$\(document\)\.ready.*function', txt).group()
        if 'setPlayerHTML5' in txt:
            m = re.findall('setPlayerHTML5\(([^\)]+)', tag.get('data'))
            m = re.search('\[[^\]]+\]', m[1])
            ret = m.group()
        else:
            m = re.search('.*src=["\']([^\'"]+)["\']', txt)
            ret = m.group(1)
    print(ret)

