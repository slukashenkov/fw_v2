#/bin/bash

# This is a script for additional verification that 
# any one of the commands run on external machine over ssh session
# has actually done whatever they suppose to do.
#
# For the cases when exit status of the command is
#not good enough indication

#SET SOME COMMON VARS

PATH_TO_FILE='/usr/bin/dolphin/param'
#PATH_TO_FILE='/home/vialuk/bl_framework/resources/testScripts/param'
PARAM=""
#echo " Before funct param ${PARAM}"

# ==============================================================
# Functions
# ==============================================================
test_step ( ) 
{
	case ${param} in
			BL)
				echo " TEST START of BL ";
				egrep_res=$(ps afx | egrep ".*./[W]atchDogServer --start .*");
				#egrep_res=$( ps afx | egrep "17380.*/usr/bin/[s]sh" );
				echo ${egrep_res}
				if [ `echo $?` == "0" ]
			       		then 
						echo "GOOD"; 
						return 0; 
					else 
						echo "!!!!---BAAAAAD---!!!!"; 
						return 99; 
				fi
			;;
			INST)
				echo " TEST INSTALLATION of BL ";
			;;	
	esac
}

read_file ( ) 
{
	export PARAM=$(< ${PATH_TO_FILE})
	#echo " inside funct param ${PARAM}"
	echo ${PARAM}
}

empty_file ( )
{
	cat > ${PATH_TO_FILE} <<< "NULL"
}


# ==============================================================
# MAIN ENTRY 
# ==============================================================
#if [ -z	${1}  ]
#echo " before funct call param ${PARAM}"
read_file
#echo " before funct call param ${PARAM}"

#echo ${PARAM}
if [ -z	${PARAM}  ]
then
	echo "WARNING!!! WRONG FLAG";	
	echo "Acceptable choices:";
	echo "BL - to test BL startup";
	echo "INST - to test BL intallation";
fi

#case ${1} in 
case ${PARAM} in 
		BL|INST)
			#echo "Parm to test:"; echo  ${1};
			#echo "Parm to test:"; echo  ${PARAM};
			#param=${1};
			param=${PARAM};
			export param;  
			#./test_this.bash;
			test_step;
			empty_file;
			;;

		NULL)
			empty_file;
			exit 0
			;;
		*)
			echo "WARNING!!! WRONG FLAG";	
			echo "Acceptable choices:";
			echo "BL - to test BL startup";
			echo "INST - to test BL intallation";
			;;
esac
