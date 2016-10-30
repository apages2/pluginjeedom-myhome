#!/usr/bin/python
# coding=UTF-8

# ------------------------------------------------------------------------------
#	
#	MYHOME_COMMAND.PY
#	
#	Copyright (C) 2012-2014 Aurelien Pages, apages2@free.fr
#	
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#	$Date: 2015-01-25 18:19:06 +0200 $
#
# ------------------------------------------------------------------------------

import requests
import logging
import subprocess
import threading

logger = logging.getLogger('myhomecmd')

class Command(object):
	def __init__(self, url,data):
		self.url = url
		self.data = data
		self.process = None
	
	def run(self, timeout):
		def target():
			logger.debug("Send data to jeedom : "+self.url+' => '+str(self.data))
			requests.get(self.url, params=self.data,timeout= float(timeout))
				
		thread = threading.Thread(target=target)
		thread.start()

# ----------------------------------------------------------------------------
