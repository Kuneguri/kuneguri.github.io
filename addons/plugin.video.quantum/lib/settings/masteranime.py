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
# Settings
mediaTable       = 'animes'
_rootURL    = 'https://masteranime.es'
_genreURL   = _rootURL + '/genre/{genre}'
_searchURL  = _rootURL + '/api/anime/search?search={query}'
_animeURL   = _rootURL + '/anime/info/{animeId}'
_episodeURL  = _rootURL + '/anime/watch/{animeId}/{episodeId}'
_videoServers = [ 'ptserver', 'fserver', 'oserver' ]
_videoAuthURL = _rootURL + '/ajax/anime/load_episodes_v2?s={server}'
_trendingURL = _rootURL + '/api/anime/trending'
_releasesURL = _rootURL + '/api/releases'

_genreList = [ 'slice-of-life', 'comedy', 'school', 'seinen',
            'romance', 'action', 'ecchi', 'drama',
            'mystery', 'police', 'sports', 'adventure',
            'shounen', 'demons', 'fantasy', 'sci-fi',
            'mecha', 'magic', 'harem', 'supernatural',
            'historical', 'ova', 'space', 'special',
            'super-power', 'horror', 'psychological', 'kids',
            'shoujo', 'shoujo-ai', 'dub', 'game',
            'thriller', 'military', 'music', 'parody',
            'martial-arts' ]
_genreList= sorted(_genreList)

# Globals
providerId = __name__.replace('lib.settings.', '')
#logger = core.log.getLogger(__name__)
#db = cache.QCache(providerId)

# Database setup (alternative place???)
mainDbData = [  ('mediaId', 'TEXT NOT NULL PRIMARY KEY'),
                ('thumb', 'TEXT'),
                ('icon', 'TEXT'),
                ('fanart', 'TEXT'),
                ('plot', 'TEXT'),
                ('genre', 'TEXT'),
                ('year', 'INTEGER'),
                ('rating', 'REAL'),
                ('playcount', 'INTEGER'),
                ('title', 'TEXT'),
                ('status', 'TEXT'),
                ('aired', 'TEXT'),
                ('votes', 'TEXT'),
                ('episodes', 'TEXT'),
                ('trailer', 'TEXT')
            ]
