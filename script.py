#!/usr/bin/python
#
# Based on Nathan Milford's stormLauncher
# https://github.com/nmilford/stormLauncher
# and information from
# http://dgwilson.wordpress.com/windows-missile-launcher/
# and code from
# www.thok.org/intranet/python/usb/README.html
#
# Copyright 2013 Daven Amin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# I'm trying to use the older version of PyUSB since we're not doing
# rocket science here, and I don't want too many headaches (wait a minute...)
import usb

class Controller:
    """A really really basic wrapper around a PyUSB device, I think"""

    VENDOR_ID = 0x2123
    PRODUCT_ID = 0x1010
    def __init__(self):
        busses = usb.busses()
        for bus in busses:
            devices = bus.devices
            for dev in devices:
                if dev.idVendor is VENDOR_ID and dev.idProduct is PRODUCT_ID:
                    self.__dev = dev
                    self.__conf = dev.configurations[0]
                    self.__intf = dev.interfaces[0][0]
                    self.__endp = self.__intf.endpoints[0]

        if self.__dev is None:
            raise ValueError('Launcher not found')

        try:
            self.__handle = self.__dev.open()
            self.__handle.detachKernelDriver(0)
            self.__handle.setConfiguration(self.__conf)
            self.__handle.claimInterface(self.__intf)
            self.__handle.setAltInterface(self.__intf)
            self.__handle.reset()
        except:
            raise ValueError('Unable to initialize Launcher!')

    # stolen from PyUSB 0.4 example code
    def debugUSB(self):
        """ a method to dump out USB information for any devices matching VENDOR_ID and PRODUCT_ID """
        busses = usb.busses()
        for bus in busses:
            devices = bus.devices
            for dev in devices:
                if dev.idVendor is VENDOR_ID and dev.idProduct is PRODUCT_ID:
                    print "Device:", dev.filename
                    print "  Device class:",dev.deviceClass
                    print "  Device sub class:",dev.deviceSubClass
                    print "  Device protocol:",dev.deviceProtocol
                    print "  Max packet size:",dev.maxPacketSize
                    print "  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor)
                    print "  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct)
                    print "  Device Version:",dev.deviceVersion
                    for config in dev.configurations:
                        print "  Configuration:", config.value
                        print "    Total length:", config.totalLength
                        print "    selfPowered:", config.selfPowered
                        print "    remoteWakeup:", config.remoteWakeup
                        print "    maxPower:", config.maxPower
                        for intf in config.interfaces:
                            print "    Interface:",intf[0].interfaceNumber
                            for alt in intf:
                                print "    Alternate Setting:",alt.alternateSetting
                                print "      Interface class:",alt.interfaceClass
                                print "      Interface sub class:",alt.interfaceSubClass
                                print "      Interface protocol:",alt.interfaceProtocol
                                for ep in alt.endpoints:
                                    print "      Endpoint:",hex(ep.address)
                                    print "        Type:",ep.type
                                    print "        Max packet size:",ep.maxPacketSize
                                    print "        Interval:",ep.interval

    # stolen wholesale from use_launcher_1.py
    def checkTurret(self):
        """ an unused method to maybe someday use limit info """
        return self.__handle.interruptRead(self.__endp.address,8)[:2]

    def turretCommand(self, bytec):
        """ send the lower six bits of integer "bytec" to the launcher """
        if not isinstance(bytec, int):
            raise TypeError('bytec must be an integer!')
        # truncate everything above "park" bit
        bytez = bytec & 0x3f

        # taken from use_launcher_1.py
        reqType = usb.TYPE_CLASS | usb.RECIP_INTERFACE | usb.ENDPOINT_OUT
        pad = [0] * 7
        self.__handle.controlMsg(reqType,usb.REQ_SET_CONFIGURATION,[bytez]+pad,value=usb.DT_CONFIG,index=0)

        # original control sending logic taken from Nathan's code
        #self.__dev.ctrl_transfer(
        #        0x21,0x09,0,0,
        #        [0x02,bytez,0x00,0x00,0x00,0x00,0x00,0x00])


    # description of control messages from wordpress site
    #// ==================================================
    #// Control of USB Rocket Launcher – DreamCheeky
    #// ==================================================
    #
    #// Control of the launcher works on a binary code
    #//
    #// |16 | 8 | 4 | 2 | 1 |
    #// | 0 | 0 | 0 | 0 | 1 | 1 – Up
    #// | 0 | 0 | 0 | 1 | 0 | 2 – Down
    #// | 0 | 0 | 0 | 1 | 1 | 3 – nothing
    #// | 0 | 0 | 1 | 0 | 0 | 4 – Left
    #// | 0 | 0 | 1 | 0 | 1 | 5 – Up / Left
    #// | 0 | 0 | 1 | 1 | 0 | 6 – Down / left
    #// | 0 | 0 | 1 | 1 | 1 | 7 – Slow left
    #// | 0 | 1 | 0 | 0 | 0 | 8 – Right
    #// | 0 | 1 | 0 | 0 | 1 | 9 – Up / Right
    #// | 0 | 1 | 0 | 1 | 0 | 10 – Down / Right
    #// | 0 | 1 | 0 | 1 | 1 | 11 – Slow Right
    #// | 0 | 1 | 1 | 0 | 0 | 12 – nothing
    #// | 0 | 1 | 1 | 0 | 1 | 13 – Slow Up
    #// | 0 | 1 | 1 | 1 | 0 | 14 – Slow Down
    #// | 0 | 1 | 1 | 1 | 1 | 15 – nothing
    #// | 1 | 0 | 0 | 0 | 0 | 16 – Fire
    #//
    #// | Fire |RT |LT |DN |UP |
    #//
    # Additionally, a value of 32 (0x20) is "Park"
    def composeByte(self,up,down,left,right,fire,stop):
        """ create an int value to represent launcher control logic """
        if stop is True:
            return 0x20
        if fire is True:
            return 0x10
        # otherwise, we're ready to make a nibble!
        retval = 0
        if up is True:
            retval |= 1 << 0
        if down is True:
            retval |= 1 << 1
        if left is True:
            retval |= 1 << 2
        if right is True:
            retval |= 1 << 3
        return retval



#################################################
# Let's see if we can get anything to go!
cntrl = Controller()
cntrl.debugUSB()
cntrl.turretCommand(0x10)
