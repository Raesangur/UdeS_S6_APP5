#   curl http://localhost:8000
#curl -d "espid=E1B4&uuid=864A" http://localhost:8000

import datetime
import argparse
import pymongo
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        content = f"<html><body><h1>{message}</h1><table border='1px solid black'>"
        content += "<tr><th>User </th> <th>Phone </th> <th>espid</th> <th>Last seen timestamp</th></tr>"
        for x in beacons.find():
            x = list(x.values())[1]
            print(x)
            
            user = x["name"]
            phone = x["phone"]
            espid = x["espid"]
            timestamp = x["timestamp"]
            
            content += f"<tr> <td>{user}</td> <td>{phone}</td> <th>{espid}</th> <td>{timestamp}</td></tr>"
        content += "</table></body></html>"
        return content.encode("utf8")

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html("Interface web cool pour l'archivage des derniers timestamps ou un utilisateur a ete vu"))

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

        
        self.wfile.write(self._html("Mise à jour'"))
        


def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()


try:
    if __name__ == "__main__":
        dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
        db = dbclient["UdeS_S6_APP5-relay"]
        beacons = db["users"]
        #beacons.drop()
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
except KeyboardInterrupt:
    dbclient.close()
    sys.exit()
