usb-launcher
============

A quick cut at writing a Python script to control a [Storm OIC?] USB Missile Launcher. The intention is to create a platform suitable for running on a Raspberry Pi using XMPP to transmit commands (and maybe someday even video!)

### installation (assuming windows) ###

install python 2.6.6

install libusb-win32 filter driver (/bin/*arch*/install-filter-win.exe) onto launcher USB port

install pyusb-0.4.3.win32

copy libusb0_x86.dll and libusb.sys from libusb-win32.zip (/bin/x86/libusb0\*) into /*PythonInstallDir*/Lib/site-packages

rename /*PythonInstallDir*/Lib/site-packages/libusb0_x86.dll to /*PythonInstallDir*/Lib/site-packages/libusb0.dll

run script.py and hopefully the thing fires! or at least dumps out some useful debug info to the terminal...

### next steps ###

convince Paul to actually run the script on his laptop

add in libjingle + dbus stuff

get the script to work

raspberry pi!
