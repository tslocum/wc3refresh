import sys
import array
import time
import struct
import socket

# Warcraft III Auto-refreshing script
#
# Created by Trevor "tj9991" Slocum
# tj9991.com - tslocum@gmail.com
# 
# A large portion of the code in this project
# was copied from Mercury, and my thanks go
# out to them for their work.
# http://git.burgestrand.se/mercury/

name        = "AutoRefresh" # name to display when refreshing
refreshrate = 15            # seconds between refreshes

name = "|r" + name
joinPacket = array.array('B')

joinPacket.extend((0xF7, 0x1E)) # packet type
joinPacket.extend((0x26, 0x00)) # packet length 
joinPacket.extend((0x0, 0x0, 0x0, 0x0)) # host count
joinPacket.extend((0x0, 0x0, 0x0, 0x0, 0x0)) # tick count
joinPacket.extend((0xE4, 0x17)) # external port
joinPacket.extend((0x0, 0x0, 0x0, 0x0)) # join/create counter
joinPacket.extend((0x0,)) # name
joinPacket.extend((0x1, 0x0)) # name terminate + ipv4 tag
joinPacket.extend((0x2, 0x0)) # sockaddr start
joinPacket.extend((0x17, 0xE0)) # internal port ()
joinPacket.extend((0x7F, 0x0, 0x0, 0x1)) # internal IP (127.0.0.1)
joinPacket.extend((0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0)) # filling zeroes

placeholder = joinPacket[19:19+joinPacket[19:].index(0x0)].tostring()

after = joinPacket[20+len(placeholder):]
rebuild = joinPacket[0:19]
rebuild[2:4] = array.array('B', struct.pack('<H', 38 + len(name)))
rebuild.extend(array.array('B', name + '\0'))
rebuild.extend(joinPacket[20+len(placeholder):])
joinPacket = rebuild

sockets = {}

while 1:
  time.sleep(refreshrate)
  refreshing = True
  
  for i in range(12):
    while refreshing:
      try:
        sockets[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockets[i].settimeout(1)
        sockets[i].connect(("127.0.0.1", 6112))
        sockets[i].send(joinPacket.tostring())
      except socket.error, msg:
        print "Unable to connect to Warcraft III:", msg
        sys.exit(1)
      
      response = array.array('B', sockets[i].recv(32))
      if response[0:4] == array.array('B', (0xF7, 0x05, 0x08, 0x00)):
        if response[4] is 0x07:
          count = struct.unpack('<L', joinPacket[4:8])[0]
          joinPacket[4:8] = array.array('B', struct.pack('<L', (count + 1) % 256))
          print "Incrementing host count from ", count, "to " + str(count + 1) + "."
        elif response[4] is 0x09:
          refreshing = False
          break
        elif response[4] is 0x0A:
          print "Game has started."
          refreshing = False
          break
        elif response[4] is 0x1B:
          refreshing = False
          break
      if response[0:2] == array.array('B', (0xF7, 0x04)):
        time.sleep(.25)
        break

  time.sleep(.25)

  for i in range(12):
    try:
      sockets[i].close()
    except:
      pass
