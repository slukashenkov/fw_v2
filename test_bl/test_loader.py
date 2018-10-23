import unittest, time, xmlrunner, datetime, platform, os, argparse, copy


def create_parser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-test_name', help = 'module name. Currently: sonata , trassa')
    return parser

def get_suites_path ():
    '''Lets find ot the system we run on'''
    syst = platform.system()
    '''And where we are'''
    proj_abs_path = os.path.abspath(os.path.dirname(__file__))
    if syst == "Windows":
        trassa_tests_path = os.path.join(proj_abs_path,
                                         "test_trassa_plugin\\tests_trassa")
        sonata_tests_path = os.path.join(proj_abs_path,
                                         "test_sonata_plugin\\tests_sonata")

    elif syst == "Linux":
        trassa_tests_path = os.path.join(proj_abs_path,
                                         "test_trassa_plugin/tests_trassa")
        sonata_tests_path = os.path.join(proj_abs_path,
                                         "test_sonata_plugin/tests_sonata")
    test_suites = {}
    test_suites['sonata'] = sonata_tests_path
    test_suites['trassa'] = trassa_tests_path

    return test_suites
def run_test_suite (path_to_tests = None,
                    path_to_logs = '/home/slon/jenkins/workspace/BL2_alt7_baselibraries_D_autotests/logs/sonata_xml_logs_'):

    for mod_name in path_to_tests:
        path_to_curr_test = path_to_tests[mod_name]
        date_now = datetime.datetime.now()
        date_now_str = date_now.strftime("%Y-%m-%d_%H-%M")
        loader = unittest.TestLoader()
        suite = loader.discover(path_to_curr_test)
        runner = xmlrunner.XMLTestRunner(output= path_to_logs + str(mod_name)+'_'+ date_now_str)
        result = runner.run(suite)

if __name__ == '__main__':

    '''All or individual tests'''
    path_logs = '/home/slon/jenkins/workspace/BL2_alt7_baselibraries_D_autotests/logs/xml_logs_'
    parser = create_parser()
    args = parser.parse_args()
    print(args)
    test_suites = get_suites_path()

    if args.test_name != None and (args.test_name in test_suites.keys()):
        print(args)
        path_to = {}
        path_to[str(args.test_name)] = copy.deepcopy(test_suites[args.test_name])
        run_test_suite(path_to_tests = path_to,
                       path_to_logs = path_logs)
    else:
        run_test_suite(path_to_tests = test_suites,
                       path_to_logs = path_logs)

