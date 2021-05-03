import requests
import os
import json


if not os.path.isdir('./PZs'):
    os.mkdir('./PZs')


try:
    home_dir = os.getcwd()
    station_list = []
    with open("stationList", 'r') as sl:
        for line in sl:
            if not line:
                pass
            else:
                station_list.append(line.strip())
except FileNotFoundError:
    print("eventList and/or stationList is not created")

print(station_list)

req_add = 'http://service.iris.edu/irisws/sacpz/1/query?net=BX&sta=STATION&loc=*&cha=CHANNEL&starttime=2001-01-01T00:00:00&endtime=2021-05-02T23:59:59&nodata=404'

for sta in station_list:
    specific_req_add = req_add.replace('STATION', sta)
    specific_req_add = specific_req_add.replace('CHANNEL', 'BHE')

    print(specific_req_add)
    resp_sta = requests.get(specific_req_add)
    # print(resp_sta.text)
    with open(f'PZs/SAC_PZs_BX_{sta}_BHE.SAC', 'w') as f:
        f.write(resp_sta.text)
    specific_req_add = specific_req_add.replace('BHE', 'BHN')

    print(specific_req_add)
    resp_sta = requests.get(specific_req_add)
    # print(resp_sta.text)
    with open(f'PZs/SAC_PZs_BX_{sta}_BHN.SAC', 'w') as f:
        f.write(resp_sta.text)
