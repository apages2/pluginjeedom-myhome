#!/usr/bin/python
# coding: utf-8

import socket

hote = "192.168.10.44"
port = 20000

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((hote, port))
print "Connection on {}".format(port)

socket.send(u"Hey my name is Olivier!")

#print "Close"
#socket.close()
