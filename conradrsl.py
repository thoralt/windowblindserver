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

# Timing:  "0" bit                          "1" bit                      pause after last bit
# SPI data: 0xFF  0x00  0x00                0xFF  0xFF  0x00             0x00 * 9
#           _____              __ ...       ____________       __ ... __                      ____
#          |     |            |            |            |     |         |                    |
# ... _____|     |____________|   ... _____|            |_____|         |_________ .... _____|
#          .     .            .            .            .     .         .                    .
#          .     .            .            .            .     .         .                    .
# ms:      |<0.6>|<---1.2---->|            |<---1.2---->|<0.6>|         |<--------5.4------->|
# Ticks:   |<-1->|<----2----->|            |<----2----->|<-1->|         |<---------9-------->|
# ms:      |<-------1.8------>|            |<-------1.8------>|
# Ticks:   |<--------3------->|            |<--------3------->|
#
# 1 Tick = 600 us (8 SPI bits) -> 75 µs per bit, SPI clock = 13333 Hz
# empirically tested SPI clock of 13075 Hz matches remote control output better
import wiringpi2 as wiringpi
import sys


# =============================================================================================================
# =============================================================================================================
class ConradRSL:

    # ---------------------------------------------------------------------------------------------------------
    # class variables
    # ---------------------------------------------------------------------------------------------------------
    SPI_CHANNEL = 1  # we don't need CS, define it anyway
    SPI_SPEED = 13075
    ZERO = '\xFF\x00\x00'
    ONE = '\xFF\xFF\x00'
    counterValues = [ZERO+ZERO, ONE+ZERO, ZERO+ONE, ONE+ONE]
    codes = {
        "1.1-up": '0011101000011010010101000000000',
        "1.1-dn": '0000011000011010010101000000000',
        "1.2-up": '1001101000011010010101000000000',
        "1.2-dn": '1011101000011010010101000000000',
        "1.3-up": '0101101000011010010101000000000',
        "1.3-dn": '0111101000011010010101000000000',
        "1.4-up": '1101101000011010010101000000000',
        "1.4-dn": '1111101000011010010101000000000',
        "2.1-up": '0001011000011010010101000000000',
        "2.1-dn": '0011011000011010010101000000000',
        "2.2-up": '1010011000011010010101000000000',
        "2.2-dn": '1001011000011010010101000000000',
        "2.3-up": '0110011000011010010101000000000',
        "2.3-dn": '0101011000011010010101000000000',
        "2.4-up": '1110011000011010010101000000000',
        "2.4-dn": '1101011000011010010101000000000',
        "3.1-up": '0010001000011010010101000000000',
        "3.1-dn": '0001001000011010010101000000000',
        "3.2-up": '1000001000011010010101000000000',
        "3.2-dn": '1010001000011010010101000000000',
        "3.3-up": '0100001000011010010101000000000',
        "3.3-dn": '0110001000011010010101000000000',
        "3.4-up": '1100001000011010010101000000000',
        "3.4-dn": '1110001000011010010101000000000',
        "4.1-up": '0000101000011010010101000000000',
        "4.1-dn": '0010101000011010010101000000000',
        "4.2-up": '1011001000011010010101000000000',
        "4.2-dn": '1000101000011010010101000000000',
        "4.3-up": '0111001000011010010101000000000',
        "4.3-dn": '0100101000011010010101000000000'
        "4.4-up": '1111001000011010010101000000000',
        "4.4-dn": '1100101000011010010101000000000'
    }

    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    def __init__(self):
        self.counter = 0
        self.devices = []
        wiringpi.wiringPiSetup()
        wiringpi.wiringPiSPISetup(self.SPI_CHANNEL, self.SPI_SPEED)

    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    def add_device(self, device):
        device.commandManager = self
        self.devices.append(device)

    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    def send_code(self, bits):

        # increment message counter
        self.counter += 1

        print 'Sending code ' + bits + ':',
        sys.stdout.flush()

        # repeat 5 times
        buf = ''
        for x in range(0, 5):
            # first two bits: message counter
            buf += self.counterValues[self.counter & 3]
            # add data bits
            for bit in bits:
                if bit == '0':
                    buf += self.ZERO
                else:
                    buf += self.ONE

            # add padding for pause between packets
            buf += '\x00\x00\x00\x00\x00\x00\x00\x00\x00'

        # send the packet
        wiringpi.wiringPiSPIDataRW(self.SPI_CHANNEL, buf)
#        print 'OK - WARNING: DEBUG MODE, DID NOT ACTUALLY TRANSMIT DATA'
        print 'OK'

    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    def move_to_position(self, address, target_position):
        # look up device address
        device = None
        for d in self.devices:
            if d.address == address:
                device = d

        # device not in list?
        if device is None:
            print 'Conrad_RSL.moveToPosition(\'%s\', %.1f): Device not found.' % \
                (address, target_position)
            return False

        # notify device class instance to move to target position
        print 'Conrad_RSL.moveToPosition(\'%s\', %.1f): Found device \'%s\'' % \
            (address, target_position, device.name)
        return device.move_to_position(target_position)

    # ---------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------
    def send_cmd(self, cmd):
        if cmd in self.codes:
            self.send_code(self.codes[cmd])
            return True
        else:
            return False
