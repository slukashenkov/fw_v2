class RecievedData:
	"""
	Simple storage  for data_from values
	recieved as payload from
	"""
	
	
	def __init__ (self):
		self.__received_list = []
		self.__recieved_map = {}
		self.__sent_list = []
		self.__sent_map = {}
	
	
	def set_received_l (self , value):
		self.__received_list.append(value)
	
	
	def get_received_l_all (self):
		return self.__received_list
	
	
	def get_received_l_indx (self , indx):
		return self.__received_list.pop(indx)
	
	
	def set_received_m (self , key , value):
		self.__received_map[key] = value
	
	
	def get_received_m_all (self):
		return self.__received_map
	
	
	def get_received_m_key (self , key):
		return self.__received_map.get[key]
	
	
	'''
	--------------------------------------------------------------------------------------------------------------------
	'''
	
	
	def reset_received_l (self):
		self.__received_list.clear()
		self.__received_list = []
		return
	
	
	def reset_received_map (self):
		self.__recieved_map.clear()
		self.__recieved_map = {}
		return
	
	
	'''
	--------------------------------------------------------------------------------------------------------------------
	'''
	
	
	def set_sent_l (self , value):
		self.__sent_list.append(value)
	
	
	def get_sent_l_all (self):
		return self.__sent_list
	
	
	def get_sent_l_indx (self , indx):
		return self.__sent_list.pop(indx)
	
	
	def set_sent_m (self , key , value):
		self.__sent_map[key] = value
	
	
	def get_sent_m_all (self):
		return self.__sent_map
	
	
	def get_sent_m_key (self , key):
		return self.__sent_map.get[key]
	
	
	'''
	--------------------------------------------------------------------------------------------------------------------
	'''
	
	
	def reset_sent_l (self):
		self.__sent_list.clear()
		self.__sent_list = []
		return
	
	
	def reset_sent_map (self):
		self.__sent_map.clear()
		self.__sent_map = {}
		return
