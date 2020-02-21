import sys
import socket
import string
import time
import ctypes
import network
import string
import os
import config


dirpath = os.getcwd().replace("\\","/")
print("current directory is : " + dirpath)

line = ""
def get_line1(f=open(config.logname), cache=['']):
    for cache[0] in f:
        pass
    return cache[0][:-1]







    
#various log formatting

def get_ip(str = ""):                               #gets ip from new connection line
    stripped = str.split("IP: ",1)[1]
    return stripped[0 : len(stripped)-1]

def connection_id(line = ""):
    return int(line.lstrip()[0 : 2])

def remove_colorcode(string=""):                   #removes quake3 color codes from strings
        for i in range(10):
                string = string.replace("^" + str(i), "")
        return string