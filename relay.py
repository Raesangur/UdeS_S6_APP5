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
users = db["users"]
users.drop()

x = [
        {"[0000febe-0000-1000-8000-00805f9b34fb]": {
            "name": "Pascal-Emmanuel Lachance",
            "phone": "123-456-7890",
            "espid": "0000",
            "timestamp": "0000"
        }},
        {"[0000fe9f-0000-1000-8000-00805f9b34fb]":
        {
            "name": "Philippe Gauthier",
            "phone": "098-765-4321",
            "espid": "0000",
            "timestamp": "0000"
        }}
]

users.insert_many(x)


try:
    while(True):
        for line in iter(subscriber.stdout.readline, ''):
            line = line.decode().replace('\n', '')
            if '[' in line:
                line = line.replace('{', "{\"").replace('}', "\"}").replace(':', "\":\"").replace(',', "\",\"")
                data = json.loads(line)
                uuid = data["uuid"]
                #print(data)
                
                for x in users.find({},{ "_id": 0, uuid: 1}):
                    if not bool(x):
                        continue

                    y = x[uuid]
                    y["timestamp"] = data["timestamp"]
                    y["espid"] = data["espid"]

                    #y = {data["uuid"]:y}
                    
                    users.find_one_and_update({uuid: {'$exists': True}}, {"$set": {uuid : y}}, upsert=False)

                for x in users.find({},{ "_id": 0, uuid: 1}):
                    if not bool(x):
                        continue
                    
                    print (x)
                    

except Exception as e:
    print("REEEEEEEEEEEE")
    print(str(e))
    subscriber.kill()
    dbclient.close()
    sys.exit()
