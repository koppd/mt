# -*- coding: utf-8 -*-
"""
Created on Thu May 28 08:21:56 2015

@author: mininet
"""

import time
import os
import signal
import argparse
import sys
from socket import *

def connect( host, port):
    """connect to the server
        params:
            host: the server host
            port: the server port (normally 110)
        returns: a socket that is connected to the server
    """
    clientSocket = socket(AF_INET, SOCK_STREAM)
    print "Verbdungsaufbau... ", host, int(port)
    clientSocket.connect((host, int(port)))
    # FIXME hier das OK pruefen
    
    print "warte auf Begruessungsnachricht..."
    toRecv = clientSocket.recv(1024)
    toRecv = toRecv.decode(encoding='UTF-8')
    print "empfangen nach connect:", toRecv
    
    return clientSocket

def send_user( clientSocket, user):
    """ send the USER command """

    toSend = "USER " + user + "\r\n"
    clientSocket.send(toSend.encode('UTF-8'))

    toRecv = clientSocket.recv(1024)
    toRecv = toRecv.decode(encoding='UTF-8')
    print "empfangen nach USER:", toRecv
    # FIXME hier das OK pruefen
    if toRecv == "+OK\r\n":
        return 0
    else:
        return 1

def send_pass( clientSocket, password):
    """ send the PASS command """
    
    toSend = "PASS " + password + "\r\n"
    clientSocket.send(toSend.encode('UTF-8'))

    toRecv = clientSocket.recv(1024)
    # FIXME hier das OK pruefen
    print "empfangen nach PASS:", toRecv
    toRecv = toRecv.decode(encoding='UTF-8')
    
    return 0


def send_cwd( clientSocket, directory):
    """ send the CWD command """
    
    toSend = "CWD " + directory + "\r\n"
    clientSocket.send(toSend.encode('UTF-8'))

    toRecv = clientSocket.recv(1024)
    # FIXME hier das OK pruefen
    print "empfangen nach CWD:", toRecv
    toRecv = toRecv.decode(encoding='UTF-8')
    
    return 0


def send_retr( clientSocket, filename):
    """ send the RETR command """
    pass


def close_connection( clientSocket):
    """ close the connection """

    clientSocket.send(b"QUIT\r\n")
    toRecv = clientSocket.recv(1024)
    # FIXME hier das OK pruefen
    print "empfangen nach QUIT:", toRecv 
    clientSocket.close()


def startRealDownload(server, port, user, password):    
#        display, tunnel = tunnelX11( self.h2, None )
##        self.p1 = self.h2.popen( ['xterm', '-title', 'BlaBla', '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
#        self.p1 = self.h2.popen( ['xterm', '-title', 'Download_in_progress...', '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

 
    if 1==2:
#        CLI(self.net)
        pass
    else:
# Erzeuge Socket
        print "create socket..."
        clientSocket = connect(server, port)

# Verbinde mit FTP-Server

# sende Username
        send_user(clientSocket, user)

# sende Passwort
        send_pass(clientSocket, password)

# wechsle Verzeichnis
        send_cwd(clientSocket, "mininet")
        send_cwd(clientSocket, "demo")

# Download Datei
#           send_retr(clientSocket, "ftp_downloadfile")


# Verabschieden und beende Verbindung
        close_connection(clientSocket)
   

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
                      port=args.port,
                      user=args.user,
                      password=args.password))