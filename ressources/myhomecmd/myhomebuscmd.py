#!/usr/bin/python
# coding=UTF-8

# ------------------------------------------------------------------------------
#	
#	myhomebuscmd.PY
#	
#	Copyright (C) 2016-2018 Aurelien Pages, apages2@free.fr
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
#	$Date: 2017-02-02 20:33:10 +0200$
#
# ------------------------------------------------------------------------------

__author__ = "Aurélien PAGES"
__copyright__ = "Copyright 2016-2018, Aurelien PAGES"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Aurélien PAGES"
__email__ = "apages2@free.fr"
__status__ = "Development-Beta-1"
__date__ = "$Date: 2017-02-02 20:33:10 +0200$"

# Default modules
import signal
import string
import sys
import os
import logging
import traceback
import xml.dom.minidom as minidom
from optparse import OptionParser
import socket
import select
import re
import time
import Queue

# MYHOMEBUSCMD modules

try:
	from lib.myhome_utils import *
except ImportError:
	print "Error: module lib/myhome_utils not found"
	sys.exit(1)
	
try:
	from lib.myhome_command import *
except ImportError:
	print "Error: module lib/myhome_command not found"
	sys.exit(1)	
	
	
# ----------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# VARIABLE CLASSS
# ------------------------------------------------------------------------------

	
class config_data:
	def __init__(
		self,
		trigger = "",
		trigger_timeout = 10,
		loglevel = "info",
		logfile = "myhomebuscmd.log",
		program_path = "",
		f454host = "",
		f454port = "",
		daemon_pidfile = "myhomebus.pid",
		log_msg = False,
		log_msgfile = "",
		):

		self.trigger_timeout = trigger_timeout
		self.loglevel = loglevel
		self.logfile = logfile
		self.program_path = program_path
		self.f454host = f454host
		self.f454port = f454port
		self.daemon_pidfile = daemon_pidfile
		self.log_msg = log_msg
		self.log_msgfile = log_msgfile
		self.trigger = trigger
		self.trigger_timeout = trigger_timeout
		
class cmdarg_data:
	def __init__(
		self,
		configfile = "",
		action = "",
		rawcmd = "",
		device = "",
		createpid = False,
		pidfile = "",
		printout_complete = True,
		):

		self.configfile = configfile
		self.action = action
		self.rawcmd = rawcmd
		self.device = device
		self.createpid = createpid
		self.pidfile = pidfile
		self.printout_complete = printout_complete
		
class trigger_data:
	def __init__(
		self,
		data = ""
		):

		self.data = data
		
def shutdown():
	# clean up PID file after us
	logger.debug("Shutdown")

	if cmdarg.createpid_event:
		logger.debug("Removing PID Event file " + str(cmdarg.pidfile_event))
		os.remove(cmdarg.pidfile_event)
	
	if cmdarg.createpid_command:
		logger.debug("Removing PID Command file " + str(cmdarg.pidfile_command))
		os.remove(cmdarg.pidfile_command)

	logger.debug("Exit 0")
	sys.stdout.flush()
	os._exit(0)

# ----------------------------------------------------------------------------

def handler(signum=None, frame=None):
	if type(signum) != type(None):
		logger.debug("Signal %i caught, exiting..." % int(signum))
		shutdown()

# ----------------------------------------------------------------------------
		
def daemonize():

	try:
		pid = os.fork()
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("1st fork failed: %s [%d]" % (e.strerror, e.errno))

	os.setsid() 

	prev = os.umask(0)
	os.umask(prev and int('077', 8))

	try:
		pid = os.fork() 
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("2nd fork failed: %s [%d]" % (e.strerror, e.errno))

	dev_null = file('/dev/null', 'r')
	os.dup2(dev_null.fileno(), sys.stdin.fileno())

	if cmdarg.createpid_event == True:
		pid = str(os.getpid())
		logger.debug("Writing PID " + pid + " to " + str(cmdarg.pidfile_event))
		file(cmdarg.pidfile_event, 'w').write("%s\n" % pid)

	if cmdarg.createpid_command== True:
		pid = str(os.getpid())
		logger.debug("Writing PID " + pid + " to " + str(cmdarg.pidfile_command))
		file(cmdarg.pidfile_command, 'w').write("%s\n" % pid)

# ----------------------------------------------------------------------------

