from test_bl.test_trassa_plugin.structs_trassa.astdutils.astd_parser import astd_msgs


class AstdMsg():
	
	
	def __init__ (self):
		self.astd_msgs = astd_msgs()
		return
	
	
	def parse_astd (self,
					astd_msg):
		astd_parsed = self.astd_msgs.parse(astd_msg)
		return astd_parsed


def test_this ():
	astd_msg = AstdMsg()
	test_astd = {}
	
	# ASTD stuct
	test_astd['trassa'] = astd_msg.get_trassa()
	
	return


if __name__ == "__main__":
	test_this()
