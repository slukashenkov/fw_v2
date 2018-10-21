#!/bin/bash


#BLD file related
bld_file=""
bld_dir="/KD_distr"
bld_ptrn="BL*gz"

#Intall locations
bin_src_dir="/bin/*"
lib_src_dir="/lib/*"
bin_trgt_dir="/usr/bin/dolphin/"
lib_trgt_dir="/usr/lib/dolphin/"

#Modules confs related
cnf_file=""
cnf_file_ptrn="module_confs*gz"

#Test install conf 
install_conf_dir="install_confs/"
start_test_app="install_confs/StartTestUDP.bash"
stop_test_app="install_confs/StopTestUDP.bash"

#Logging conf
logging_conf="log4cxx.properties"
logging_test_conf="log4cxx.properties_file"


#CREATE INSTALL DIRECTORIES
function create_inst_dirs {

#Check if dir for bin files exists
        if [ ! -d ${bin_trg_dir} ]; then
                /bin/mkdir -v ${bin_trgt_dir}
        fi

#Check if dir for libs exists
        if [ ! -d ${lib_trgt_dir} ]; then
                /bin/mkdir -v ${lib_trgt_dir}
        fi
}

function find_latest_f {
echo "Enter ${FUNCNAME} with: ${1} ${2} ${3}"

	local __return=${1}
	local __loc_dir=${!2}
	local __srch_ptrn=${!3}
	
	if [ -d ${__loc_dir} ]; then
		
		local result=""
		local result=$(find  $__loc_dir -name ${__srch_ptrn} -print0 | xargs -0 ls -1 -t | head -1)
	else
		echo "No directory to search files in"
		exit 99
	fi

	if [[ -n "${__return}"  ]]; then

		eval ${__return}=${result}	
	else

		echo ${result}
	fi
}

function has_distr_name {

echo "Enter ${FUNCNAME} with: ${1}"

	local __fl_name=${1}

	if [ -n "${1+present}" ]; then
		if [ -e ${1} ];then
			echo "Build file exists at: ${1} "
			eval ${__fl_name}=${1}	
		else
			echo "No file with this name"
			exit 99
		fi
	else
			find_latest_f bld_file bld_dir bld_ptrn		
			echo "Use default: ${bld_file}"
	fi
}



function has_confs_name {

echo "Enter ${FUNCNAME} with: ${1}"

	local __fl_name=${1}

	if [ -n "${1+present}" ]; then
		if [ -e ${1} ];then
			echo "Config files exists at: ${1} "
			eval ${__fl_name}=${1}	
		else
			echo "No file with this name"
			exit 99
		fi
	else
		 cnf_file=""
			find_latest_f cnf_file bld_dir cnf_file_ptrn 		
			echo "Use default: ${cnf_file}"
	fi
}



function inst_bld {

	if [ -a ${bld_file}  ]; then
		/bin/tar -xzf ${bld_file} -C ${bld_dir};
		alias cp='cp';  
		cp -f $(echo ${bld_dir}${lib_src_dir}) ${lib_trgt_dir} 
		cp -f $(echo ${bld_dir}${bin_src_dir}) ${bin_trgt_dir} 

	else		echo "File does not exist"
	fi
}


function inst_confs {

	if [ -a ${cnf_file}  ]; then
		alias cp='cp';  
		/bin/tar -xzf ${cnf_file} -C ${bin_trgt_dir};

	else
		echo "File does not exist"
	fi
}

function start_app_test {
	test_app_start_path=$(echo ${bin_trgt_dir}${start_test_app})
	test_app_stop_path=$(echo ${bin_trgt_dir}${stop_test_app})
	if [ -f ${test_app_start_path_path} ]; then
		cp -f $(echo ${bin_trgt_dir}${install_conf_dir}${logging_test_conf}) $(echo ${bin_trgt_dir}${logging_conf}) 
		eval $(echo ${test_app_start_path})	
		
		while :
		do
			ps afx | egrep ".*./[W]atchDogServer --start .*"	

			if [ $? ];
			then
				echo "Test config started successfully"
				eval $(echo ${test_app_stop_path})	
				sleep 3
				break
			else
				sleep 3
				continue
			fi
		done

		cp -f $(echo ${bin_trgt_dir}${install_conf_dir}${logging_conf}) ${bin_trgt_dir} 
	else 
		echo "Test conf file does not exist"
	fi
}

#===========================================================================|
#ACTION
create_inst_dirs
has_distr_name ${1}
has_confs_name ${2}
inst_bld
inst_confs
start_app_test
