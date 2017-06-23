from WikiGameEngine import WikiGameEngine
import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

wk =  WikiGameEngine()

class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global wk
        (path, params) = self._parse_path()
        if path == '/crawl':
            self._set_header("text/json")
            wk.set_param(params["start"], params["end"])
            result = wk.crawl()
            self.wfile.write(result)


    def _set_header(self, type="text/plain"):
        self.send_response(200)
        self.send_header('Content-type', type)
        self.end_headers()

    def _parse_path(self):
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

def main():
    print "start"
    server_address = ('', 8090)
    httpd = HTTPServer(server_address, HTTPHandler)
    httpd.serve_forever()



if __name__ == "__main__":
    main()