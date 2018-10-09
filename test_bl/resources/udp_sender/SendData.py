#!/usr/bin/python

# Version 1.0

# optional, for pyhton 2.x
from __future__ import print_function

try:
	input = raw_input
except NameError:
	pass
#

import sys
import socket
import argparse
import threading
import re

from time import sleep


def create_parser ():
	parser = argparse.ArgumentParser()
	parser.add_argument('-i' , '--input-file' , help = 'Input filename with NMEA messages.' , required = True)
	parser.add_argument('-a' , '--address' , help = 'IP address to send messages to.' , required = True)
	parser.add_argument('-p' , '--port' , help = 'UDP port to send messages to.' , required = True)
	parser.add_argument('-d' , '--delay' , help = 'Delay time between messages (in 0.01 seconds)' , default = '100')
	parser.add_argument('-f' , '--filter' , help = 'Allowed NMEA types (e.g. "TEGLL,INXDP")' , default = '')
	parser.add_argument('-l' , '--lines' , help = 'Number of lines sent before delay' , default = '1')
	parser.add_argument('-v' , '--verbose' , help = 'Print sending messages' , action = "store_true")
	parser.add_argument('-n' , '--no-loop' , help = 'Don\'t loop sending messages' , action = "store_true")
	return parser


pause_flag = False
quit_flag = False


def keyboard_input ():
	global pause_flag , quit_flag
	while not quit_flag:
		line = input().lower()
		if line == 'q':
			quit_flag = True
		elif line == 'p' and not pause_flag:
			pause_flag = True
		elif line == 'c' and pause_flag:
			pause_flag = False


def send_messages (udp_ip ,
				   udp_port ,
				   udp_msgs ,
				   lines = None ,
				   delay = None ,
				   verbose = None ,
				   no_loop = None):
	global pause_flag , quit_flag
	
	sock = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
	iterator = iter(udp_msgs)
	while 1:
		if quit_flag:
			print('Quit')
			return
		if pause_flag:
			print('Pause')
			while pause_flag and not quit_flag:
				sleep(0.5)
			if quit_flag:
				continue
			else:
				print('Continue')
		
		for n in range(0 , lines):
			try:
				msg = next(iterator)
			except StopIteration as e:
				if no_loop:
					quit_flag = True
					print('Done. Press any key.')
					return
				iterator = iter(udp_msgs)
				msg = next(iterator)
			
			if type(msg) is str:
				encoded = str.encode(msg)
				sock.sendto(encoded , (udp_ip , udp_port))
			else:
				sock.sendto(msg , (udp_ip , udp_port))
			if verbose:
				print(msg)
		
		if not verbose:
			print('.' , end = '')
			sys.stdout.flush()
		
		for i in range(delay):
			if quit_flag or pause_flag:
				break;
			sleep(0.01)


def filter_message (line , msg_filter):
	if len(msg_filter) == 0:
		return line
	for fl in msg_filter:
		if line.upper().startswith(fl + ","):
			return line
	return ""


def load_messages (filename , msg_filter):
	udp_msgs = []
	try:
		with open(filename , 'r') as fin:
			for line in fin:
				msg = (re.sub("^[0-2][0-9]:[0-5][0-9]:[0-5][0-9].[0-9]* " , "" , line)).strip().rstrip('\x00')
				if len(msg) == 0:
					continue
				if msg.startswith('$') or msg.startswith('!'):
					msg = filter_message(msg , msg_filter)
					if len(msg) == 0:
						continue
					udp_msgs.append(''.join([msg , '\r\n']))
				else:
					s = msg.replace(" " , "")
					b = [s[i:i + 2] for i in range(0 , len(s) , 2)]
					msg = bytearray([int(x , 16) for x in b])
					udp_msgs.append(msg)
	except (OSError , IOError) as e:
		print(str(e))
	return udp_msgs


if __name__ == '__main__':
	'''
	parser = create_parser()
	args = parser.parse_args(sys.argv[1:] if len(sys.argv) > 1 else ['-h'])

	msg_filter = list(map(lambda s: '$' + s.upper(), [] if len(args.filter) == 0 else args.filter.split(',')))


	print('Destination address:', args.address + ':' + args.port)
	print('Allowed messages:', 'all' if len(msg_filter) == 0 else msg_filter)
	print('Lines at once:', args.lines)
	print('Delay between messages (in 0.1 seconds):', args.delay)
	print('Input file:', args.input_file)
	print('Loop sending:', not args.no_loop)
	#path_to_file = args.input_file
	'''
	
	path_to_file = "C:\\Users\\vialuk\\python_vdi\\vdm.txt"
	msg_filter = ""
	
	udp_msgs = load_messages(path_to_file , msg_filter)
	if len(udp_msgs) == 0:
		print("  nothing to send")
		exit(0)
	else:
		print("  " + str(len(udp_msgs)) + " allowed line(s)")
	
	print('------------------------------------------------------------------')
	print('Press \'q\'+<Enter> to quit, \'p\'+<Enter> to pause, \'c\'+<Enter> to continue')
	
	keyboard_thread = threading.Thread(target = keyboard_input)
	keyboard_thread.start()
	
	print("Total lines to process:" , len(udp_msgs))
	
	address = "10.11.10.11"
	port = 47300
	lines = 1
	delay = 0
	verbose = None
	no_loop = None
	
	send_messages(address , int(port) , udp_msgs , int(lines) , int(delay) , verbose , no_loop)
	
	keyboard_thread.join()
