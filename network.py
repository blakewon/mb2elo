import sys
import socket
import string
import time
import ctypes
import threading
import config



#introducing multithreading because the server takes inputs in 0.5sec intervals, i want multiple inputs to be able to queue
#as to not timeout the socket

def init_connection(ip = config.ip, port = config.port): #initializes connection, redundant to insert into every function
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, 0))
    sock.settimeout(10)
    sock.connect((ip, port))
    return sock

    #these methods shouldn't be used as is, as the socket times out if two inputs are sent in less than 0.5 seconds, use threaded functions below these.

def _check_connection():                #checks if the server is responding to a command
    s = init_connection()
    print("sending heartbeat")
    s.send(b"\xff\xff\xff\xffrcon 1234")

    msg = s.recv(2048)
    if msg.startswith(b'\xff\xff\xff\xffprint'):
        print("connection successful")
        print(msg)
    else:
        print("connection unsuccessful")
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    time.sleep(0.5)
    
def _send_cmd(string):                  #string is a console command you want to execute
    if len(string) > 100:
        s.send("Error sending output. STR too large.")
        msg = s.recv(2048)
        return

    s = init_connection()
    print("sending cmd")
    string = string.encode()
    try:
        s.send(b"\xff\xff\xff\xffrcon detoxisanigger " + string)
    except:
        print("command not sent.")
 
    msg = s.recv(2048)
    if msg.startswith(b'\xff\xff\xff\xffprint'):
        print("command sent")
        print(msg)
    else:
        print("improper response")
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    time.sleep(1)

    #threading the function calls, couldn't figure out how to make it one function though

def check_connection():
    thread = threading.Thread(target=_check_connection)
    thread.start()
    thread.join()
def send_cmd(string):
    thread = threading.Thread(target=_send_cmd, args= (string,))
    thread.start()
    thread.join()

    












