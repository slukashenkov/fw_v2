from __future__ import absolute_import
from __future__ import print_function

import logging
import os
import platform
import re
import shlex
import shutil
import signal
import sys
import time
from builtins import Exception
from subprocess import Popen, check_output

# imports for scp which used Paramico as transport
import paramiko
from fabric2 import Connection
from scp import SCPClient

# imports local for project
from test_bl.test_bl_tools import var_utils


class ExtScripts:
    
    
    def __init__ (self,
                  config = None
                  ):
        """
        :param commands_file:
        :param script_location:
        :param script_type:
        """
        '''
        CURRENT SYSTEM
        '''
        self.syst = platform.system()
        '''SETUP Logging'''
        self.logger = logging.getLogger(__name__)
        '''
        CONFIG FILE USED BY THE CURRENT TEST SUITE
        '''
        if config != None:
            self.conf = config
        '''
        SETUP SSH
        '''
        self.ssh_target_ip = None
        self.ssh_target_port = None
        self.ssh_target_user = None
        self.ssh_target_pswd = None
        self.ssh_client = None
        '''
        SETUP SSH COPY
        '''
        self.ssh_scp_content_location = None
        self.ssh_target_dir = None
        '''
        SETUP FABRIC CONNECTION
        '''
        self.fabric_connection = None
        '''
        SETUP commands to be executed remotely
        '''
        self.ssh_commands_to_exec = {}
        '''
        SETUP a possibility to check commands execution of the remote host
        via dedicated script.
        The script command should be part of the above
        dictionary and key for that should be made known in advance
        '''
        self.ssh_ded_test_key = None
        '''
        SETUP VIRT_BOX exec commands (VBoxmanage based) from conf file PREFS
        '''
        self.vm_start_cmnd = None
        self.vm_shutdown_cmnd = None
        self.vm_resnap_cmnd = None
        self.vm_makesnap_cmnd = None
        '''
        SETUP REMOTE COMMANDS TO BE EXECUTED ON SUT START/STOP and OTHER ???? not envisioned yet. To be repeated in set_remote_commands function
        '''
        self.sut_start_commands = None
        self.sut_stop_commands = None
        '''
        SETUP location of the LOGGING server external to BL
        '''
        self.vm_log_srv_exec = None
        self.vm_log_srv_exec_dir = None
        self.vm_log_srv_log_file = None
        '''
        SETUP Logger banner helpers
        '''
        self.vm_start_ssh_test_banner = var_utils.Varutils().build_VM_ssh_test_banner
        self.vm_ssh_cmds_exec_banner = var_utils.Varutils().remote_commands_exec_banner
        '''-----------------------------------------------------------------------------------------------------------
        SETUP PARAMS when CONFIG is available
        '''
        if config != None:
            '''
            SETUP VIRT_BOX exec commands (VBoxmanage based) from conf file PREFS
            '''
            self.vm_start_cmnd = None
            self.vm_shutdown_cmnd = None
            self.vm_resnap_cmnd = None
            self.vm_makesnap_cmnd = None
            '''
            SETUP REMOTE COMMANDS TO BE EXECUTED ON SUT START/STOP
            and
            OTHER ???? not envisioned yet. To be repeated in set_remote_commands function
            '''
            self.sut_start_commands = None
            
            '''
            SETUP VIRT_BOX exec commands (VBoxmanage based) from conf file PREFS
            '''
            self.set_vbox_manage()
            '''
            SETUP REMOTE COMMANDS TO BE EXECUTED ON SUT START/STOP
            '''
            self.set_remote_commands()
            '''
            SETUP SSH Connection PARAMS
            '''
            self.set_connection_params()
            '''
            SETUP location of the LOGGING server external to BL
            '''
            self.vm_log_srv_exec = None
            self.vm_log_srv_exec_dir = None
            self.vm_log_srv_log_file = None
        
        return
    
    
    '''--------------------------------------------------------------------------------------------------------------'''
    '''Functions for remote shell scripts execution'''
    
    
    def start_sut (self):
        self.set_fabric_connection()
        self.fabric_run_commands()
        time.sleep(5)
        return
    
    
    def stop_sut (self):
        self.set_fabric_connection()
        self.fabric_run_commands()
        return
    
    
    def restart_sut (self):
        self.start_sut()
        self.stop_sut()
        return
    
    
    '''--------------------------------------------------------------------------------------------------------------'''
    '''Functions VM execution'''
    
    
    def vm_start (self):
        
        self.logger.debug("<== Start  VM ==>")
        self.logger.debug(self.vm_start_cmnd)
        
        if self.syst == 'Windows':
            p = Popen(self.vm_start_cmnd,
                      shell = False,
                      cwd = None
                      )
            stdout, stderr = p.communicate()
        
        elif self.syst == 'Linux':
            # p = Popen(self.vm_shutdown_cmnd,
            p = Popen(shlex.split(self.vm_start_cmnd),
                      shell = False,
                      cwd = None
                      )
            stdout, stderr = p.communicate()
        
        test = 1
        while test == 1:
            try:
                time.sleep(30)
                self.vm_start_ssh_test_banner(server_ip = self.ssh_target_ip,
                                              server_port = self.ssh_target_port,
                                              ending = 'attempts to connect to VM',
                                              logging_level = 'DEBUG',
                                              logger = self.logger
                                              )
                
                self.create_Paramiko_SSHClient()
                ssh_trans = self.ssh_client.get_transport()
                ssh_conn_state = ssh_trans.is_active()
                
                if ssh_conn_state == True:
                    test = 2
                else:
                    raise Exception('Something UnPredictable is happening with SSH_Client')
                self.vm_start_ssh_test_banner(server_ip = self.ssh_target_ip,
                                              server_port = self.ssh_target_port,
                                              ending = 'has connected to VM',
                                              logging_level = 'DEBUG',
                                              logger = self.logger
                                              )
            except:
                try:
                    raise
                except TimeoutError:
                    self.ssh_client.close()
                    continue
                except Exception as e:
                    self.ssh_client.close()
                    continue
        
        p.terminate()
        p.kill()
        return
    
    
    def vm_shutdown (self):
        self.logger.debug("<==SHUTTING DOWN NEEDED image IF IT IS UP ==>")
        self.logger.debug(self.vm_shutdown_cmnd)
        
        if self.syst == 'Windows':
            p = Popen(self.vm_shutdown_cmnd,
                      # p = Popen(shlex.split(self.vm_shutdown_cmnd),
                      shell = False,
                      cwd = None
                      )
            stdout, stderr = p.communicate()
            p.terminate()
            p.kill()
            self.logger.debug("<==SHUTTING DOWN NEEDED image -|DONE|- ==>")
            return
        elif self.syst == 'Linux':
            # p = Popen(self.vm_shutdown_cmnd,
            p = Popen(shlex.split(self.vm_shutdown_cmnd),
                      shell = False,
                      cwd = None
                      )
            stdout, stderr = p.communicate()
            p.terminate()
            p.kill()
            self.logger.debug("<==SHUTTING DOWN NEEDED image -|DONE|- ==>")
            return
    
    
    def vm_restore_snap (self):
        if self.syst == 'Windows':
            p = Popen(self.vm_resnap_cmnd,
                      shell = False,
                      cwd = None
                      )
            stdout, stderr = p.communicate()
            p.terminate()
            p.kill()
            return
        elif self.syst == 'Linux':
            p = Popen(shlex.split(self.vm_resnap_cmnd),
                      shell = False,
                      cwd = None
                      )
            stdout, stderr = p.communicate()
            p.terminate()
            p.kill()
            return
    
    
    '''--------------------------------------------------------------------------------------------------------------'''
    '''Functions for LOGGING server control'''
    
    
    def start_log_server (self):
        p = Popen(self.vm_log_srv_exec,
                  shell = False,
                  cwd = self.vm_log_srv_exec_dir
                  )
        stdout, stderr = p.communicate()
        p.terminate()
        p.kill()
        time.sleep(5)
        return
    
    
    def stop_logserver (self):
        self.syst = platform.system()
        if self.syst == 'Windows':
            name = "javaw"
            log_srv_pid = check_output(["ps", "-laW"],
                                       universal_newlines = True)
            # os.kill(get_pid(whatever_you_search), signal.SIGTERM)  # or signal.SIGKILL
            # os.kill(check_output(["pidof", name]),
            #       signal.SIGTERM)  # or signal.SIGKILL
            proc_names_data = log_srv_pid.split('\n')
            pid = []
            pid = self.getPidByName(proc_name = name,
                                    proc_data_in = proc_names_data)
        elif self.syst == 'Linux':
            name = "apache-chainsaw-2"
            log_srv_pid = check_output(["ps", "-afx"],
                                       universal_newlines = True)
            # os.kill(get_pid(whatever_you_search), signal.SIGTERM)  # or signal.SIGKILL
            # os.kill(check_output(["pidof", name]),
            #       signal.SIGTERM)  # or signal.SIGKILL
            proc_names_data = log_srv_pid.split('\n')
            pid = []
            pid = self.getPidByName(proc_name = name,
                                    proc_data_in = proc_names_data)
        for i in pid:
            os.kill(i,
                    signal.SIGTERM)  # or signal.SIGKILL
        time.sleep(5)
        self.copy_log()
        return
    
    
    def copy_log (self):
        t_stmp = time.strftime("%Y_%m_%d__%H_%M_%S", time.gmtime())
        if os.path.isfile(self.vm_log_srv_log_file):
            src = self.vm_log_srv_log_file
            dst = self.vm_log_srv_log_file + "__backup_" + t_stmp
            path_to_log = self.vm_log_srv_log_file
            self.syst = platform.system()
            if self.syst == 'Windows':
                shutil.copy(src = src, dst = dst)
                os.remove(src)
            elif self.syst == 'Linux':
                shutil.copy(src = src, dst = dst)
                os.remove(src)
        return
    
    
    '''---------------------------------------------------------------------------------------------------------------'''
    '''Common tools'''
    '''---------------------------------------------------------------------------------------------------------------'''
    '''For linux only'''
    '''---------------------------------------------------------------------------------------------------------------'''
    
    
    def getPidByName (self,
                      proc_name = None,
                      proc_data_in = None):
        
        if proc_data_in != None:
            process = proc_data_in
        else:
            process = check_output(["ps", "-afx"]).split('\n')
        pid = []
        
        for x in range(0, len(process)):
            entry_cnt = 0
            args_prep = re.sub("\s+", ",", process[x].strip())
            args = args_prep.split(',')
            for j in range(0, len(args)):
                part = args[j]
                if (proc_name in part):
                    if entry_cnt == 0:
                        pid.append(int(args[0]))
                        entry_cnt = entry_cnt + 1
                    else:
                        continue
        
        return pid
    
    
    def get_pid_from_proc (self):
        for dirname in os.listdir('/proc'):
            if dirname == 'curproc':
                continue
            
            try:
                with open('/proc/{}/cmdline'.format(dirname), mode = 'rb') as fd:
                    content = fd.read().decode().split('\x00')
            except Exception:
                continue
            
            for i in sys.argv[1:]:
                if i in content[0]:
                    print('{0:<12} : {1}'.format(dirname, ' '.join(content)))
        return
    
    
    ''' Function to execute
    '''
    
    
    def load_env_vars (self):
        # def set_env_vars(self):
        """
           Run the cmd file to set env variables
           :param default_level:
           :param env_key:
           :return:
        """
        ''' Run the cmd file to set env variables'''
        if self.script_type == "win":
            p = Popen(self.commands_file,
                      shell = False,
                      cwd = self.script_location
                      )
            stdout, stderr = p.communicate()
            p.terminate()
            p.kill()
            
            return
        if self.script_type == "sh":
            return
    
    
    def scp_files (self):
        try:
            self.create_Paramiko_SSHClient()
            scp = SCPClient(self.ssh_client.get_transport())
            '''SET PREFS AND COPY ALL CONFIGS AND SCRIPTS to DUT'''
            scp.put(self.ssh_scp_content_location, remote_path = self.ssh_target_dir)
            return
        except:
            Exception("SOMETHING BAD HAPPENED DURING COPYING OF THE FILE")
    
    
    '''------------------------------------------------------------------------------------------------------------------'''
    '''Functions for SCP and remote commands exec over SSH'''
    '''------------------------------------------------------------------------------------------------------------------'''
    
    
    def set_connection_params (self):
        '''
         SET CONNECTION PREFS
         '''
        if self.conf != None:
            self.ssh_target_ip = self.conf.ssh_host
            self.ssh_target_port = self.conf.ssh_port
            self.ssh_target_user = self.conf.ssh_user
            self.ssh_target_pswd = self.conf.ssh_pwd
        else:
            raise Exception('Configuration class is NOT loaded BUT needed. To early to set that!')
        return
    
    
    '''------------------------------------------------------------------------------------------------------------------'''
    '''SETTERS for VARIOUS PARAMS'''
    '''------------------------------------------------------------------------------------------------------------------'''
    
    
    def create_Paramiko_SSHClient (self):
        '''
        Setup pure paramico SSH client
        :return:
        '''
        
        if self.ssh_client != None:
            self.ssh_client.close()
        
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        self.logger.debug(" <== CONNECTION PARAMS: " + self.ssh_target_ip + ": " + self.ssh_target_port + " ==>")
        self.ssh_client.connect(hostname = self.ssh_target_ip,
                                port = self.ssh_target_port,
                                username = self.ssh_target_user,
                                password = self.ssh_target_pswd
                                )
        return
    
    
    def set_fabric_connection (self):
        self.fabric_connection = Connection(  # host="kd",
            host = self.ssh_target_ip,
            port = self.ssh_target_port,
            user = self.ssh_target_user)
        self.fabric_connection.connect_kwargs.password = self.ssh_target_pswd
        return
    
    
    def set_scp_details (self):
        '''
        SET ALL THE PARAMS RELATED TO COPING
        :return:
        '''
        self.ssh_scp_content_location = self.conf.ssh_content_to_copy
        self.ssh_target_dir = self.conf.ssh_target_dir
        return
    
    
    def set_vbox_manage (self):
        """SETUP VIRT_BOX exec commands (VBoxmanage based) from conf file PREFS"""
        if self.conf != None:
            self.vm_start_cmnd = self.conf.vm_vbox_manage + ' startvm ' + self.conf.vm_alt_img + ' --type headless'
            self.vm_shutdown_cmnd = self.conf.vm_vbox_manage + ' controlvm ' + self.conf.vm_alt_img + ' poweroff'
            self.vm_resnap_cmnd = self.conf.vm_vbox_manage + ' snapshot ' + self.conf.vm_alt_img + ' restore ' + self.conf.vm_alt_img_snapshot
            self.vm_makeclone_cmnd = self.conf.vm_vbox_manage + ' clonevm ' + self.conf.vm_alt_img
        else:
            raise Exception("Test Suite`s conf file is not Present")
        return
    
    
    def set_remote_commands (self):
        """SETUP REMOTE/SSH exec commands (VBoxmanage based) from conf file PREFS"""
        if self.conf != None:
            self.sut_start_commands = self.conf.ssh_remote_commands_conf_start
            self.sut_stop_commands = self.conf.ssh_remote_commands_conf_stop
        else:
            raise Exception("Test Suite`s conf file is not Present")
        return
    
    
    '''------------------------------------------------------------------------------------------------------------------'''
    '''UTILITY FUNCTIONS '''
    '''------------------------------------------------------------------------------------------------------------------'''
    
    
    def fabric_run_commands (self):
        ''' Lets create a possibility of
            dedicated test on remote host with a ASH script
            which may be needed only in some
            cases. The script should be uploaded to the target machine
            in the same archive as config files and start scripts.
            For that configure special key on the class level and
            after check whether it exists pop a command for the script execution
            from common dict (may not be entirely good idea but will work)
        '''
        ded_test_command = None
        if self.ssh_ded_test_key != None:
            ded_test_command = self.ssh_commands_to_exec.pop(self.ssh_ded_test_key)
            self.vm_ssh_cmds_exec_banner(command = ded_test_command,
                                         ending = ' for testing exec results content',
                                         logging_level = 'DEBUG',
                                         logger = self.logger
                                         )
        else:
            return
        
        for key, command in self.ssh_commands_to_exec.items():
            
            if key == self.ssh_ded_test_key:
                ded_test_command = self.ssh_commands_to_exec.pop(self.ssh_ded_test_key)
                continue
            else:
                result = self.fabric_connection.run(command)
            
            if ded_test_command != None:
                result_dedicated_test = self.fabric_connection.run(ded_test_command)
            
            else:
                result_dedicated_test = None
            
            self.vm_ssh_cmds_exec_banner(command = command,
                                         ending = ' for the key ' + str(key) + ' has been executed ',
                                         exec_res01 = 'result.ok: ' + str(result.ok),
                                         exec_res02 = 'result.return_code: ' + str(result.return_code),
                                         exec_res03 = 'result_dedicated_test.return_code: ' + str(
                                             result_dedicated_test.return_code),
                                         logging_level = 'DEBUG',
                                         logger = self.logger
                                         )
            
            if result.ok == True and result.return_code == 0 and (
                    result_dedicated_test != None or result_dedicated_test.return_code == 0):
                pass
            else:
                raise Exception('Last command did not go thru. Execution interrupted')
        return
    
    
    def set_test_env (self,
                      no_VM = None):
        """
        Function:
         1) starts VM
         2) copies current archive of configs and scripts to SUT Host
         3) sets predefined start SUT remote commands as default
         4) executes then in start)sut function
        :return:
        """
        
        if no_VM == None:
            '''make it avalable to the ScriptsControlling class'''
            # es.conf = sonata_conf
            
            self.vm_shutdown()
            self.vm_start()
            '''test whether files can be copied via scp'''
            self.scp_files()
        else:
            pass
        
        
        '''Do the test for actions on the remote host'''
        self.ssh_ded_test_key = 'test_exec'
        '''
        DEBUG THING for local test this
        '''
        
        '''Start the SUT on the remote box'''
        self.ssh_commands_to_exec = self.sut_start_commands
        self.start_sut()
        return
    
    
    def tear_down_test_env (self,
                            no_VM = None):
        """
        Function:
         1) Stops SUT
         2) Stops VM
         3) Restores clean snap
        :return:
        """
        self.ssh_commands_to_exec.clear()
        self.ssh_commands_to_exec = self.sut_stop_commands
        self.stop_sut()
        
        '''There are two options VM enabled and physical box'''
        if no_VM == None:
            self.vm_shutdown()
            self.vm_restore_snap()
        else:
            pass
        return


