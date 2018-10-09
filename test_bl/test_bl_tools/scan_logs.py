import logging
import re
import sys


class ScanLogs():
	
	
	def __init__ (self ,
				  logs_location ,
				  search_pttrn
				  ):
		self.logger = logging.getLogger(__name__)
		self.search_pttrn = search_pttrn
		self.logs_location = logs_location
	
	
	def scan_logs (self ,
				   pattern_in = None
				   ):
		"""
		:param pattern_in:
		:return:
		"""
		
		'''SET THE PATTERN'''
		if pattern_in == None:
			pattern = self.search_pttrn
		else:
			pattern = pattern_in
		
		'''
		GET THE BLOODY LOG first
		'''
		log_for_parsing = self.log_reader(self.logs_location)
		
		matches = []
		comp_result = {}
		full_text = ""
		for line in log_for_parsing:
			res = self.parse_line(line_in = line ,
								  pattern_in = pattern)
			if res != None:
				line_matched = res.string
				matches.append(line_matched)
			full_text = full_text + str(line)
		comp_result[pattern] = matches
		
		'''
		Here is a simpler way to obtain
		an array of matches
		but it returns just an expression
		for comparison it would be good to see
		full string from the log
		'''
		matches_02 = self.parse_all(lines_in = full_text ,
									pattern_in = pattern)
		log_for_parsing.close()
		return comp_result
	
	
	def parse_line (self ,
					line_in = None ,
					pattern_in = None):
		srch = re.compile(pattern_in)
		res = srch.search(line_in)
		return res
	
	
	def parse_all (self ,
				   lines_in = None ,
				   pattern_in = None):
		srch = re.compile(pattern_in)
		res = srch.findall(lines_in)
		return res
	
	
	def log_reader (self ,
					logfile = None
					):
		if logfile == None:
			raise Exception("NO PATH to the File To parse")
		try:
			log = open(logfile , 'r')
		except IOError:
			print("You must specify a valid file to parse")
			print(__doc__)
			sys.exit(1)
		
		return log


def test_this ():
	sl = ScanLogs(
		logs_location = "C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\ext_tools\\KD_LOGS\\kd_LogFile.log")
	
	matches = sl.scan_logs(pattern_in = "Message too short")
	# matches = sl.scan_logs(pattern_in="Message does not start")
	# matches = sl.scan_logs(pattern_in="Wrong message CRC")
	return


if __name__ == "__main__":
	test_this()
