#!/usr/bin/python
# coding=UTF-8

# ------------------------------------------------------------------------------
#	
#	server.PY
#	
#	Copyright (C) 2012-2017 Aurelien Pages, apages2@free.fr
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
#	$Date: 2016-05-18 22:37:06 +0200$
#
# ------------------------------------------------------------------------------

__author__ = "Aurélien PAGES"
__copyright__ = "Copyright 2015-2017, Aurelien PAGES"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Aurélien PAGES"
__email__ = "apages2@free.fr"
__status__ = "Development-Beta-2"
__date__ = "$Date: 2016-05-18 22:37:06 +0200$"


# Default modules
import signal
import string
import sys
import os
import logging
import traceback
import xml.dom.minidom as minidom
from optparse import OptionParser
import inspect
import socket
import re

# MYHOMECMD modules

try:
	from lib.myhome_socket import *
except ImportError:
	print "Error: importing module from lib folder"
	sys.exit(1)
	
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
	
# 3rd party modules
# These might not be needed, depended on usage

# Serial
try:
	import serial
except ImportError:
	pass

	
# ----------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# VARIABLE CLASSS
# ------------------------------------------------------------------------------

class config_data:
	def __init__(
		self,
		serial_device = None,
		serial_rate = 115200,
		serial_timeout = 9,
		trigger = "",
		trigger_timeout = 10,
		loglevel = "info",
		logfile = "myhomecmd.log",
		program_path = "",
		sockethost = "",
		socketport = "",
		daemon_pidfile = "myhome.pid",
		log_msg = False,
		log_msgfile = "",
		):

		self.serial_device = serial_device
		self.serial_rate = serial_rate
		self.serial_timeout = serial_timeout
		self.trigger_timeout = trigger_timeout
		self.loglevel = loglevel
		self.logfile = logfile
		self.program_path = program_path
		self.sockethost = sockethost
		self.socketport = socketport
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
		
class serial_data:
	def __init__(
		self,
		port = None,
		rate = 115200,
		timeout = 9
		):

		self.port = port
		self.rate = rate
		self.timeout = timeout

class trigger_data:
	def __init__(
		self,
		data = ""
		):

		self.data = data
		
		
# ----------------------------------------------------------------------------
# DEAMONIZE
# Credit: George Henze
# ----------------------------------------------------------------------------

def shutdown():
	# clean up PID file after us
	logger.debug("Shutdown")

	if cmdarg.createpid:
		logger.debug("Removing PID file " + str(cmdarg.pidfile))
		os.remove(cmdarg.pidfile)

	if serial_param.port is not None:
		logger.debug("Close serial port")
		serial_param.port.close()
		serial_param.port = None

	logger.debug("Exit 0")
	sys.stdout.flush()
	os._exit(0)

def handler(signum=None, frame=None):
	if type(signum) != type(None):
		logger.debug("Signal %i caught, exiting..." % int(signum))
		shutdown()

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

	if cmdarg.createpid == True:
		pid = str(os.getpid())
		logger.debug("Writing PID " + pid + " to " + str(cmdarg.pidfile))
		file(cmdarg.pidfile, 'w').write("%s\n" % pid)

# ----------------------------------------------------------------------------
# C __LINE__ equivalent in Python by Elf Sternberg
# http://www.elfsternberg.com/2008/09/23/c-__line__-equivalent-in-python/
# ----------------------------------------------------------------------------

def _line():
	info = inspect.getframeinfo(inspect.currentframe().f_back)[0:3]
	return '[%s:%d]' % (info[2], info[1])

# ----------------------------------------------------------------------------

def read_myhome():
	"""
	Read message from USB/RF
	"""
	action = {'packettype' : "00", 'apikey' : str(config.apikey)}
	message = None
	byte = None
	buffer = None
	
	try:
		
		try:
			if serial_param.port.inWaiting() != 0:
				timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
				logger.debug("Timestamp: " + timestamp)
				logger.debug("SerWaiting: " + str(serial_param.port.inWaiting()))
				#logger.debug("Byte: " + str(byte))
				byte = serial_param.port.read()
				message = str(byte)
				#logger.debug("Byte: " + message)
		except IOError, err:
			print("Error: " + str(err))
			logger.error("Serial read error: %s, Line: %s" % (str(err),_line()))
		
		if message is not None:
			while re.search(r"(.*?##)(.*)$", message) is None:
				buffer = serial_param.port.read()
				message = message + str(buffer)
			#logger.debug("Message: " + str(message))
			#logger.debug("Send trame to Jeedom")
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
			return message
			
	except OSError, e:
		logger.error("Error in message: " + str(message) + " Line: " + _line())
		logger.error("Traceback: " + traceback.format_exc())
		print("------------------------------------------------")
		print("Received\t\t= " + message)
		traceback.format_exc()

# ----------------------------------------------------------------------------
	