def read_config( configFile, configItem):
	"""
	Read item from the configuration file
	"""
	logger.debug('Open configuration file')
	logger.debug('File: ' + configFile)
	
	xmlData = ""
	if os.path.exists( configFile ):

		#open the xml file for reading:
		f = open( configFile,'r')
		data = f.read()
		f.close()
	
		# xml parse file data
 		logger.debug('Parse config XML data')
		try:
			dom = minidom.parseString(data)
		except:
			print "Error: problem in the config.xml file, cannot process it"
			logger.debug('Error in config.xml file')
			
		# Get config item
	 	logger.debug('Get the configuration item: ' + configItem)
		
		try:
			xmlTag = dom.getElementsByTagName( configItem )[0].toxml()
			logger.debug('Found: ' + xmlTag)
			xmlData = xmlTag.replace('<' + configItem + '>','').replace('</' + configItem + '>','')
			logger.debug('--> ' + xmlData)
		except:
			logger.debug('The item tag not found in the config file')
			
			
 		logger.debug('Return')
 		
 	else:
 		logger.error("Error: Config file does not exists. Line: " + _line())
 		
	return xmlData

# ----------------------------------------------------------------------------

def print_version():
	"""
	Print MYHOMEBUSCMD version, build and date
	"""
	logger.debug("print_version")
 	print "MYHOMEBUSCMD Version: " + __version__
 	print __date__.replace('$', '')
 	logger.debug("Exit 0")
 	sys.exit(0)
	
# ----------------------------------------------------------------------------

def event(address, port=20000):
	"""
	Listen Event from Legrand F454
	"""
	action = {'packettype' : "00", 'apikey' : str(config.apikey)}
	message = None
	message = b""
	logger.debug("Start Connect Event...")
	eventsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	eventsocket.connect((address, port))
	eventsocket.send(b"*99*1##") 
	
	while 1:
		message = message+eventsocket.recv(1024)
		trame = re.search(b"(.*?##.*$)", message)
		if trame:
			prm = message.replace('*', 'Y')
			prm = prm.replace('#', 'Z')
			action['trame'] = str(prm)
			command = Command(config.trigger_url,action)
			command.run(timeout=config.trigger_timeout)
			if config.log_msg == True:
				try:
					file = open(config.log_msgfile,"a+")
					file.write("---------------------------------\n")
					file.write(time.strftime("%Y-%m-%d %H:%M:%S")+' Send data to jeedom : => '+message+'\n')
					file.close()
				except Exception, e:
					logger.error("Error when trying to write message log")
					logger.error("Exception: %s" % str(e))
					pass
			message = None
			message = b""

# ----------------------------------------------------------------------------

def sendcommand(address, trame, port=20000):
	"""
	Send Command to Legrand F454
	"""
	action = {'packettype' : "00", 'apikey' : str(config.apikey)}
	logger.debug("Start Send Command...")
	commandsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	commandsocket.settimeout(10)
	
	try:
		commandsocket.connect((address, port))
		commandsocket.send(b"*99*9##") 
		logger.debug("Send *99*9##")
		message = commandsocket.recv(1024)
		logger.debug(message)
		check = re.search(b"\*#\*1##", message)
		if check:
			logger.debug("Send "+trame)
			commandsocket.send(trame.encode())
			message2 = commandsocket.recv(1024)
			logger.debug(message2)
			commandsocket.close()
			exit(1)
		else:
			commandsocket.close()
			exit(1)
	
	except socket.timeout as error:
		commandsocket.close()
		exit(1)

# ----------------------------------------------------------------------------

def read_configfile():
	"""
	Read items from the configuration file
	"""
	if os.path.exists( cmdarg.configfile ):

		# ----------------------
		# TRIGGER
		config.trigger_url = read_config( cmdarg.configfile, "trigger_url")
		config.apikey = read_config( cmdarg.configfile, "apikey")
		config.trigger_timeout = read_config( cmdarg.configfile, "trigger_timeout")

		# ----------------------
		# SOCKET SERVER EXTERNE
		config.f454host = read_config( cmdarg.configfile, "f454host")
		config.f454port = read_config( cmdarg.configfile, "f454port")
		logger.debug("F454Host: " + str(config.f454host))
		logger.debug("F454Port: " + str(config.f454port))

		# -----------------------
		# DAEMON
		config.daemon_pidfile_event = read_config( cmdarg.configfile, "daemon_pidfile_event")
		logger.debug("Daemon_pidfile_event: " + str(config.daemon_pidfile_event))
		config.daemon_pidfile_command = read_config( cmdarg.configfile, "daemon_pidfile_command")
		logger.debug("Daemon_pidfile_command: " + str(config.daemon_pidfile_command))
		# ------------------------
		# LOG MESSAGES
		if (read_config(cmdarg.configfile, "log_msg") == "yes"):
			config.log_msg = True
		else:
			config.log_msg = False
		config.log_msgfile = read_config(cmdarg.configfile, "log_msgfile")
		
	else:
		# config file not found, set default values
		print "Error: Configuration file not found (" + cmdarg.configfile + ")"
		logger.error("Error: Configuration file not found (" + cmdarg.configfile + ")")

