from obspy import read
import os


def output_strip(i_bytes):
    if not isinstance(i_bytes, bytes):
        return i_bytes
    # get byte input and decode into utf-8 and omit space and newline
    decoded = i_bytes.decode('utf-8')
    return decoded.strip()


eventList = os.listdir("./")
with open('stationList', 'r') as sta:
    stationList = sta.readlines()

for i in range(len(stationList)):
    stationList[i] = stationList[i].strip()


for event in eventList:
    if event[0] != 'E':
        # drop them from the list
        print(event)