def read_socket():
	"""
	Check socket for messages
	"""

	action = {'packettype' : "00", 'apikey' : str(config.apikey)}
	message = None
	byte = None
	buffer = None
	
	global messageQueue
	
	if not messageQueue.empty():
		logger.debug("Message received in socket messageQueue")
		message = stripped(messageQueue.get())
		
		if test_myhome( message ):
			# Flush buffer
			serial_param.port.flushOutput()
			logger.debug("SerialPort flush output")
			serial_param.port.flushInput()
			logger.debug("SerialPort flush input")

			timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
			
			if cmdarg.printout_complete == True:
				print "------------------------------------------------"
				print "Incoming message from socket"
				print "Send\t\t\t= " + message
				print "Date/Time\t\t= " + timestamp
				logger.debug("Write message to serial port")
				serial_param.port.write( message)
				logger.debug("Write message ok : "+ message)
            
			prm = message.replace('*', 'Y')
			prm = prm.replace('#', 'Z')
			action['trame'] = str(prm)
			command = Command(config.trigger_url,action)
			command.run(timeout=config.trigger_timeout)
			if config.log_msg == True:
				try:
					file = open(config.log_msgfile,"a+")
					file.write("---------------------------------\n")
					file.write(time.strftime("%Y-%m-%d %H:%M:%S")+' Received data from jeedom : => '+message+'\n')
					file.close()
				except Exception, e:
					logger.error("Error when trying to write message log")
					logger.error("Exception: %s" % str(e))
					pass
			
		else:
			logger.error("Invalid message from socket. Line: " + _line())
			if cmdarg.printout_complete == True:
				print "------------------------------------------------"
				print "Invalid message from socket"
	
# ----------------------------------------------------------------------------

