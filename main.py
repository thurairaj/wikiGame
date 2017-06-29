from WikiGameEngine import WikiGameEngine
from WikiGameEngine import json
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib

memCache = {}

class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global memCache
        (path, params) = self._parse_path()
        if path == '/crawl':
            self._set_header("text/json")
            wk = WikiGameEngine(memCache)
            wk.set_param(params["start"], params["end"])
            result = wk.crawl()


        elif path == 'quick_check':
            self._set_header("text/json")
            if (params["start"], params["end"]) in memCache:
                result = {"status" : "SUCCESS",  "result" : memCache[(params["start"], params["end"])]}
            else:
                result = {"status": "ERROR", "message" : "NO_CACHE"}
            result = json.dumps(result)

        elif path == 'ping':
            result = {"status" : "SUCCESS"}
            result = json.dumps(result)

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
    server = ThreadedHTTPServer(('192.168.0.12', 8080), HTTPHandler)
    print "start server"
    server.serve_forever()
    print "server dead"


if __name__ == "__main__":
    main()