from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse
import cgi
import requests


from random import seed
from random import randint


class Server(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    # GET sends back a Hello world message
    def do_GET(self):
        parsed_path = urlparse(self.path)
        print(parsed_path)
        self._set_headers()
        if self.path == "/health":
            self.wfile.write(bytes("health OK", encoding='utf8'))            
        else:
            generated_name = name_generator()
            self.wfile.write(bytes(json.dumps(generated_name), encoding='utf8'))

    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))
        
        # add a property to the object, just to mess with data
        message['received'] = 'ok'
        
        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(message))

def name_generator():
    try:
        PREFIX = os.environ.get('PREFIX')
    except:
        PREFIX = ""
    try:
        NAMESPACE = os.environ.get('NAMESPACE')
    except:
        NAMESPACE = ""
    generated_name = {}
    attributes_list = ['adjectives', 'animals', 'colors', 'locations']
    for attribute in attributes_list:
        api_size = get_index(PREFIX, NAMESPACE, attribute)
        if api_size == 0 : #error api_size
            generated_name[attribute] = "null"
        else:
            index = randint(1, api_size)
            name = get_data(PREFIX, NAMESPACE, attribute, index)
            generated_name[attribute] = name
    return generated_name

def get_index(prefix ,ns, attribute):
    content_type = 'application/json'

    uri = 'http://' + prefix + '-' + attribute + '.' + ns + '/' + attribute

    headers = {
        'content-type': content_type,
    }

    try:
        response = requests.get(uri, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        return 0
    
    if (response.status_code >= 200 and response.status_code <= 299):
        print(uri + 'Accepted')

        print('Response: ' + str(response))
        json_data = response.json()
        print(json.dumps(json_data))
        list_size = len(json_data)	
        print('Size: ' + list_size)

    else:
        print("Response code: {}".format(response.status_code))
    return list_size

def get_data(prefix, ns, attribute, index):
    method = 'GET'
    content_type = 'application/json'
    resource = '/'+ attribute
    #content_length = len(body)
    uri = 'http://' + prefix + '-' + attribute + '.' + ns + '/' + attribute + '/' + str(index)

    headers = {
        'content-type': content_type,
    }
    print("index " + str(index))
    response = requests.get(uri, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print('Accepted')
        print('Response: ' + str(response))
        json_data = response.json()
        print(str(json_data))
        name = json_data['name']
        print('Name: ' + name)
    else:
        print("Response code: {}".format(response.status_code))
    return name        

def run(server_class=HTTPServer, handler_class=Server, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    print('Starting httpd on port %d...' % port)
    httpd.serve_forever()
    
if __name__ == "__main__":
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
