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
        self.queue = []

    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    def move_to_position(self, targetPosition):

        # if currently moving, add next target position to queue, will be processed when current movement ends
        if self.isMoving:
            print 'Shutter.moveToPosition(): Currently moving, adding new targetPosition to queue.'
            self.queue.append(targetPosition)
            return

        # check if we need to move at all
        if self.position == targetPosition:
            print 'Shutter.moveToPosition(): Current position = target position -> no action'
            return True

        self.isMoving = True
        self.targetPosition = targetPosition

        # calculate direction and moving time
        if self.targetPosition >= 100:
            # always move full time up to sync position
            t = self.closingTime
            self.direction = 'up'
            print 'moveToPosition(): Target position = 100 -> performing full up cycle'
        elif self.targetPosition <=0:
            # always move full time down to sync position
            t = self.closingTime
            self.direction = 'dn'
            print 'moveToPosition(): Target position = 0 -> performing full down cycle'
        else:
            if self.targetPosition > self.position:
                self.direction = 'up'
                t = (self.targetPosition - self.position)/100 * self.closingTime
            else:
                self.direction = 'dn'
                t = (self.position - self.targetPosition)/100 * self.closingTime

        print 'moveToPosition(): Current position=%.1f, target position=%.1f, direction=\'%s\', time=%.1f' \
            % (self.position, self.targetPosition, self.direction, t)

        self.delayed_stop(t)
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
            d = self.device

            # actuator is moving, now wait until we reach target position
            print 'delayedExecutionThread.run() start, waiting %f s...' % self.delay
            time.sleep(self.delay)
            d.position = d.targetPosition
            print '%s reached position %d' % (d.address, d.targetPosition)

            # queue contains commands?
            while len(d.queue) > 0:
                # get next target position
                d.targetPosition = d.queue.pop(0)
                print '%s next position in queue: %d, items left: %d' % (d.address, d.targetPosition, len(d.queue))

                # depending on new target position either continue to move or
                # change direction
                if d.direction == 'up' and d.targetPosition > d.position:
                    # can continue to move up
                    t = (d.targetPosition - d.position)/100 * d.closingTime
                    print '%s can continue to move up, waiting %.1f seconds' % (d.address, t)
                    time.sleep(t)
                    d.position = d.targetPosition
                    print '%s reached position %d' % (d.address, d.targetPosition)
                elif d.direction == 'dn' and d.targetPosition < d.position:
                    # can continue to move down
                    t = (d.position - d.targetPosition)/100 * d.closingTime
                    print '%s can continue to move down, waiting %.1f seconds' % (d.address, t)
                    time.sleep(t)
                    d.position = d.targetPosition
                    print '%s reached position %d' % (d.address, d.targetPosition)
                else:
                    # direction changed for next queue element
                    print '%s needs to change direction, stopping and starting.' % d.address
                    if d.direction == 'up':
                        cmd = d.address + '-dn'
                        d.direction = 'dn'
                        t = (d.position - d.targetPosition)/100 * d.closingTime
                    else:
                        cmd = d.address + '-up'
                        d.direction = 'up'
                        t = (d.targetPosition - d.position)/100 * d.closingTime

                    # first command to stop
                    d.commandManager.send_cmd(cmd)
                    # same command to start again in opposite direction
                    d.commandManager.send_cmd(cmd)

                    print '%s changed direction, waiting %.1f seconds' % (d.address, t)
                    time.sleep(t)
                    d.position = d.targetPosition
                    print '%s reached position %d' % (d.address, d.targetPosition)

            # queue is now empty -> issue stop command
            if d.direction == 'up':
                cmd = d.address + '-dn'
            else:
                cmd = d.address + '-up'
            d.commandManager.send_cmd(cmd)
            d.isMoving = False

        except Exception as e:
            print 'Exception during delayedExecutionThread'
            traceback.print_exc()
