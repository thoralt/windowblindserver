# -*- coding: utf-8 -*-

import sys, threading, time, traceback

#==============================================================================================================
#==============================================================================================================
class Shutter:
    def __init__(self, address, name, closingTime):
        self.address = address
        self.name = name
        self.closingTime = closingTime
        self.isMoving = False
        self.position = 100
        self.targetPosition = 100

    def moveToPosition(self, targetPosition):

        # check if we need to move at all
        if self.position == targetPosition:
            print 'Shutter.moveToPosition(): Current position = target position -> no action'
            return True

        self.isMoving = True
        self.targetPosition = targetPosition

        # calculate direction and moving time
        movingtime = 0
        direction = ''
        stopdirection = ''
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

        self.delayedStop(movingtime)
        return self.commandManager.sendCmd(self.address + '-' + self.direction)


    #----------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------
    def delayedStop(self, delay):
        t = delayedStopThread(self, delay)
        t.start()

#==============================================================================================================
#==============================================================================================================
class delayedStopThread(threading.Thread):
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
            self.device.commandManager.sendCmd(cmd)
            self.device.position = self.device.targetPosition
            self.device.isMoving = False
        except Exception as e:
            print 'Exception during delayedExecutionThread'
            traceback.print_exc()
