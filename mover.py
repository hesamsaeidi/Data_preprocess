# This file should be called with command below and
# python mover.py HH /Users/Hesam/AFRICA/TEST
# it needs 2 args the first one mention what kind of network
# you want, HH or BH, the second one is the destination directory
# for copying the scripts there.

import os
import sys

try:
    pre_address=sys.argv[1]
    new_addr=sys.argv[2]
except IndexError:
    print("you need to insert type of the network and destination!")
    sys.exit(1)

if not os.path.exists(new_addr):
    os.makedirs(new_addr)

defualt_addr = "/Users/hesam/AFRICA/1C"

file_list = [
    "1merge_rename.perl",
    "2removePZ_forE.perl",
    "2removePZ_forN.perl",
    "2removePZ.perl",
    "3cleanUp.perl",
    "4-1_length_check.py",
    "4filterData_Horiz.csh",
    "4filterData.csh",
    "5mark_taup.csh",
    "pickData.csh"
]

for i_scr in file_list:
    with open(pre_address+'/'+i_scr, 'r') as file:
        my_script = file.readlines()
        for count, line in enumerate(my_script):
            if defualt_addr in line:
                my_script[count] = line.replace(defualt_addr, new_addr)
                


    fo = open(new_addr+'/'+i_scr, "w+")
    fo.writelines(my_script)
    fo.close
    # files need to be executable, so:
    os.chmod(new_addr+'/'+i_scr, 0o755)
