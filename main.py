from WikiGameEngine import WikiGameEngine
from WikiGameEngine import json
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib

memCache = {}
request_pool = {}

class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global memCache
        (path, params) = self._parse_path()
        print self.path
        if path == '/crawl':
            self._set_header("text/json")
            wk = WikiGameEngine(memCache)
            wk.set_param(params["start"], params["end"])

            if (params["start"], params["end"]) in memCache :
                result = {"status" : "SUCCESS", "result" : memCache[params["start"], params["end"]]}
            elif (params["start"], params["end"]) in request_pool:
                result = {"status": "PENDING", "message": "REQUEST_EXIST"}
            else:
                result = {"status" : "PENDING", "message" : "REQUEST_SUBMITTED"}
                request_pool[(params["start"], params["end"])] = 1

            result = json.dumps(result)
            self.wfile.write(result)
            wk.crawl()
            if (params["start"], params["end"]) in request_pool:
                del request_pool[(params["start"], params["end"])]

        elif path == '/check_result':
            print memCache
            self._set_header("text/json")
            if (params["start"], params["end"]) in memCache:
                result = {"status" : "SUCCESS",  "result" : memCache[(params["start"], params["end"])]}
            else:
                result = {"status": "PENDING", "message" : "NO_CACHE"}
            result = json.dumps(result)
            self.wfile.write(result)

        elif path == '/ping':
            result = {"status" : "SUCCESS"}
            result = json.dumps(result)
            self.wfile.write(result)

        else :
            result = {"status" : "ERROR", "message" : "PATH_INVALID"}
            result = json.dumps(result)
            self.wfile.write(result)



    def _set_header(self, type="text/plain"):
        self.send_response(200)
        self.send_header('Content-type', type)
        self.end_headers()

    def _parse_path(self):
        self.path = urllib.unquote(self.path)
        query_index = self.path.find("?")
        param_dict = {}
        if query_index < 0:
            return (self.path, param_dict)

        actual_path = self.path[:query_index]
        params = self.path[query_index+1:].split("&")

        for param in params:
            key_value  = param.split("=")
            param_dict[key_value[0]] = key_value[1]

        return (actual_path, param_dict)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    '''Threaded'''

def main():
    print "start process"
    server = ThreadedHTTPServer(('ec2-13-58-179-9.us-east-2.compute.amazonaws.com', 8080), HTTPHandler)
    print "start server"
    server.serve_forever()
    print "server dead"


if __name__ == "__main__":
    main()
