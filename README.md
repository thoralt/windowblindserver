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

I defined short pulses followed by a long pause as binary "0" and long pulses followed by a short pause as binary "1". My remote control uses 33 bits of data, followed by a 5.4 ms long pause. Data packets are repeated minimum five times, and if you get the timing right, the actuators start clicking :)

My remote is able to switch 12 window blinds up and down (I have seen remotes with 16 channels). The channel and up/down information is somehow encoded into the bits, I didn't bother to work that out and simply copied the bit streams into the source code. They have the following structure:
```
Channel Direction Code
------- --------- -----------------------------------
1.1     up        xx 001110 1000011010010101000000000
1.1     down      xx 000001 1000011010010101000000000
1.2     up        xx 100110 1000011010010101000000000
1.2     down      xx 101110 1000011010010101000000000
1.3     up        xx 010110 1000011010010101000000000
1.3     down      xx 011110 1000011010010101000000000
2.1     up        xx 000101 1000011010010101000000000
2.1     down      xx 001101 1000011010010101000000000
2.2     up        xx 101001 1000011010010101000000000
2.2     down      xx 100101 1000011010010101000000000
2.3     up        xx 011001 1000011010010101000000000
2.3     down      xx 010101 1000011010010101000000000
3.1     up        xx 001000 1000011010010101000000000
3.1     down      xx 000100 1000011010010101000000000
3.2     up        xx 100000 1000011010010101000000000
3.2     down      xx 101000 1000011010010101000000000
3.3     up        xx 010000 1000011010010101000000000
3.3     down      xx 011000 1000011010010101000000000
4.1     up        xx 000010 1000011010010101000000000
4.1     down      xx 001010 1000011010010101000000000
4.2     up        xx 101100 1000011010010101000000000
4.2     down      xx 100010 1000011010010101000000000
4.3     up        xx 011100 1000011010010101000000000
4.3     down      xx 010010 1000011010010101000000000
````

The first two bits act as a message counter to distinguish between repeated packets and individual button presses, they change with each button press like 00, 10, 01 and 11. Bits 2...7 seem to represent the channels and up/down states, although it is not clear to me, how this is encoded. There is no alternating bit or bit sequence for up/down in this list, maybe somebody else can figure this out. The last long group of bits is likely to be the ID of my remote since it is constant througout all codes.

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