# ----------------------------------------------------------------------------

def logger_init(configFile, name, debug):
	"""

	Init loghandler and logging
	
	Input: 
	
		- configfile = location of the config.xml
		- name	= name
		- debug = True will send log to stdout, False to file
		
	Output:
	
		- Returns logger handler
	
	"""
	program_path = os.path.dirname(os.path.realpath(__file__))
	dom = None
	
	if os.path.exists( configFile ):

		# Read config file
		f = open( configFile,'r')
		data = f.read()
		f.close()

		try:
			dom = minidom.parseString(data)
		except Exception, e:
			print "Error: problem in the config.xml file, cannot process it"
			print "Exception: %s" % str(e)
			
		if dom:
		
			# Get loglevel from config file
			try:
				xmlTag = dom.getElementsByTagName( 'loglevel' )[0].toxml()
				loglevel = xmlTag.replace('<loglevel>','').replace('</loglevel>','')
			except:
				loglevel = "INFO"

			# Get logfile from config file
			try:
				xmlTag = dom.getElementsByTagName( 'logfile' )[0].toxml()
				logfile = xmlTag.replace('<logfile>','').replace('</logfile>','')
			except:
				logfile = os.path.join(program_path, "myhomebuscmd.log")
			
			loglevel = loglevel.upper()
			
			#formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
			formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s')
			
			if debug:
				loglevel = "DEBUG"
				handler = logging.StreamHandler()
			else:
				handler = logging.FileHandler(logfile)
							
			handler.setFormatter(formatter)
			
			logger = logging.getLogger(name)
			logger.setLevel(logging.getLevelName(loglevel))
			logger.addHandler(handler)
			
			return logger

# ----------------------------------------------------------------------------
		