def test_this ():
    # imports for scp which used Paramico as transport
    
    # imports local for project
    from test_bl.test_sonata_plugin.test_tools_sonata import config_sonata_suite
    
    '''Instance of config. All preferences come from it. Connection and script commands'''
    sonata_conf = config_sonata_suite.ConfigSonataSuite()
    '''Do the test for actions on the remote host'''
    
    '''Instance External Scripting class'''
    es = ExtScripts(sonata_conf)
    '''Start log server before everything else'''
    es.start_log_server()
    es.stop_logserver()
    # es.ssh_ded_test_key = 'test_exec'
    # es.set_test_env()
    # es.tear_down_test_env()
    
    '''make it avalable to the ScriptsControlling class'''
    # es.conf = sonata_conf
    # es.vm_shutdown()
    # es.vm_start()
    
    '''test whether files can be copied via scp'''
    # es.scp_files()
    
    '''
    commands_to_exec = {}
    commands_to_exec['com00']               = 'cd /usr/bin/dolphin'
    commands_to_exec['com01']               = '/bin/tar -xzvf /usr/bin/dolphin/bl_tests.tar.gz'
    commands_to_exec['com02']               = 'cd /usr/bin/dolphin/bl_tests'
    commands_to_exec['com03']               = './StartSonataOnly.bash'
    commands_to_exec['com04']               = 'cd /usr/bin/dolphin'
    commands_to_exec['com05']               = 'rm -f ./build_num.txt'
    commands_to_exec[es.ssh_ded_test_key]   = './testScr_param.bash TESTING_LAST_COMMAND_SUCCESS_ON_SETUP'

    es.ssh_commands_to_exec = commands_to_exec
    '''
    '''TODO: Think of controlling execution.
             dedicated key name for the script
             that tests other scripts correctness.
    '''
    
    '''test loading configuration params as env vars'''
    # es.load_env_vars()
    
    '''Test commands can
       execution on the remote host
    '''
    # es.stop_sut()
    # es.start_sut()
    # es.start_sut()
    '''
    es.ssh_commands_to_exec.clear()
    commands_to_exec['com01'] = 'cd /usr/bin/dolphin/bl_tests'
    commands_to_exec['com03'] = './StopSonataOnly.bash'
    commands_to_exec[es.ssh_ded_test_key] = './testScr_param.bash TESTING_LAST_COMMAND_SUCCESS_ON_TEARINGDOWN'
    es.ssh_commands_to_exec = commands_to_exec
    '''
    # es.stop_sut()
    # es.restart_sut()
    # es.vm_shutdown()
    # es.vm_restore_snap()
    
    '''Test ENV Var Setup'''
    # es.commands_file = 'C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\env_setup.cmd'
    return


if __name__ == "__main__":
    test_this()
