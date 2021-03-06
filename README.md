# windowblindserver

## A python server for Raspberry Pi to control window blinds equipped with Conrad RSL actuators

Conrad sells a few remote controls, switches and dimmers for their RSL home automation system. They use 433 MHz signals with a simple protocol which has been implemented in this server to control the window blinds of my house. 

I reverse engineered the protocol using a scope attached to the remote control, pushing buttons and comparing the signals. Although the protocol has been described here and there on the web, I was not able to get it working using only online ressources, that's why I did it from scratch. The protocol is quite easy to implement, it consist of pulses with variable length:

```
           _____              __ ...       ____________       __ ... __                      ____
          |     |            |            |            |     |         |                    |
 ... _____|     |____________|   ... _____|            |_____|         |_________ .... _____|
          .     .            .            .            .     .         .                    .
          .     .            .            .            .     .         .                    .
 ms:      |<0.6>|<---1.2---->|            |<---1.2---->|<0.6>|         |<--------5.4------->|
 ms:      |<-------1.8------>|            |<-------1.8------>|

               "Zero-bit"                    "One-bit"                "pause between packets"
```

I defined short pulses followed by a long pause as binary "0" and long pulses followed by a short pause as binary "1". My remote control transmits 33 bits of data, followed by a 5.4 ms long pause. Data packets are repeated minimum five times, and if you get the timing right, the actuators start clicking :)

My remote is able to switch 12 window blinds up and down (I have seen remotes with 16 channels). The channel and up/down information is somehow encoded into the bits, I didn't bother to work that out and simply copied the bit streams into the source code. They have the following structure:
```
Channel Direction Code
------- --------- ------------------------------------
1.1     up        xx 00 1110 1000011010010101000000000
1.1     down      xx 00 0001 1000011010010101000000000
1.2     up        xx 10 0110 1000011010010101000000000
1.2     down      xx 10 1110 1000011010010101000000000
1.3     up        xx 01 0110 1000011010010101000000000
1.3     down      xx 11 1110 1000011010010101000000000
1.4     up        xx 11 0110 1000011010010101000000000
1.4     down      xx 01 1110 1000011010010101000000000
2.1     up        xx 00 0101 1000011010010101000000000
2.1     down      xx 00 1101 1000011010010101000000000
2.2     up        xx 10 1001 1000011010010101000000000
2.2     down      xx 10 0101 1000011010010101000000000
2.3     up        xx 01 1001 1000011010010101000000000
2.3     down      xx 01 0101 1000011010010101000000000
2.4     up        xx 11 1001 1000011010010101000000000
2.4     down      xx 11 0101 1000011010010101000000000
3.1     up        xx 00 1000 1000011010010101000000000
3.1     down      xx 00 0100 1000011010010101000000000
3.2     up        xx 10 0000 1000011010010101000000000
3.2     down      xx 10 1000 1000011010010101000000000
3.3     up        xx 01 0000 1000011010010101000000000
3.3     down      xx 01 1000 1000011010010101000000000
3.4     up        xx 11 0000 1000011010010101000000000
3.4     down      xx 11 1000 1000011010010101000000000
4.1     up        xx 00 0010 1000011010010101000000000
4.1     down      xx 00 1010 1000011010010101000000000
4.2     up        xx 10 1100 1000011010010101000000000
4.2     down      xx 10 0010 1000011010010101000000000
4.3     up        xx 01 1100 1000011010010101000000000
4.3     down      xx 01 0010 1000011010010101000000000
4.4     up        xx 11 1100 1000011010010101000000000
4.4     down      xx 11 0010 1000011010010101000000000
````

The first two bits act as a 2 bit message counter (LSB first) to distinguish between repeated packets and individual button presses. Bits 2 and 3 carry the button number inside a group (LSB first) Bits 4...7 seem to represent the channels and up/down states although it is not clear to me how this is encoded. There is no alternating bit or bit sequence for up/down in this list, maybe somebody else can figure this out. The last long group of bits is likely to be the ID of my remote since it is constant througout all codes.

To get a consistent timing on the Raspberry Pi, I used the SPI port. This ensures the bits aren't disturbed by task switching activities and frees a bit of CPU time. I use only the MOSI pin since this protocol is asynchronous. Since the SPI can't handle speeds as low as 1667 Hz needed by this protocol (minimum pulse length = 0.6 ms), I grouped pulses into whole bytes which lets us use 13.3 kHz as SPI frequency. To transmit a binary "0", we therefore need to put ```0xFF 0x00 0x00``` into our buffer (```0xFF 0xFF 0x00``` for a binary "1"). The whole bitstream is assembled before transmitting it using WiringPi's SPI functions.

<i>Copyright (C) 2015 Thoralt Franz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.</i>
