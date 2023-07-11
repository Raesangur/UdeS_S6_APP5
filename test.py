#   curl http://localhost:8000
#curl -d "espid=E1B4&uuid=864A" http://localhost:8000

import datetime
import argparse
import os
import pymongo
import subprocess
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        content = f"<html><body><h1>{message}</h1><table border='1px solid black'>"
        content += "<tr><th>espid </th> <th>uuid</th> <th>timestamp</th></tr>"
        for x in beacons.find({},{ "_id":0 ,"espid": 1, "uuid": 1, "timestamp":1}):
            espid = x["espid"][0]
            uuid = x["uuid"][0]
            timestamp = x["timestamp"]
            content += f"<tr> <td>{espid}</td> <td>{uuid}</td> <td>{timestamp}</td></tr>"
        content += "</table></body></html>"
        return content.encode("utf8")

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html("Bon matin"))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        data = self.rfile.read(int(self.headers['Content-Length']))
        data = data.decode()
        result = parse_qs(data, strict_parsing=True)
        result.update({"timestamp": datetime.datetime.now()})
        test = beacons.insert_one(result)
        print(result)
        timestampstring = str(result['timestamp'])
        timestampstring = [timestampstring.replace(" ", "_").replace(":", "-")]
        thegreatstring = "{uuid:" + str(result["uuid"]) + ",espid:" + str(result["espid"]) + ",timestamp:" + str(timestampstring) + "}"
        os.system(f"mosquitto_pub -h 192.168.0.16 -d -t beacons -m {thegreatstring}")
        
        self.wfile.write(self._html("Mise à jour'"))
        


def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = dbclient["UdeS_S6_APP5-beacons"]
    beacons = db["beacons"]
    beacons.drop()
    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)
