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
import requests
import lib.core.quantum as core

userAgent = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36' }

logger = core.log.getLogger(__name__)

def get(url, timeout=5, headers=userAgent):
    logger.debug('--- Network GET request: {0}'.format(url))
    try:
        resp = requests.get(url, timeout=timeout, headers=headers)
    except Exception as ex:
        msg = 'Network error accessing: {0} \n {1}'.format(url, ex)
        logger.error(msg)
        core.popupError('Network error...', msg)
        return None
    return resp

class QuantumSession(object):
    def __init__(self, headers=None, timeout=10, verify=False, proxies=None):
        self._session = requests.Session()
        self._session.verify = verify
        self._timeout = timeout
        self._cookieJar = None
        self._proxies = None
        if proxies:
            self._proxies = proxies
        self._session.headers.update( userAgent )
        if headers:
            self._session.headers.update(headers)

    def GET(self, url, timeout=None):
        logger.debug('--- Network session GET request: {0}'.format(url))
        if not timeout:
            timeout = self._timeout
        try:
            return self._session.get(url, timeout=timeout, proxies=self._proxies)
        except Exception as ex:
            msg = 'Network error accessing: {0} \n {1}'.format(url, ex)
            logger.error(msg)
            core.popupError('Network error...', msg)
            return None

    def POST(self, url, data, timeout=None):
        logger.debug('--- Network session POST request: {0} - PostData: {1}'.format(url, data))
        if not timeout:
            timeout = self._timeout
        try:
            return self._session.post(url, data, timeout=timeout, proxies=self._proxies)
        except Exception as ex:
            msg = 'Network error accessing: {0} \n {1}'.format(url, ex)
            logger.error(msg)
            core.popupError('Network error...', msg)
            return None

    def HEAD(self, url, timeout=None):
        logger.debug('--- Network session HEAD request: {0}'.format(url))
        if not timeout:
            timeout = self._timeout
        try:
            return self._session.head(url, timeout=timeout, proxies=self._proxies)
        except Exception as ex:
            msg = 'Network error accessing: {0} \n {1}'.format(url, ex)
            logger.error(msg)
            core.popupError('Network error...', msg)
            return None

    def setHeaders(self, headers):
        self._session.headers.update(headers)

    def close(self):
        self._session.close()


