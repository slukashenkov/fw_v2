@ECHO OFF

:: GENERAL PROJECT PREFS
:: PROJECT LOCATION; PROJECT LOGGING LOCATION


::General framework configs
::HOME
::SETx PROJECT_PATH "d:\data\python\projects\bl_frame_work_25_05_18_02\bl_frame_work"
::SETx BL_TESTS_PATH "d:\data\python\projects\bl_frame_work_25_05_18_02\bl_frame_work\test_bl"
::SETx BL_CONF_PATH "d:\data\python\projects\bl_frame_work_25_05_18_02\bl_frame_work\test_bl\test_bl_configs"

::General framework configs
:: WORK C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\test_bl\\test_bl_configs\\logging_conf.json
SETx PROJECT_PATH "C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work"
SETx BL_TESTS_PATH "C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work\test_bl"
SETx BL_CONF_PATH "C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work\test_bl\test_bl_configs"

::Logging configuration
::HOME

::SETx BL_LOG_CONF_PATH "d:\data\python\projects\bl_frame_work_25_05_18_02\bl_frame_work\test_bl\test_sonata_plugin\configs_sonata\"
::SETx BL_LOG_CONF_PATH_TOF "d:\data\python\projects\bl_frame_work_25_05_18_02\bl_frame_work\test_bl\test_sonata_plugin\configs_sonata\logging_conf.json"
::SETx BL_LOG_CONF_FNAME "logging_conf.json"
::SETx BL_LOGGING_DIR "d:\data\python\projects\bl_frame_work_25_05_18_02\bl_frame_work"

::Logging configuration
::WORK C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work\test_bl\test_bl_configs\logging_conf.json
SETx BL_LOG_CONF_PATH "C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work\test_bl\test_bl_configs"
SETx BL_LOG_CONF_PATH_TOF "C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work\test_bl\test_sonata_plugin\configs_sonata\logging_conf.json"
SETx BL_LOG_CONF_FNAME "logging_conf.json"
SETx BL_LOGGING_DIR "C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work"
SETx BL_LOGGING_LEVEL "logging.INFO"


:: TESTS SPECIFIC CONFIGS
:: FILE WITH MESSAGES TO BE SENT OUT.
:: IT CAN BE PLAIN TEXT FILE OR JSON(FROM DB OR OTHERWISE) FOR MORE ELABORATE TEST CASES


:: SWITCHER for CONFIG CLASS TO PICK TEST MESSAGES CONTENT SOURCE
:: Possible values as of 31.05.2018
:: JSON; TXT
SETx BL_MESSAGES_SRC "JSON"
:: SETx BL_MESSAGES_SRC "TXT"

:: SWITCHER for CONFIG CLASS TO PICK TEST MESSAGES CONTENT TYPE
:: Possible values as of 05.06.2018 - SONATA
SETx BL_MESSAGES_TYPE "SONATA"
::CONTENT FROM TEXT FILE
:: WORK
:: SETx BL_MESSAGES_PATH "C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work\resources\messagesUDP.txt"
:: SETx BL_MESSAGES_PATH "C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work\test_bl\test_sonata_plugin\resources_sonata\sonata_fields.txt"
SETx BL_MESSAGES_PATH_JSON "C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work\test_bl\test_sonata_plugin\resources_sonata\sonata_test_data.json"
SETx BL_MESSAGES_PATH_TXT "C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work\test_bl\test_sonata_plugin\resources_sonata\sonata_fields.txt"

:: HOME
::SET BL_MESSAGES_PATH=D:\data\python\projects\bl_frame_work_23_05_18\bl_frame_work\resources\messagesUDP.txt"

:: CONTENT FROM JSON
:: TO DO


:: TEST traffic configs
SETx SENDER_PAUSE_FLAG "False"
SETx SENDER_STOP_FLAG "False"
SETx NUM_OF_MSGS "3"
SETx DEL_BTWN_MSGS "1"

:: TEST REAFFIC SENDER/RECEIVER PARAMS
SETx BL_IP_TO "10.11.10.11"
SETx BL_PORT_TO "55555"
SETx BL_PROT_TO "UDP"
SETx BL_IP_ON "10.11.10.12"
SETx BL_PORT_ON "55556"
SETx BL_BUFFSZ_ON "4096"



::ALL PATHS COMBINED FOR SYS PATH
SETx BL_PATHS ";%PROJECT_PATH%;%BL_TESTS_PATH%;%BL_CONF_PATH%"

::SET PROJECT_PATH=d:\data\python\projects\bl_frame_work_25_05_18_02\bl_frame_work
::SET BL_TESTS_PATH=d:\data\python\projects\bl_frame_work_25_05_18_02\bl_frame_work\test_bl
::SET BL_CONF_PATH=d:\data\python\projects\bl_frame_work_25_05_18_02\bl_frame_work\test_bl\test_bl_configs
::SET BL_LOG_CONF_FILE=d:\data\python\projects\bl_frame_work_25_05_18_02\bl_frame_work\test_bl\test_sonata_plugin\configs_sonata\logging_conf.json
::SET BL_LOG_CONF_PATH=%BL_CONF_PATH%\logging_conf.json
::WORK
::SET BL_MESSAGES_PATH=C:\data\kronshtadt\QA\BL\AutomationFrameworkDesign\bl_frame_work\resources\messagesUDP.txt
::HOME
::SET BL_MESSAGES_PATH=D:\data\python\projects\bl_frame_work_23_05_18\bl_frame_work\resources\messagesUDP.txt

::ALL PATHS COMBINED FOR SYS PATH
::SET BL_PATHS=;%PROJECT_PATH%;%BL_TESTS_PATH%;%BL_CONF_PATH%


:: Set Path variable
setx PATH "%BL_PATHS%"


:: PAUSE