import sys, os, logging, logging.config, json

class LoggingTools():
    def __init__(self,
                 path_to_json =None):
            """
            Logger is not set yet
            """
            self.default_path = path_to_json
            self.__setup_logging(default_path=self.default_path)

    def __setup_logging(self,
                    default_path = None
                     ):

            if default_path != None:
                if os.path.exists(default_path):
                    with open(default_path, 'rt') as f:
                        config = json.load(f)
                        logging.config.dictConfig(config)
                else:
                   raise Exception ("JSON config was not found")

                self.logger_is_set=True
            else:
                raise Exception("No JSON config for logging")


    def get_logger(self,
                   mod_name=None):
            curr_mod_logger=logging.getLogger(mod_name)
            return curr_mod_logger

def test_this():
    import sys, os, logging, logging.config, json
    from test_bl.test_sonata_plugin.test_tools_sonata.sonata_test_parser import SonataTestParser

    '''Get log config wherever we are'''
    module_abs_path = os.path.abspath(os.path.dirname(__file__))
    path_to_conf = "..\\test_bl_configs\\logging_conf.json"
    path_to_data = os.path.join(module_abs_path, path_to_conf)
    lt = LoggingTools(path_to_json=path_to_data)
    # lt.setup_logging()
    logger = lt.get_logger(__name__)
    logger.info("got logger")
    sp = SonataTestParser()


    '''Check loggers enabling disabling'''
    '''
    logger_root = lt.get_logger()
    lhStdout = logger_root.handlers
    '''
    #logging.disable(logging.DEBUG)
    #logging.disable(logging.INFO)
    #logging.disable(logging.ERROR)
    #loggers_dict =  logging.Logger.manager.loggerDict
    '''
      for logger_id in loggers_dict:
          loggers_dict[logger_id].propagate = False
            loggers_dict[logger_id].disabled = True
    '''


if __name__ == "__main__":
    test_this()