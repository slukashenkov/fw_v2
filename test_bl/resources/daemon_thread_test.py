import logging
import threading
import time

logging.basicConfig(level = logging.DEBUG ,
					format = '(%(threadName)-10s) %(message)s' ,
					)


class TestThread(threading.Thread):
	
	
	def __init__ (self , daemon):
		threading.Thread.__init__(self)
		self.daemon = daemon
		self.name = "DAEMON_THREAD"
	
	
	def run (self):
		t = threading.currentThread()
		x = 0
		while 1:
			if self.daemon:
				print("Daemon :: %s" % x)
			else:
				print("Non-Daemon :: %s" % x)
			x += 1
			time.sleep(1)


if __name__ == "__main__":
	
	print("__main__ start")
	test = "daemonic"
	if test == "daemonic":
		thread = TestThread(True)
	else:
		thread = TestThread(False)
	thread.start()
	
	for t in threading.enumerate():
		logging.info('joining %s' , t.getName())
	time.sleep(20)
	
	print("__main__ stop")
