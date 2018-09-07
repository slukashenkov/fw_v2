#!/bin/bash
#some extra stuff is needed
#VBoxManage extpack install Oracle_VM_VirtualBox_Extension_Pack-4.1.6-74713.vbox-extpack

if [ -z "$1" ]; then
        echo "Usage: $0 VMNAME_or_UUID"
        exit 1
fi
set -x
VBoxManage controlvm  "$1" poweroff  #enforce turnoff
VBoxManage snapshot   "$1" restorecurrent   #retore state
VBoxManage showvminfo "$1" | grep State   #display state to ensure
VBoxHeadless -s       "$1"  #run in headless mode in background

#here is another command
#this one works fine
VBoxManage startvm "2003" --type headless --vrde=on
--vrde=on <-- nonexisting param in VBox 5.2.8
VBoxManage startvm "alt7_KD_BL2.0_10.10.10.101_02" --type headless

#Shutdown virt machine
VBoxManage controlvm alt7_KD_BL2.0_10.10.10.101_02 poweroff