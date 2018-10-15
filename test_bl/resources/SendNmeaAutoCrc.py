from __future__ import print_function

try:
    input = raw_input
except NameError:
    pass

import sys
import socket
import argparse

from time import sleep
from ctypes import c_ushort


def create_parser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default = '10.10.77.157')
    parser.add_argument('-p', '--port', default = '53111')
    parser.add_argument('-f', '--file', default = 'nmea_msgs.txt')
    parser.add_argument('-l', '--loop', default = "0",
                        help = '\"once\" if no loop, time in seconds after sending all lines otherwise')
    parser.add_argument('-d', '--delay', default = "1",
                        help = '\"kbd\" if wait for <Enter>, time in seconds after sending one line otherwise')
    
    return parser


def crc_nmea (nmea_str):
    """ crc calculation nmea standard """
    crc = 0x00
    
    for byte in nmea_str.strip()[1:]:
        crc ^= ord(byte)
    
    return '{0:02x}'.format(c_ushort(crc).value)


def main (udp_ip, udp_port, file_name, loop_time, sleep_time):
    print("udp_ip =", udp_ip)
    print("udp_port =", udp_port)
    print("delay between messages (-1 for keyboard) =", sleep_time)
    print("delay after loop (-1 if once) =", loop_time)
    print("---------------------------------------------------------")
    
    udp_msgs = []
    
    with open(file_name, 'r') as fin:
        for line in fin:
            msg = line[:line.find('#')].strip()
            
            if not msg:
                continue
            
            udp_msgs.append("".join([msg, '*', crc_nmea(msg), '\r\n']))
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while 1:
        for udp_msg in udp_msgs:
            print(udp_msg)
            sock.sendto(str.encode(udp_msg), (udp_ip, udp_port))
            
            if sleep_time >= 0:
                sleep(sleep_time)
            else:
                print('Press <Enter> to continue')
                input()
        
        if loop_time >= 0:
            print("--- end of loop ---\n")
            sleep(loop_time)
        else:
            break


if __name__ == "__main__":
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    
    sleep_time = 1
    if namespace.delay == 'kbd':
        sleep_time = -1
    else:
        sleep_time = int(namespace.delay)
    
    loop_time = 1
    if namespace.loop == 'once':
        loop_time = -1
    else:
        loop_time = int(namespace.loop)
    
    main(namespace.address, int(namespace.port), namespace.file, loop_time, sleep_time)
