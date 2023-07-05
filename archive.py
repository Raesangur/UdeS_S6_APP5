import os
import subprocess
import sys
import time

subscriber = subprocess.Popen(["mosquitto_sub", "-d", "-t", "hello/world"], start_new_session=True)

try:
    while(True):
        os.system("mosquitto_pub -d -t hello/world -m \"Bon matin\"")
        time.sleep(3)
        
except KeyboardInterrupt:
    subscriber.kill()
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAH FUCK IT HURTS HELP ME AAAAAAAAAAAAAAAAAH I'M JUST A PROCESS PLEASE STOP HURTING ME")
    sys.exit()
