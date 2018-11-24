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
# Quantum
import lib.core.quantum as core
import lib.providers.providers as providers

# Logger
logger = core.log.getLogger(__name__)

def main(params):
    # Search needs to be the first to execute before the delegate
    if params.get('action') == 'search':
        searchAllProviders(params)

    elif params.get('provider'):
        delegateProvider(params)
    else:
        core.addSearch(params)
        core.addSeparator()
        mainMenu(params)

def delegateProvider(params):
    provider = params.get('provider')
    action = params.get('action')

    if provider in providers.providersControllers.keys():
        providers.providersControllers[provider](params)
    elif action == 'search':
        searchAllProviders(params)
    else:
        msg = 'Invalid provider: {0} - {1}'.format(provider, params)
        logger.warn(msg)
        raise ValueError(msg)

def mainMenu(params):
    localParams = dict(params)
    for provider in providers.providersControllers.keys():
        listItem = core.listItem(label=provider.capitalize())
        localParams.update({ 'provider': provider })
        url = core.getURL(localParams)
        core.addDirectoryItem(core.handle, url, listItem, True)

def searchAllProviders(params):
    query = params.get('query')
    if not query:
        core.searchHistory(params)
    else:
        if query == core.NEWSEARCH:
            dialog = core.dialog
            query = core.dialog.input('Search: ', type=core.INPUT_ALPHANUM)
            del dialog
            if len(query) < 3:
                msg = 'Search parameter is too small. Use at least 3 characters'
                dialog = core.dialog.ok('Search error', msg)
                del dialog
                return

        core.addSearchHistory(params.get('media'), query)
        result = list()
        p = params.get('provider')
        if p == 'allproviders':
            for provider in providers.providersSearch.keys():
                ret = providers.providersSearch[provider](query)
                result.append( { 'provider': provider, 'searchResults': ret } )
        else:
            result.append( { 'provider': p, 'searchResults': providers.providersSearch[p](query) } )
        showSearchResults(result)

def showSearchResults(results):
    matches = 0
    for i in results:
        provider = i.get('provider')
        resultList = core.sortDictList( i.get('searchResults'), 'title' )
        if not resultList:
            logger.warn('Empty search results for: {0}'.format(provider))
            break
        matches = len(resultList)
        item = core.listItem(label='[B][COLOR springgreen] --- {0}: Found {1} matches[/B][/COLOR]'.format(provider.capitalize(), matches))
        core.addDirectoryItem(core.handle, None, item, False)
        for m in resultList:
            params = { 'mediaId': m.get('mediaId'), 'provider': provider, 'media': m.get('media') }
            m.update( { 'mediatype': 'video' } )
            url = core.getURL(params)
            listItem = core.listItem(label=m.get('title').encode('utf8'))
            m.pop('aired')
            if not m.get('year'):
                m.pop('year')
            listItem.setInfo('video', m)
            listItem.setArt(m)
            core.addDirectoryItem(core.handle, url, listItem, True)


