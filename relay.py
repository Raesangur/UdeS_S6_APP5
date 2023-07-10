import json
import os
import pymongo
import subprocess
import sys
import time

# Start subscriber
subscriber = subprocess.Popen(["mosquitto_sub", "-d", "-t", "beacons", "-h", "192.168.0.16"], start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = dbclient["UdeS_S6_APP5-relay"]
beacons = db["beacons"]

try:
    while(True):
        for line in iter(subscriber.stdout.readline, ''):
            line = line.decode().replace('\n', '')
            if '[' in line:
                line = line.replace('{', "{\"").replace('}', "\"}").replace(':', "\":\"").replace(',', "\",\"")
                #print(line)
                data = json.loads(line)
                print(data)
                print(data["uuid"])
                beacons["data"].insert_one(line)
            
        time.sleep(3)

# Kill process (careful its sentient)
except:
    print("REEEEEEEEEEEE")
    subscriber.kill()
    sys.exit()