def main():

	global logger

	# Get directory of the myhomebuscmd script
	config.program_path = os.path.dirname(os.path.realpath(__file__))

	parser = OptionParser()
	parser.add_option("-l", "--listen", action="store_true", dest="listen", help="Daemon for listen event")
	parser.add_option("-c", "--command", action="store_true", dest="command", help="Send a Command")
	parser.add_option("-j", "--jeedom", action="store_true", dest="jeedom", help="Daemon for jeedom")
	parser.add_option("-t", "--trame", action="store", type="string", dest="trame", help="Trame to send")
	parser.add_option("-o", "--config", action="store", type="string", dest="config", help="Specify the configuration file")
	parser.add_option("-V", "--version", action="store_true", dest="version", help="Print myhomebuscmd version information")
	parser.add_option("-D", "--debug", action="store_true", dest="debug", default=False, help="Debug printout on stdout")
	(options, args) = parser.parse_args()

	# ----------------------------------------------------------
	# VERSION PRINT
	if options.version:
		print_version()

	# ----------------------------------------------------------
	# CONFIG FILE
	if options.config:
		cmdarg.configfile = options.config
	else:
		cmdarg.configfile = os.path.join(config.program_path, "config.xml")
		
	# ----------------------------------------------------------
	# TRAME
	if options.trame:
		cmdarg.trame= options.trame
	else:
		cmdarg.trame = "*#1*##"

	# ----------------------------------------------------------
	# LOGHANDLER
	if options.debug:
		logger = logger_init(cmdarg.configfile,'myhomebuscmd', True)
	else:
		logger = logger_init(cmdarg.configfile,'myhomebuscmd', False)
	
	logger.debug("Python version: %s.%s.%s" % sys.version_info[:3])
	logger.debug("MYHOMEBUSCMD Version: " + __version__)
	logger.debug(__date__.replace('$', ''))

	# ----------------------------------------------------------
	# PROCESS CONFIG.XML
	logger.debug("Configfile: " + cmdarg.configfile)
	logger.debug("Read configuration file")
	read_configfile()
	
	# ----------------------------------------------------------
	# DAEMON
	if options.listen:
		logger.debug("Daemon Event")
		logger.debug("Check PID file for Event")
		
		if config.daemon_pidfile_event:
			cmdarg.pidfile_event = config.daemon_pidfile_event
			cmdarg.createpid_event = True
			cmdarg.createpid_command = False
			logger.debug("PID Event file '" + cmdarg.pidfile_event + "'")
		
			if os.path.exists(cmdarg.pidfile_event):
				print("PID Event file '" + cmdarg.pidfile_event + "' already exists. Exiting.")
				logger.debug("PID Event file '" + cmdarg.pidfile_event + "' already exists.")
				logger.debug("Exit 1")
				sys.exit(1)
			else:
				logger.debug("PID Event file does not exists")

		else:
			print("You need to set the --pidfile parameter at the startup")
			logger.error("Command argument --pidfile missing. Line: " + _line())
			logger.debug("Exit 1")
			sys.exit(1)

		logger.debug("Check platform")
		if sys.platform == 'win32':
			print "Daemonize not supported under Windows. Exiting."
			logger.error("Daemonize not supported under Windows. Line: " + _line())
			logger.debug("Exit 1")
			sys.exit(1)
		else:
			logger.debug("Platform: " + sys.platform)
			
			try:
				logger.debug("Write PID Event file")
				file(cmdarg.pidfile_event, 'w').write("pid\n")
			except IOError, e:
				logger.error("Line: " + _line())
				logger.error("Unable to write PID Event file: %s [%d]" % (e.strerror, e.errno))
				raise SystemExit("Unable to write PID Event file: %s [%d]" % (e.strerror, e.errno))

			logger.debug("Start daemon Event")
			daemonize()
			
	if options.jeedom:
		logger.debug("Daemon Command")
		logger.debug("Check PID file for Command")
		
		if config.daemon_pidfile_command:
			cmdarg.pidfile_command = config.daemon_pidfile_command
			cmdarg.createpid_command = True
			cmdarg.createpid_event = False
			logger.debug("PID Command file '" + cmdarg.pidfile_command + "'")
		
			if os.path.exists(cmdarg.pidfile_command):
				print("PID Command file '" + cmdarg.pidfile_command + "' already exists. Exiting.")
				logger.debug("PID Command file '" + cmdarg.pidfile_command + "' already exists.")
				logger.debug("Exit 1")
				sys.exit(1)
			else:
				logger.debug("PID Command file does not exists")

		else:
			print("You need to set the --pidfile parameter at the startup")
			logger.error("Command argument --pidfile missing. Line: " + _line())
			logger.debug("Exit 1")
			sys.exit(1)

		logger.debug("Check platform")
		if sys.platform == 'win32':
			print "Daemonize not supported under Windows. Exiting."
			logger.error("Daemonize not supported under Windows. Line: " + _line())
			logger.debug("Exit 1")
			sys.exit(1)
		else:
			logger.debug("Platform: " + sys.platform)
			
			try:
				logger.debug("Write PID Command file")
				file(cmdarg.pidfile_command, 'w').write("pid\n")
			except IOError, e:
				logger.error("Line: " + _line())
				logger.error("Unable to write PID Command file: %s [%d]" % (e.strerror, e.errno))
				raise SystemExit("Unable to write PID Command file: %s [%d]" % (e.strerror, e.errno))

			logger.debug("Start daemon Command")
			daemonize()


	# ----------------------------------------------------------
	# LISTEN
	if options.listen:
		event(config.f454host,int(config.f454port))
	
	# ----------------------------------------------------------
	# COMMAND
	if options.command:
		sendcommand(config.f454host,cmdarg.trame,int(config.f454port))
		
	logger.debug("Exit 0")
	sys.exit(0)
	
# ------------------------------------------------------------------------------


if __name__ == '__main__':

	# Init shutdown handler
	signal.signal(signal.SIGINT, handler)
	signal.signal(signal.SIGTERM, handler)

	# Init objects
	config = config_data()
	cmdarg = cmdarg_data()

	main()

# ------------------------------------------------------------------------------
# END
# ------------------------------------------------------------------------------

