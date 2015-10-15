#!/usr/bin/python
# -*- coding: utf-8 -*-

# windowblindserver
# A python server for Raspberry Pi to control window blinds equipped with Conrad RSL actuators
# Copyright (C) 2015 Thoralt Franz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
import atexit
import threading
import traceback
from conradrsl import ConradRSL
from shutter import Shutter


# =============================================================================================================
# =============================================================================================================
class ConnectionThread(threading.Thread):
    def __init__(self, connection, shutter_manager):
        self.connection = connection
        self.shutterManager = shutter_manager
        threading.Thread.__init__(self)

    def run(self):
        try:
            buf = self.connection.recv(64)
            if len(buf) > 0:
                print 'ConnectionThread(): Received \'%s\'' % buf
                cmd = buf.split(':')
                if cmd[0] == 'direct-cmd':
                    if self.shutterManager.send_cmd(cmd[1]):
                        self.connection.send(buf + ': Okay.')
                    else:
                        self.connection.send(buf + ': Unknown command.')
                elif cmd[0] == 'goto-position':
                    if self.shutterManager.move_to_position(cmd[1], float(cmd[2])):
                        self.connection.send(buf + ': Okay.')
                    else:
                        self.connection.send(buf + ': Error.')
        except Exception as e:
            print 'Exception during receive'
            traceback.print_exc()
        finally:
            self.connection.close()


# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
def close_socket():
    print 'Closing socket.'
    server_socket.shutdown(1)
    server_socket.close()

# =============================================================================================================
# MAIN
# =============================================================================================================

# one global object for SPI command management
shutterManager = ConradRSL()

# add devices to manager
shutterManager.add_device(Shutter('1.1', 'Bad', 16))
shutterManager.add_device(Shutter('1.2', 'Arbeitszimmer', 16))
shutterManager.add_device(Shutter('1.3', 'Wohnzimmer 3', 16))
shutterManager.add_device(Shutter('2.1', 'Wohnzimmer 2', 16))
shutterManager.add_device(Shutter('2.2', 'Wohnzimmer 1', 16))
shutterManager.add_device(Shutter('2.3', 'Vorsaal', 16))
shutterManager.add_device(Shutter('3.1', 'Küche 1', 16))
shutterManager.add_device(Shutter('3.2', 'Küche 2', 16))
shutterManager.add_device(Shutter('3.3', 'Küche 3', 16))
shutterManager.add_device(Shutter('4.1', 'Küche 4', 16))
# shutterManager.addDevice(Shutter('4.2', '', 16))
# shutterManager.addDevice(Shutter('4.3', '', 16))

SERVER_IP = '192.168.178.219'
SERVER_PORT = 8089

atexit.register(close_socket)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(5)  # become a server socket, maximum 5 connections


print 'Waiting for incoming connections...'

while True:
    connection, address = server_socket.accept()
    t = ConnectionThread(connection, shutterManager)
    t.start()
