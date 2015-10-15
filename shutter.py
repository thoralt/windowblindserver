# -*- coding: utf-8 -*-

import threading
import time
import traceback

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


# =============================================================================================================
# =============================================================================================================
class Shutter:

    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    def __init__(self, address, name, closingTime):
        self.address = address
        self.name = name
        self.closingTime = closingTime
        self.isMoving = False
        self.position = 100
        self.targetPosition = 100
        self.direction = None
        self.commandManager = None

    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    def move_to_position(self, targetPosition):

        # check if we need to move at all
        if self.position == targetPosition:
            print 'Shutter.moveToPosition(): Current position = target position -> no action'
            return True

        self.isMoving = True
        self.targetPosition = targetPosition

        # calculate direction and moving time
        if self.targetPosition >= 100:
            # always move full time up to sync position
            movingtime = self.closingTime
            self.direction = 'up'
            print 'moveToPosition(): Target position = 100 -> performing full up cycle'
        elif self.targetPosition <=0:
            # always move full time down to sync position
            movingtime = self.closingTime
            self.direction = 'dn'
            print 'moveToPosition(): Target position = 0 -> performing full down cycle'
        else:
            if self.targetPosition > self.position:
                self.direction = 'up'
                movingtime = (self.targetPosition - self.position)/100 * self.closingTime
            else:
                self.direction = 'dn'
                movingtime = (self.position - self.targetPosition)/100 * self.closingTime

        print 'moveToPosition(): Current position=%.1f, target position=%.1f, direction=\'%s\', time=%.1f' \
            % (self.position, self.targetPosition, self.direction, movingtime)

        self.delayed_stop(movingtime)
        return self.commandManager.send_cmd(self.address + '-' + self.direction)

    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    def delayed_stop(self, delay):
        t = DelayedStopThread(self, delay)
        t.start()


# =============================================================================================================
# =============================================================================================================
class DelayedStopThread(threading.Thread):
    def __init__(self, device, delay):
        print 'delayedExecutionThread.init(%s:\'%s\', %f)' % (device.address, device.name, delay)
        self.device = device
        self.delay = delay
        threading.Thread.__init__(self)

    def run(self):
        try:
            print 'delayedExecutionThread.run() start, waiting %f s...' % self.delay
            time.sleep(self.delay)
            print 'delayedExecutionThread.run() finished waiting'
            if self.device.direction == 'up':
                cmd = self.device.address + '-dn'
            else:
                cmd = self.device.address + '-up'
            self.device.commandManager.send_cmd(cmd)
            self.device.position = self.device.targetPosition
            self.device.isMoving = False
        except Exception as e:
            print 'Exception during delayedExecutionThread'
            traceback.print_exc()
