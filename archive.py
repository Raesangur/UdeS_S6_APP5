import os
import pymongo
import subprocess
import sys
import time

# Start Mongo database
dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = dbclient["UdeS_S6_APP5-archive"]
clients = db["clients"]

d = {
    "uuid": "11111111111111111",
    "name": "Petit Pascal",
    "tel" : "111-222-3333"
}

x = clients.insert_one(d)
print(x)

# Start subscriber
subscriber = subprocess.Popen(["mosquitto_sub", "-d", "-t", "hello/world"], start_new_session=True)

try:
    while(True):
        os.system("mosquitto_pub -d -t hello/world -m \"Bon matin\"")
        time.sleep(3)

# Kill process (careful its sentient)
except KeyboardInterrupt:
    print(clients)
    subscriber.kill()
    dbclient.close()
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAH FUCK IT HURTS HELP ME AAAAAAAAAAAAAAAAAH I'M JUST A PROCESS PLEASE STOP HURTING ME")
    sys.exit()
