import re

from test_bl.test_bl_tools import send_receive


class astd_meta(type):
	
	
	def __new__ (cls_to_create,
				 name_of_the_cr_cls,
				 bases,
				 attr_dict
				 ):
		return super(astd_meta, cls_to_create).__new__(cls_to_create,
													   name_of_the_cr_cls,
													   bases,
													   attr_dict)
	
	
	def __init__ (cls_to_create,
				  name_of_the_cr_cls,
				  bases,
				  attr_dict
				  ):
		super(astd_meta, cls_to_create).__init__(name_of_the_cr_cls,
												 bases,
												 attr_dict
												 )
		cls_to_create.created_classes[name_of_the_cr_cls] = name_of_the_cr_cls
		if 'fields' in attr_dict.keys():
			cls_to_create.classes_fields[name_of_the_cr_cls] = dict(
				(f[1], i) for i, f in enumerate(attr_dict['fields']))
			cls_to_create.created_classes[name_of_the_cr_cls] = cls_to_create


class astd_msgs(object,
				metaclass = astd_meta):
	created_classes = {}
	classes_fields = {}
	
	
	def __init__ (self,
				  sub_cls = None,
				  fields = None):
		
		if sub_cls is not None and fields is not None:
			name_sub = type(sub_cls).__name__
			self.created_classes[name_sub] = sub_cls
			self.classes_fields[name_sub] = dict((f[1], i) for i, f in enumerate(sub_cls.fields))
		return
	
	
	# @staticmethod
	def parse (self,
			   line):
		
		parsed_data = {}
		
		if type(line) is str:
			astd_fields = line.split('.')
		else:
			raise Exception("Message is not a string")
		
		message_type = str(astd_fields[1]).lower()
		r_msg_type = re.compile(message_type)
		
		if message_type in self.created_classes.keys():
			num_of_fields_reg = len(self.classes_fields[message_type]) - 1
			num_of_fields_res = len(astd_fields)
			if num_of_fields_reg == num_of_fields_res:
				payload = self.created_classes[message_type].parse_payload(astd_fields[3])
				astd_fields[-1] = payload[0]
				astd_fields.append(payload[1])
				for fld_name in self.classes_fields[message_type]:
					idx = self.classes_fields[message_type][fld_name]
					parsed_data[fld_name] = astd_fields[idx]
			
			return parsed_data
		else:
			raise Exception("Message type subclass is not named as deviceId in ASTD message as it MUST")


class trassa(astd_msgs):
	"""
	trassa ASTD message example: S.TRASSA.FE.KD1G
	"""
	fields = (
		('signal_type', 'signal_type'),
		('device_id', 'device_id'),
		('network_type', 'network_type'),
		('kd_id', 'kd_id'),
		('payload', 'trassa_status'),
	)
	
	
	@staticmethod
	def parse_payload (last_field):
		
		r_msg_payload = re.compile(r''' ^.*
                                        (?P<signal_type>KD1)
                                        .*
                                        (?P<trassa_msg>                        
                                                        # payload 
                                                        (.*\w{1}$)
                                                    )
                                    ''', re.X | re.IGNORECASE)
		match = r_msg_payload.match(last_field)
		if not match:
			raise Exception('could not parse data')
		else:
			signal_type = match.group('signal_type')
			last_field = match.group('trassa_msg')
			result = (signal_type, last_field,)
			return result


class other(astd_msgs):
	fields = (
		('signal_type', 'signal_type'),
		('device_id', 'device_id'),
		('network_type', 'network_type'),
		('kd_id', 'kd_id'),
		('payload', 'other_msg'),
	)


def test_this ():
	astd_msg_g = 'S.TRASSA.FE.KD1G'
	astd_msg_f = 'S.TRASSA.FE.KD1F'
	trassa_astd_msgs = astd_msgs()
	parsed_trassa_astd_msg = trassa_astd_msgs.parse(astd_msg_f)
	
	sr = send_receive.SendReceive(q_based = True)
	udp_srv_name = sr.set_udp_server(ip_address = "10.11.10.12",
									 port = 47300)
	messages_to_send = ['w']
	sr.test_messages_received(messages_list = messages_to_send,
							  server_id = udp_srv_name)
	'''get the queue to read from'''
	received_q = sr.get_received_queue(udp_srv_name)
	print(received_q)
	
	str_q = received_q[0]
	str_q = str(str_q.decode())
	print(str_q)
	# received_q = received_q.decode('UTF-8')
	parsed_trassa_astd_msg = trassa_astd_msgs.parse(str_q)
	print(parsed_trassa_astd_msg)
	return


if __name__ == "__main__":
	test_this()
