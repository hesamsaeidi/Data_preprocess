# This script must be run before filtering.
# use `$>python3 4-1_length_check.py` in the network directory
# This code checks if events in a network has equal length
# or not, as a prepration for rotating to gc
# If the length of E and N are not equal, the data
# will trimmed to the length of the shorter one
# It needs 2 lists for processing; eventList & stationList
# The scripts flush the report into a log file named `length_check.log`


import subprocess
import os
import obspy

# Define absolute directory of the network path
try:
    home_dir = '/Users/hesam/AFRICA/1C'
    event_list = []
    with open("eventList", 'r') as el:
        for line in el:
            event_list.append(line.strip())


    station_list = []
    with open("stationList", 'r') as sl:
        for line in sl:
            if not line:
                pass
            else:
                station_list.append(line.strip())
except FileNotFoundError:
    print("eventList and/or stationList is not created")

# Error log
file = open("length_check.log", "w")
for event in event_list:
    for sta in station_list:
        n_comp = home_dir+"/"+event+"/"+sta+ ".BHN"
        e_comp = home_dir+"/"+event+"/"+sta+ ".BHE"
        if os.path.isfile(e_comp) & os.path.isfile(n_comp):
            st_N = obspy.read(n_comp, debug_headers=True)
            st_E = obspy.read(e_comp, debug_headers=True)
            if st_N[0].stats.npts == st_E[0].stats.npts:
                pass

            else:
                file.write(f">>> The {sta} has different length for E and N component\n")
                if st_N[0].stats.npts < st_E[0].stats.npts:
                    t1 = st_N[0].stats.starttime
                    t2 = st_N[0].stats.endtime
                    st_E[0].trim(t1, t2)
                    st_E.write(e_comp, format='SAC')

                else:
                    t1 = st_E[0].stats.starttime
                    t2 = st_E[0].stats.endtime
                    st_N[0].trim(t1, t2)
                    st_N.write(n_comp, format='SAC')

        else:
            file.write(f"--- The {sta} does not have E or N component for {event}.\n")


file.close()
