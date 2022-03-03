import os
# This script split the response files downloaded by http request
# and contain more than one resp file and name each file by the
# start time and end time of the resp header
# By Hesam Saeidi hsaeidi@crimson.ua.edu

def make_new_file(content_list_seg, start_time, end_time, resp):
    if len(content_list_seg) > 3:
        if content_list_seg[0] == "\n":
            content_list_seg.pop(0)
        file_name = dir_path+"/"+resp[:-4]+"_"+start_time+"-"+end_time
        # print(dir_path+"/"+file_name)
        # print()
        # print(content_list_seg)
        with open(file_name, 'w') as newRespFile:
            newRespFile.writelines(content_list_seg)


dir_path = "./PZs" # pz files location
bigList = os.listdir(dir_path)
for resp in bigList:
    with open(dir_path+"/"+resp, "r") as respfile:
        content_lst = respfile.readlines()

    segment_counter = 0
    for ct, line in enumerate(content_lst):
        if 'START' in line:
            start_time = line[line.find(':')+2:].strip().replace(":", ".")
        elif 'END' in line:
            end_time = line[line.find(':')+2:].strip().replace(":", ".")
        elif len(line) == 1:
            make_new_file(content_lst[segment_counter:ct],start_time, end_time, resp)
            segment_counter = ct


            # if line == '/n':
            #     print(content_lst[:ct])
