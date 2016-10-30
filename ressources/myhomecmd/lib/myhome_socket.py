#!/usr/bin/python
# -*- coding:utf-8 -*-

# ------------------------------------------------------------------------------
#	
#	MYHOME_SOCKET.PY
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

import time
import logging
import threading

from Queue import Queue
messageQueue = Queue()

import SocketServer
SocketServer.TCPServer.allow_reuse_address = True
from SocketServer import (TCPServer, StreamRequestHandler)


logger = logging.getLogger('myhomecmd')
	
# ------------------------------------------------------------------------------

class NetRequestHandler(StreamRequestHandler):
	
	def handle(self):
		logger.debug("Client connected to [%s:%d]" % self.client_address)
		lg = self.rfile.readline()
		messageQueue.put(lg)
		logger.debug("Message read from socket: " + lg.strip())
		
		self.netAdapterClientConnected = False
		logger.debug("Client disconnected from [%s:%d]" % self.client_address)
	
class myhomecmdSocketAdapter(object, StreamRequestHandler):
	def __init__(self, address='localhost', port=55004):
		self.Address = address
		self.Port = port

		self.netAdapter = TCPServer((self.Address, self.Port), NetRequestHandler)
		if self.netAdapter:
			self.netAdapterRegistered = True
			threading.Thread(target=self.loopNetServer, args=()).start()

	def loopNetServer(self):
		logger.debug("LoopNetServer Thread started")
		logger.debug("Listening on: [%s:%d]" % (self.Address, self.Port))
		self.netAdapter.serve_forever()
		logger.debug("LoopNetServer Thread stopped")

# ------------------------------------------------------------------------------
# END
# ------------------------------------------------------------------------------