def test_myhome( message ):
	"""
	Test, filter and verify that the incoming message is valid
	Return true if valid, False if not
	"""

	logger.debug("Test message: " + message)
		
	# Remove all invalid characters
	message = stripped(message)
	
	# Remove any whitespaces
	try:
		message = message.replace(' ', '')
	except Exception:
		logger.debug("Error: Removing white spaces")
		return False
	
	logger.debug("Message OK")

	return True

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
	Print MYHOMECMD version, build and date
	"""
	logger.debug("print_version")
 	print "MYHOMECMD Version: " + __version__
 	print __date__.replace('$', '')
 	logger.debug("Exit 0")
 	sys.exit(0)
	
# ----------------------------------------------------------------------------

def check_pythonversion():
	"""
	Check python version
	"""
	if sys.hexversion < 0x02060000:
		print "Error: Your Python need to be 2.6 or newer, please upgrade."
		sys.exit(1)

# ----------------------------------------------------------------------------

def option_listen():
	"""
	Listen to USB/CPL device and process data, exit with CTRL+C
	"""
	logger.debug("Start listening...")
	logger.debug("Open serial port")
	open_serialport()

	try:
		serversocket = myhomecmdSocketAdapter(config.sockethost,int(config.socketport))
	except Exception as err:
		logger.error("Error starting socket server. Line: " + _line())
		logger.error("Error: %s" % str(err))
		print "Error: can not start server socket, another instance already running?"
		exit(1)
	if serversocket.netAdapterRegistered:
		logger.debug("Socket interface started")
	else:
		logger.debug("Cannot start socket interface")

	try:
		while 1:
			# Let it breath
			# Without this sleep it will cause 100% CPU in windows
			time.sleep(0.05)
			#time.sleep(0.244)

			# Read serial port
			message = read_myhome()
			if message:
				logger.debug("Processed: " + message)
			
			# Read socket
			read_socket()
			
	except KeyboardInterrupt:
		logger.debug("Received keyboard interrupt")
		logger.debug("Close server socket")
		serversocket.netAdapter.shutdown()
		
		logger.debug("Close serial port")
		close_serialport()
		
		print("\nExit...")
		pass
		
# ----------------------------------------------------------------------------

def read_configfile():
	"""
	Read items from the configuration file
	"""
	if os.path.exists( cmdarg.configfile ):

		# ----------------------
		# Serial device
		config.serial_device = read_config( cmdarg.configfile, "serial_device")
		config.serial_rate = read_config( cmdarg.configfile, "serial_rate")
		config.serial_timeout = read_config( cmdarg.configfile, "serial_timeout")

		logger.debug("Serial device: " + str(config.serial_device))
		logger.debug("Serial rate: " + str(config.serial_rate))
		logger.debug("Serial timeout: " + str(config.serial_timeout))

		# ----------------------
		# TRIGGER
		config.trigger_url = read_config( cmdarg.configfile, "trigger_url")
		config.apikey = read_config( cmdarg.configfile, "apikey")
		config.trigger_timeout = read_config( cmdarg.configfile, "trigger_timeout")

		
		# ----------------------
		# SOCKET SERVER
		config.sockethost = read_config( cmdarg.configfile, "sockethost")
		config.socketport = read_config( cmdarg.configfile, "socketport")
		logger.debug("SocketHost: " + str(config.sockethost))
		logger.debug("SocketPort: " + str(config.socketport))

		# -----------------------
		# DAEMON
		config.daemon_pidfile = read_config( cmdarg.configfile, "daemon_pidfile")
		logger.debug("Daemon_pidfile: " + str(config.daemon_pidfile))

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
		logger.error("Error: Configuration file not found (" + cmdarg.configfile + ") Line: " + _line())

# ----------------------------------------------------------------------------

def open_serialport():
	"""
	Open serial port for communication to the USB/CPL device.
	"""

	# Check that serial module is loaded
	try:
		logger.debug("Serial extension version: " + serial.VERSION)
	except:
		print "Error: You need to install Serial extension for Python"
		logger.debug("Error: Serial extension for Python could not be loaded")
		logger.debug("Exit 1")
		sys.exit(1)

	# Check for serial device
	if config.device:
		logger.debug("Device: " + config.device)
	else:
		logger.error("Device name missing. Line: " + _line())
		print "Serial device is missing"
		logger.debug("Exit 1")
		sys.exit(1)

	# Open serial port
	logger.debug("Open Serialport")
	try:  
		serial_param.port = serial.Serial(config.device, config.serial_rate, timeout=serial_param.timeout)
	except serial.SerialException, e:
		logger.error("Error: Failed to connect on device " + config.device + " Line: " + _line())
		print "Error: Failed to connect on device " + config.device
		print "Error: " + str(e)
		logger.debug("Exit 1")
		sys.exit(1)

	if not serial_param.port.isOpen():
		serial_param.port.open()

# ----------------------------------------------------------------------------

def close_serialport():
	"""
	Close serial port.
	"""

	logger.debug("Close serial port")
	try:
		serial_param.port.close()
		logger.debug("Serial port closed")
	except:
		logger.error("Failed to close the serial port (" + device + ") Line: " + _line())
		print "Error: Failed to close the port " + device
		logger.debug("Exit 1")
		sys.exit(1)

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
		f = open( configFile ,'r')
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
				logfile = os.path.join(program_path, "myhomecmd.log")
			
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

	# Get directory of the myhomecmd script
	config.program_path = os.path.dirname(os.path.realpath(__file__))

	parser = OptionParser()
	parser.add_option("-d", "--device", action="store", type="string", dest="device", help="The serial device of the USB/RF, example /dev/ttyUSB0")
	parser.add_option("-l", "--listen", action="store_true", dest="listen", help="Listen for messages from USB/RF")
	parser.add_option("-s", "--sendmsg", action="store", type="string", dest="sendmsg", help="Send one message to USB/RF")
	parser.add_option("-f", "--myhomestatus", action="store_true", dest="myhomestatus", help="Get USB/RF device status")
	parser.add_option("-o", "--config", action="store", type="string", dest="config", help="Specify the configuration file")
	parser.add_option("-V", "--version", action="store_true", dest="version", help="Print myhomecmd version information")
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
	# LOGHANDLER
	if options.debug:
		logger = logger_init(cmdarg.configfile,'myhomecmd', True)
	else:
		logger = logger_init(cmdarg.configfile,'myhomecmd', False)
	
	logger.debug("Python version: %s.%s.%s" % sys.version_info[:3])
	logger.debug("MYHOMECMD Version: " + __version__)
	logger.debug(__date__.replace('$', ''))

	# ----------------------------------------------------------
	# PROCESS CONFIG.XML
	logger.debug("Configfile: " + cmdarg.configfile)
	logger.debug("Read configuration file")
	read_configfile()
	
	# ----------------------------------------------------------
	# SERIAL
	if options.device:
		config.device = options.device
	elif config.serial_device:
		config.device = config.serial_device
	else:
		config.device = None
	
	# ----------------------------------------------------------
	# DAEMON
	if options.listen:
		logger.debug("Daemon")
		logger.debug("Check PID file")
		
		if config.daemon_pidfile:
			cmdarg.pidfile = config.daemon_pidfile
			cmdarg.createpid = True
			logger.debug("PID file '" + cmdarg.pidfile + "'")
		
			if os.path.exists(cmdarg.pidfile):
				print("PID file '" + cmdarg.pidfile + "' already exists. Exiting.")
				logger.debug("PID file '" + cmdarg.pidfile + "' already exists.")
				logger.debug("Exit 1")
				sys.exit(1)
			else:
				logger.debug("PID file does not exists")

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
				logger.debug("Write PID file")
				file(cmdarg.pidfile, 'w').write("pid\n")
			except IOError, e:
				logger.error("Line: " + _line())
				logger.error("Unable to write PID file: %s [%d]" % (e.strerror, e.errno))
				raise SystemExit("Unable to write PID file: %s [%d]" % (e.strerror, e.errno))

			logger.debug("Start daemon")
			daemonize()

	# ----------------------------------------------------------
	# LISTEN
	if options.listen:
		option_listen()

	# ----------------------------------------------------------
	# SEND MESSAGE
	if options.sendmsg:
		cmdarg.rawcmd = options.sendmsg
		option_send()

	# ----------------------------------------------------------
	# GET MYHOME STATUS
	if options.myhomestatus:
		cmdarg.rawcmd = myhomecmd.status
		option_send()
	
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
	serial_param = serial_data()
	
	# Check python version
	check_pythonversion()
	
	main()

# ------------------------------------------------------------------------------
# END
# ------------------------------------------------------------------------------
