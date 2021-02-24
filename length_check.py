# This scripts check if all the streams in one directory
# which are related to one seismic event recorded in
# different stations have the same npts or not?
# If the differnce is less that 200 npts, the script
# cut the long streams. But if there are any streams
# with less than 200 npts than the longest in the event
# all of them will be renamed with a ".short" appended
### IMPORTANT ###
# this code works with ?HZ only files
import os
import obspy
import warnings
import time


def call_trim(ev_dir):
    # this function should be called for one event with
    # different values for npts in their header
    # Then it will iterate through each stream and cut it
    # from its beginning time up to the value of the shortest
    # npts in the event
    generic_path = ev_dir+"/"+"*.?HZf"

    z_comps = obspy.read(generic_path, debug_headers=True)
    shortest_npts = z_comps[0].stats.npts
    longest_npts = z_comps[0].stats.npts
    smpl_r = z_comps[0].stats.sampling_rate
    samp_rate_warn = False
    for st_i in range(len(z_comps)):
        if z_comps[st_i].stats.npts < shortest_npts:
            shortest_npts = z_comps[st_i].stats.npts

    for st_i in range(len(z_comps)):
        if z_comps[st_i].stats.npts > longest_npts:
            longest_npts = z_comps[st_i].stats.npts
    for st_i in range(len(z_comps)):
        if z_comps[st_i].stats.sampling_rate != smpl_r:
            samp_rate_warn = True
            stat_name = z_comps[st_i].stats.station
            warnings.warn(f'Different sampling rates of {stat_name} in {generic_path}!')

    if longest_npts != shortest_npts and not samp_rate_warn:


        for st_i in range(len(z_comps)):

            t1 = z_comps[st_i].stats.starttime
            smpl_r = z_comps[st_i].stats.sampling_rate
            t2 = t1 + (shortest_npts/smpl_r) - 1/smpl_r
            stat_name = z_comps[st_i].stats.station
            stat_ch = z_comps[st_i].stats.channel
            str_path = ev_dir + "/" + stat_name + ".BHZf"
            z_comps[st_i].trim(t1, t2)
            time.sleep(0.1)
            z_comps[st_i].write(str_path, format='SAC')
            time.sleep(0.1)
    elif samp_rate_warn:
        warnings.warn('check sampling rates and rerun the code!')
        samp_rate_warn = False
    else:
        print('no trimming needed!!!! \n')



def cast_out_unsuited_streams(stat_name, stat_ch, ev_dir):
    # apped ".unsuited" at the end of the filenames without proper
    # criteria, either less npts or no predicted time to cast them
    # out of the auto picking procedure
    str_path = ev_dir + "/" + stat_name + ".BHZf"
    new_str_path = str_path + ".unsuited"
    os.rename(str_path, new_str_path)
    print(str_path)
    print(new_str_path)
    warnings.warn(f'\nOne or more files have been renamed in {ev_dir}!')



# Define absolute directory of the network path
try:
    # home_dir = '/Users/hesam/Documents/MCCC/AFRICA/test'
    home_dir = os.getcwd()
    event_list = []
    with open("eventList", 'r') as el:
        for line in el:
            event_list.append(line.strip())

except FileNotFoundError:
    print("eventList and/or stationList is not created")

for event in event_list:
    ev_dir = home_dir+"/"+event
    generic_path = ev_dir+"/"+"*.?HZf"
    try:
        z_comps = obspy.read(generic_path, debug_headers=True)

        for st_i in range(len(z_comps)):
            if z_comps[st_i].stats.sac.t2 != -12345.0:
                tB = z_comps[st_i].stats.sac.b #begin time
                tE = z_comps[st_i].stats.sac.e #end time
                t2 = z_comps[st_i].stats.sac.t2 #tuap predicted time
                smpl_r = z_comps[st_i].stats.sampling_rate
                if t2 - 25 > tB and t2 + 25 < tE:
                    pass
                else:
                    stat_name = z_comps[st_i].stats.station
                    stat_ch = z_comps[st_i].stats.channel
                    cast_out_unsuited_streams(stat_name, stat_ch, ev_dir)
            else:
                stat_name = z_comps[st_i].stats.station
                stat_ch = z_comps[st_i].stats.channel
                cast_out_unsuited_streams(stat_name, stat_ch, ev_dir)

    except Exception as e:
        print(e)

    try:
        call_trim(ev_dir)
    except Exception as e:
        print(e)
