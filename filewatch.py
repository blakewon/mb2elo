import sys
import socket
import string
import time
import ctypes
import network
import string
import os
import config


mypath1 = 'D:/Program Files (x86)/Steam/steamapps/common/Jedi Academy/GameData/MBII/'

dirpath = os.getcwd().replace("\\","/")
print("current directory is : " + dirpath)

line = ""
def get_line1(f=open(config.logname), cache=['']):
    for cache[0] in f:
        pass
    return cache[0][:-1]




def get_line():
    last_line = ""
    with open(mypath1 + "log.log", "r") as f:
        for line in f:
            pass
        last_line = line[:-1]
        return last_line




    
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