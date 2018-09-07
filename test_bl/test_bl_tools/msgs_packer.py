from test_bl.test_sonata_plugin.configs_sonata import sonata_send_recieve_properties



class MessagesPacker:
    def __init__(self,
                 conf=sonata_send_recieve_properties.SonataSendReceiveProperties):

        return

    def load_messages(self):

        """
        self.messages_type,
                                               self.messages_src,
                                               self.messages_dir_json
        Here we want to pick messages for the test selectively.
            1) In the simplest case by loading them from the text file as it was done for the case of prototype sending UDP
            2) In more elaborate cases use some utility classes to load data_from from json into proper structure
            for later usage it in the test
        :return:
        """
        '''
        Store messages to be sent out
        '''
        udp_msgs = []
        '''
        Clean up ultimate receiver of 
        TEST messages
        '''
        self.msgs_to_send = None

        if self.messages_src == "TXT":
            '''
            Read stuff from the file
            '''
            try:
                # with open(filename, 'r') as fin:
                with open(self.message_dir, 'r') as fin:

                    for line in fin:
                        start = line.find('$')
                        msg = (line[start:] if start != -1 else line).strip()
                        '''do not get this messaging yet '''
                        # msg = filter_message(msg, msg_filter)
                        if not msg:
                            continue
                        udp_msgs.append(''.join([msg, '\n\n']))

            except (OSError, IOError) as e:
                print(str(e))
            self.msgs_to_send = udp_msgs
            return

        elif self.messages_src == "JSON":
            '''
            Read stuff from the JSON config.
            TODO: the JSON reading part 
            For now 5.06.18
            just get a couple of Sonata messages
            for 
            testing purposes
            '''
            if self.messages_type == "SONATA":
                s_msg = sonata_msg.SonataMsg(self)
                msg = s_msg.get_msg()
                s_msg_range = [1, 2, 3]
                for i in s_msg_range:
                    try:
                        udp_msgs.append(''.join([msg, '\n\n']))
                    except (OSError, IOError) as e:
                        print(str(e))
            self.msgs_to_send = udp_msgs
            return


