import sys
import os
import shutil
import re
from obspy import read
from datetime import timedelta
from datetime import datetime
import warnings
import pprint
import time
import subprocess



# network name must be inserted as second arg
try:
    netwrok_name = str(sys.argv[1])
except IndexError:
    print("you need to insert network name!")
    sys.exit(1)

dir_path = f"./{netwrok_name}"
bigList = os.listdir(dir_path)
init_chnl = None
devnull = open(os.devnull, 'w')
# # # # #
 # # # #
# # # # #
def output_strip(i_bytes):
    if not isinstance(i_bytes, bytes):
        return i_bytes
    # get byte input and decode into utf-8 and omit space and newline
    decoded = i_bytes.decode('utf-8')
    return decoded.strip()


def merge(input_path):
    # for issues if not merging or further reading see:
    # https://docs.obspy.org/packages/autogen/obspy.core.stream.Stream._cleanup.html#obspy.core.stream.Stream._cleanup
    st = read(f'{input_path}.0')
    idx = 1
    while os.path.exists(f'{input_path}.{idx}'):
        st += read(f'{input_path}.{idx}')
        idx += 1
    # sort
    st.sort(['starttime'])

    # merge together
    st.merge(method=1)

    # sanity check for merging
    try:
        st._merge_ckecks()
    except Exception as e:
        print('Exception!! ', e, f'\n\n{input_path}\n\n')

    # write to file
    # replace HH with BH if it exists
    st.write(f'{input_path}'.replace('HH', 'BH'), format='SAC')
    print('merge!!!')




# initialize the dict for each event with unique loc and date
# to create a unique directory for them
eventinfo={}
for comp in bigList:
    evinfo = read(dir_path+"/"+comp)

    # Get geo data of event from sac header
    lon=evinfo[0].stats.sac['evlo']
    lat=evinfo[0].stats.sac['evla']
    dep=evinfo[0].stats.sac['evdp']

    # Get time data for event from sac header
    days = int(evinfo[0].stats.sac['nzjday']) -1  # minus one to correct the year convertion
    refr = timedelta(
        days= days,
        seconds=int(evinfo[0].stats.sac['nzsec']),
        milliseconds=int(evinfo[0].stats.sac['nzmsec']),
        minutes=int(evinfo[0].stats.sac['nzmin']),
        hours=int(evinfo[0].stats.sac['nzhour'])
        )
    origin_diff = timedelta(seconds = int(evinfo[0].stats.sac['o']))
    year = datetime(int(evinfo[0].stats.sac['nzyear']),1,1,0,0,0)

    # Put the time and difference together as datetime object
    evtime = year + refr + origin_diff
    event_path = "Event_"+evtime.strftime("%Y.%m.%d.%H.%M.%S.%f").rstrip("0")
    # print(event_path)
    # print(evinfo[0].stats.sac['nzmsec'])

    event_year = int(evinfo[0].stats.sac['nzyear'])
    event_jday = int(evinfo[0].stats.sac['nzjday'])

    eventinfo[(lon,lat,dep,event_year,event_jday)] = event_path
#
#

print(f"{len(eventinfo)} events detected!")
# pprint.pprint(eventinfo)
# #
#
stationList = set()
# In the second loop each component will be checked
# to find the corresponding event and copy there
for comp in bigList:
    comp_info = read(dir_path+"/"+comp)


    # Get file name for storing in "station.channel" format
    station_name = str(comp_info[0].stats.station)
    stationList.add(station_name)
    file_name = station_name+"."+str(comp_info[0].stats.channel)

    # defining either BH or HH:
    # if not init_chnl:
    init_chnl = str(comp_info[0].stats.channel)[0]


    # extracting loc and year for the event
    lon=comp_info[0].stats.sac['evlo']
    lat=comp_info[0].stats.sac['evla']
    dep=comp_info[0].stats.sac['evdp']
    event_year = int(comp_info[0].stats.sac['nzyear'])
    event_jday = int(comp_info[0].stats.sac['nzjday'])
    evnt_path = eventinfo[(lon,lat,dep,event_year,event_jday)]
    if not os.path.exists(dir_path+"/"+evnt_path):
        os.mkdir(dir_path+"/"+evnt_path)

    i = 0
    while os.path.exists(dir_path+"/"+evnt_path+"/"+file_name+"."+str(i)):
        i+=1

    shutil.move(dir_path+"/"+comp, dir_path+"/"+evnt_path+"/"+file_name+"."+str(i))

# create list of events
eventList = list(eventinfo.values())
with open(dir_path+'/eventList', 'w') as file_handler:
    for item in eventList:
        file_handler.write("{}\n".format(item))

# create list of stations
with open(dir_path+'/stationList', 'w') as file_handler:
    for item in stationList:
        file_handler.write("{}\n".format(item))


# just to be sure the files are created
time.sleep(1)

# in this loop search for any merge if needed
# otherwise just remove the zeros from the end of the file names
for event in eventList:
    for stat in stationList:
        # There were some networks with mixed type of channels therefore
        # I added the try except below to get the channel for each file
        try:
            st_header = read(f"{dir_path}/{event}/{stat}.*")
            init_chnl = str(st_header[0].stats.channel)[0]
        except Exception:
            pass



        try:
            ls_output_E = subprocess.check_output(f"ls {dir_path}/{event}/{stat}.{init_chnl}HE* | wc -l", stderr = subprocess.DEVNULL, shell=True)
        except subprocess.CalledProcessError:
            ls_output_E = 0
        ctE = int(output_strip(ls_output_E))

        try:
            ls_output_N = subprocess.check_output(f"ls {dir_path}/{event}/{stat}.{init_chnl}HN* | wc -l", stderr = subprocess.DEVNULL, shell=True)
        except subprocess.CalledProcessError:
            ls_output_N = 0
        ctN = int(output_strip(ls_output_N))

        try:
            ls_output_Z = subprocess.check_output(f"ls {dir_path}/{event}/{stat}.{init_chnl}HZ* | wc -l", stderr = subprocess.DEVNULL, shell=True)
        except subprocess.CalledProcessError:
            ls_output_Z = 0
        ctZ = int(output_strip(ls_output_Z))

        if ctE > 1:
            merge(f"{dir_path}/{event}/{stat}.{init_chnl}HE")
        elif ctE == 1:
            # print(f">>>{dir_path}/{event}/{stat}.{init_chnl}HE.0")
            # replace HH with BH if it exists while copying

            shutil.move(f"{dir_path}/{event}/{stat}.{init_chnl}HE.0", f"{dir_path}/{event}/{stat}.BHE")

        if ctN > 1:
            merge(f"{dir_path}/{event}/{stat}.{init_chnl}HN")
        elif ctN == 1:
            shutil.move(f"{dir_path}/{event}/{stat}.{init_chnl}HN.0", f"{dir_path}/{event}/{stat}.BHN")

        if ctZ > 1:
            merge(f"{dir_path}/{event}/{stat}.{init_chnl}HZ")
        elif ctZ == 1:
            shutil.move(f"{dir_path}/{event}/{stat}.{init_chnl}HZ.0", f"{dir_path}/{event}/{stat}.BHZ")
