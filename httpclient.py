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
import subprocess

import shlex

def call_wget(server, filename):
#    call(["wget", "-O", "-", "%s/%s" % (server, filename), "|", "md5sum"])
    args = shlex.split("wget -O tmp_file %s/%s" % (server, filename))
    wget = subprocess.call(args)
    md5sum = subprocess.call(shlex.split("md5sum tmp_file"))

    subprocess.call(shlex.split("rm tmp_file"))


def startRealDownload(server, filename):

    if 1==2:
#        CLI(self.net)
        pass
    else:
        print "After every download, md5sum will calculate the md5 hash."
        print "This will show you the correctness of the file transfer even if the link quality is bad."
        print ""
        raw_input("Press Enter to download file %s from server %s. " % (filename, server))

        redownload = True
        while redownload == True:
            call_wget(server, filename)
            again = raw_input("Download complete. Download again? (y/N) ")
            if not(again == "y" or again == "Y"):
                redownload = False

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

    description = ("Download a file from a HTTP server")

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-s",
                        "--server",
                        help="The IP of the http server. "
                             "(Default: '10.0.0.1')",
                        default="10.0.0.1")
    parser.add_argument("-f",
                        "--file",
                        help="file name",
                        type=str,
                        required=True)

    args = parser.parse_args()

    exit(startRealDownload(server=args.server,
                      filename=args.file))
