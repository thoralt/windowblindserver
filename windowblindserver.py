#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import atexit
import threading
import sys
import traceback
from conrad_rsl import Conrad_RSL
from shutter import Shutter

#==============================================================================================================
#==============================================================================================================
class ConnectionThread(threading.Thread):
    def __init__(self, connection, shutterManager):
        self.connection = connection
        self.shutterManager = shutterManager
        threading.Thread.__init__(self)

    def run(self):
        try:
            buf = self.connection.recv(64)
            if len(buf) > 0:
                print 'ConnectionThread(): Received \'%s\'' % buf
                cmd = buf.split(':')
                if cmd[0] == 'direct-cmd':
                    if self.shutterManager.sendCmd(cmd[1]):
                        self.connection.send(buf + ': Okay.')
                    else:
                        self.connection.send(buf + ': Unknown command.')
                elif cmd[0] == 'goto-position':
                    if self.shutterManager.moveToPosition(cmd[1], float(cmd[2])):
                        self.connection.send(buf + ': Okay.')
                    else:
                        self.connection.send(buf + ': Error.')
        except Exception as e:
            print 'Exception during receive'
            traceback.print_exc()
        finally:
            self.connection.close()

#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
def close_socket():
    print 'Closing socket.'
    serversocket.shutdown(1)
    serversocket.close()

#==============================================================================================================
# MAIN
#==============================================================================================================

# one global object for SPI command management
shutterManager = Conrad_RSL()

# add devices to manager
shutterManager.addDevice(Shutter('1.1', 'Bad', 16))
shutterManager.addDevice(Shutter('1.2', 'Arbeitszimmer', 16))
shutterManager.addDevice(Shutter('1.3', 'Wohnzimmer 3', 16))
shutterManager.addDevice(Shutter('2.1', 'Wohnzimmer 2', 16))
shutterManager.addDevice(Shutter('2.2', 'Wohnzimmer 1', 16))
shutterManager.addDevice(Shutter('2.3', 'Vorsaal', 16))
shutterManager.addDevice(Shutter('3.1', 'Küche 1', 16))
shutterManager.addDevice(Shutter('3.2', 'Küche 2', 16))
shutterManager.addDevice(Shutter('3.3', 'Küche 3', 16))
shutterManager.addDevice(Shutter('4.1', 'Küche 4', 16))
#shutterManager.addDevice(Shutter('4.2', '', 16))
#shutterManager.addDevice(Shutter('4.3', '', 16))

SERVER_IP = '192.168.178.219'
SERVER_PORT = 8089

atexit.register(close_socket)
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind((SERVER_IP, SERVER_PORT))
serversocket.listen(5) # become a server socket, maximum 5 connections


print 'Waiting for incoming connections...'

while True:
    connection, address = serversocket.accept()
    t = ConnectionThread(connection, shutterManager)
    t.start()
