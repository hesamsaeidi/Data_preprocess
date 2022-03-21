import os
import obspy
import numpy as np
import warnings
import requests
import re
import time
from bs4 import BeautifulSoup as BS


def elevation_grabber(station_name):

    req_add = 'http://service.iris.edu/irisws/sacpz/1/query?net=AF&sta=STATION&loc=*&cha=*&nodata=404'
    req_add = req_add.replace('STATION', station_name)
    resp_sta = requests.get(req_add)
    if resp_sta.status_code != 200:
        req_add = 'http://geofon.gfz-potsdam.de/fdsnws/station/1/query?net=AF&station=STATION&level=response'
        req_add = req_add.replace('STATION', station_name)
        resp_sta = requests.get(req_add)
        if resp_sta.status_code != 200:
            return str(0)
        else:
            soup = BS(resp_sta.text)
            elev = soup.find('elevation').text
            return elev

    else:
        time.sleep(.1)
        ele = re.search('ELEVATION\s+:(.*)\\n', resp_sta.text)
        elev = ele.group(1).strip()
        elev = str(float(elev))
        return elev


def event_time_extractor(line):
    date_time_list = line[6:].split('.')
    if len(date_time_list) == 7:
        evtyr, mon, day, hr, min, secM, secD = line[6:].split('.')
        sec = secM + '.' + secD
    elif len(date_time_list) == 6:
        evtyr, mon, day, hr, min, sec = line[6:].split('.')
    else:
        warnings.warn("WARNINGS! Event file names are not correct")

    return evtyr, mon, day, hr, min, sec

dir_path = os.getcwd()
sac_file_extention = '.BHRf'

try:
    event_list = []
    with open("eventList", 'r') as el:
        for line in el:
            event_list.append(line.strip())

except FileNotFoundError:
    print("eventList is not created")

try:
    station_list = []
    with open("stationList", 'r') as sl:
        for line in sl:
            station_list.append(line.strip())

except FileNotFoundError:
    print("stationList is not created")

with open('sta_evt.out', 'w+') as output:
    for event in event_list:
        ev_dir = os.path.join(dir_path,str(event))
        evtyr, mon, day, hr, min, sec = event_time_extractor(event)
        for station in station_list:
            sac_addr = os.path.join(ev_dir,str(station)) + sac_file_extention
            if os.path.isfile(sac_addr):
                tr = obspy.read(sac_addr, debug_headers=True)
                if tr[0].stats.sac.t5 != -12345:
                    pick = tr[0].stats.sac.t5
                elif tr[0].stats.sac.t1 != -12345:
                    pick = tr[0].stats.sac.t1
                else:
                    continue
                elat = str(tr[0].stats.sac.evla)
                elon = str(tr[0].stats.sac.evlo)
                edep = str(tr[0].stats.sac.evdp / 1000)
                stnm = tr[0].stats.sac.kstnm.strip()
                slat = str(tr[0].stats.sac.stla)
                slon = str(tr[0].stats.sac.stlo)
                # sdep = str(tr[0].stats.sac.stel / 1000)
                print(station)
                sdep = elevation_grabber(station)
                time.sleep(.1)
                azim = str(tr[0].stats.sac.az)
                garc = str(tr[0].stats.sac.gcarc)
                originT = tr[0].stats.sac.o
                TT = str(pick - originT)
                pick = str(pick)
                out_str = " ".join([evtyr, mon, day, hr, min, sec, stnm, elat, elon, edep, slat, slon, sdep, azim, garc, pick, TT])
                # print(elat, elon, edep, stnm, slat, slon, sdep, azim, garc, pick, originT, TT)
                # print(out_str)
                output.write("{}\n".format(out_str))
                # del stnm, elat, elon, edep, slat, slon, sdep, azim, garc, pick, TT
