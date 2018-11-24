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
import logging

class Logger(object):
    def __init__(self, logPath):
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s#%(funcName)s():\n    %(message)s', filename=logPath)
        self._logPath = logPath

    def getLogPath(self):
        return self._logPath

    def getLogger(self, name, logLevel=logging.DEBUG):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        return logger

