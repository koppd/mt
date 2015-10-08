# -*- coding: utf-8 -*-
"""
Created on Thu May 28 08:21:56 2015

@author: mininet
"""

#import time
#import os
#import signal
import argparse
#import sys
from socket import *
import re

def connect( host, port):
    """connect to the server
        params:
            host: the server host
            port: the server port (normally 110)
        returns: a socket that is connected to the server
    """
    clientSocket = socket(AF_INET, SOCK_STREAM)
    print "Create Connection... ", host, int(port)
    clientSocket.connect((host, int(port)))

    print "wait for welcome message..."
    toRecv = clientSocket.recv(1024)
    toRecv = toRecv.decode(encoding='UTF-8')
    print "received after connection established:", toRecv

    return clientSocket

def send_user( clientSocket, user):
    """ send the USER command """

    raw_input("Press Enter to send user. ")

    toSend = "USER " + user + "\r\n"
    print "sent:", toSend[:-1]
    clientSocket.send(toSend.encode('UTF-8'))

    toRecv = clientSocket.recv(1024)
    toRecv = toRecv.decode(encoding='UTF-8')
    print "received:", toRecv
    if toRecv == "+OK\r\n":
        return 0
    else:
        return 1

def send_pass( clientSocket, password):
    """ send the PASS command """

    raw_input("Press Enter to send password. ")

    toSend = "PASS " + password + "\r\n"
    print "sent:", toSend[:-1]
    clientSocket.send(toSend.encode('UTF-8'))

    toRecv = clientSocket.recv(1024)
    print "received:", toRecv
    toRecv = toRecv.decode(encoding='UTF-8')

def send_cwd( clientSocket, directory):
    """ send the CWD command """
    raw_input("Press Enter to change folder. ")

    toSend = "CWD " + directory + "\r\n"
    print "sent:", toSend[:-1]
    clientSocket.send(toSend.encode('UTF-8'))

    toRecv = clientSocket.recv(1024)
    print "received:", toRecv
    toRecv = toRecv.decode(encoding='UTF-8')

def send_syst(clientSocket):
    """ send the SYST command """
    # not used because it is not necessary

    toSend = "SYST" + "\r\n"
    print "sent:", toSend[:-1]
    clientSocket.send(toSend.encode('UTF-8'))

    toRecv = clientSocket.recv(1024)
    print "received:", toRecv
    toRecv = toRecv.decode(encoding='UTF-8')

def send_type(clientSocket):
    """ send the TYPE command """

    raw_input("Press Enter to switch to binary mode. ")

    toSend = "TYPE I" + "\r\n"
    print "sent:", toSend[:-1]
    clientSocket.send(toSend.encode('UTF-8'))

    toRecv = clientSocket.recv(1024)
    print "received:", toRecv
    toRecv = toRecv.decode(encoding='UTF-8')

def send_port( clientSocket, localip ):
    """ send the RETR command """

#    send_syst(clientSocket)   #not necessary
    send_type(clientSocket)

    dataSocket = socket(AF_INET, SOCK_STREAM)
    dataSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# localhost is not working. Error code 500, because 
# there is a NAT allegedly active.
    dataSocket.bind((localip, 0))
    dataSocket.listen(1)

    localIP = dataSocket.getsockname()[0]
    localport = dataSocket.getsockname()[1]
    print "Active mode needs a new TCP-connection:"
    print "Chosen local IP:", localIP
    print "Chosen local port:", localport

    localIPtext = re.sub('\.', ',', localIP)
    localPortHi = int(localport / 256)
    localPortLow = localport % 256
    localPortText = str(localPortHi) + ',' + str(localPortLow)

    print "\r"
    raw_input("Press Enter to send PORT command. ")

    toSend = "PORT " + localIPtext + ',' + localPortText + "\r\n"
    print "sent:", toSend[:-1]
    clientSocket.send(toSend.encode('UTF-8'))

    toRecv = clientSocket.recv(1024)
    print "received:", toRecv
    toRecv = toRecv.decode(encoding='UTF-8')

    return dataSocket


def send_retr( clientSocket, dataport, filename):
    """ send the RETR command """

    raw_input("Press Enter to start download. ")

    toSend = "RETR " + filename +"\r\n"
    print "sent:", toSend[:-1]
    clientSocket.send(toSend.encode('UTF-8'))

    toRecv = clientSocket.recv(1024)
    print "received:", toRecv
    toRecv = toRecv.decode(encoding='UTF-8')

# receive file
    (connectionSocket, connectionSocket_addr) = dataport.accept()
    receivedMessage = ''
#    connectionSocket.setblocking(0)   #non-blocking
    connectionSocket.settimeout(1000)
    notFinished = True
    while notFinished:
        try:
            buf = connectionSocket.recv(20000)
            if len(buf) > 0:
                receivedMessage += buf
                print "downloaded so far:", len(receivedMessage)
            else:
                notFinished = False
        except:
            notFinished = False
    print "download finished:", len(receivedMessage)

    toRecv = clientSocket.recv(1024)
    print "received:", toRecv
    toRecv = toRecv.decode(encoding='UTF-8')


def close_connection( clientSocket):
    """ close the connection """

    raw_input("Press Enter to close connection. ")

    toSend = "QUIT\r\n"
    print "sent:", toSend[:-1]
    clientSocket.send(toSend.encode('UTF-8'))

    toRecv = clientSocket.recv(1024)
    print "received:", toRecv
    clientSocket.close()


def startRealDownload(server, localip, port, user, password):

# create socket
    raw_input("Press Enter to connect to server. ")
    clientSocket = connect(server, port)

# connect to FTP server

# send user name
    send_user(clientSocket, user)

# send passwort
    send_pass(clientSocket, password)

# change directory
    send_cwd(clientSocket, "mininet")
    send_cwd(clientSocket, "demo")

# download file
    dataport = send_port(clientSocket, localip)
    send_retr(clientSocket, dataport, "ftp_downloadfile")

# quit and close connection
    close_connection(clientSocket)
    raw_input("Demo is over. Press Enter to close window. ")

    return 0

if __name__ == '__main__':
    #setLogLevel( 'info' )

    def type_port(x):
        x = int(x)
        if x < 1 or x > 65535:
            raise argparse.ArgumentTypeError(
                "Port number has to be greater than 1 and less than 65535.")
        return x

    description = ("Download a file from a specific folder from a FTP server")

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-s",
                        "--server",
                        help="The IP of the mail server. "
                             "(Default: '10.0.0.1')",
                        default="10.0.0.1")
    parser.add_argument("-lip",
                        "--localip",
                        help="The IP of the local host. "
                             "(Default: '192.168.56.4')", #stupid
                        default="192.168.56.4")
    parser.add_argument("-p",
                        "--port",
                        help="Port the FTP server is listening on. "
                             "(Default: 21)",
                        type=type_port,
                        default=21)
    parser.add_argument("-u",
                        "--user",
                        help="Username",
                        type=str,
                        required=True)
    parser.add_argument("-pw",
                        "--password",
                        help="Password",
                        type=str,
                        required=True)

    args = parser.parse_args()

    exit(startRealDownload(server=args.server,
                      localip=args.localip,
                      port=args.port,
                      user=args.user,
                      password=args.password))
