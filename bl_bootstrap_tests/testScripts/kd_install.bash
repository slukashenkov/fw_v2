#!/bin/bash  



bld_file=""
bld_dir="/KD_distr"
bld_ptrn="BL*gz"

bin_src_dir="/bin/*"
bin_trgt_dir="/usr/bin/dolphin/"
lib_src_dir="/lib/*"
lib_trgt_dir="/usr/lib/dolphin/"

cnf_file=""
cnf_file_ptrn="module_confs*gz"

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
			find_latest_f cnf_file bin_trgt_dir cnf_file_ptrn 		
			echo "Use default: ${bld_file}"
	fi
}



function inst_bld {

	if [ -a ${bld_file}  ]; then
		/bin/tar -xzvf ${bld_file} -C ${bld_dir};	
		alias cp='cp';  
		cp -f $(echo ${bld_dir}${lib_src_dir}) ${lib_trgt_dir} 
		cp -f /KD_distr/bin/* /usr/bin/dolphin/

	else
		echo "File does not exist"
	fi
}


function inst_confs {

	if [ -a ${bld_file}  ]; then
		/bin/tar -xzvf ${cnf_file} -C ${bin_trgt_dir};	

	else
		echo "File does not exist"
	fi
}


#===========================================================================|
#ACTION
has_distr_name ${1}
has_confs_name 
inst_bld


#===========================================================================|
#ACTION
has_distr_name ${1}
has_confs_name 
inst_bld
inst_confs
