import os
import sys


pzList = os.listdir('./')


for i in pzList:
    with open(i, 'r') as file:
        pz_file = file.readlines()

    with open(i, 'w') as new_file:
        for line in pz_file:
            if line[0] != '*':
                new_file.write(line)
