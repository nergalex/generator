from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse
import cgi
import requests
import os
import logging
import time


from random import seed
from random import randint


class Server(BaseHTTPRequestHandler):

    # Set JSON headers
    def _set_json_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    
    def _set_text_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    # Handle Head  
    def do_HEAD(self):
        logging.info("HEAD request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_json_headers()
        
    # Handle GET
    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        
        # get Health
        if self.path == "/health":
            self._set_text_headers()
            self.wfile.write(bytes("health OK", encoding='utf8'))

        # get Sentence 
        elif self.path == "/api/sentence":
            self._set_json_headers()
            generated_name = name_generator()
            self.wfile.write(bytes(json.dumps(generated_name), encoding='utf8'))           
        
        # else 404
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes("404 not found", encoding='utf8'))

    # POST echoes the message adding a JSON field
    def do_POST(self):
        print(self.headers)
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\nBody:\n%s\n", str(self.path), str(self.headers), post_data.decode('utf-8'))

        # read the message and convert it into a python dictionary
        message = json.loads(post_data)

        # add a property to the object, just to mess with data
        #message['received'] = 'ok'

        targetService = message['service']

        print(message['service'])
        print(message['value'])
        
        # send the message back
        self._set_json_headers()
        self.wfile.write(json.dumps(message).encode(encoding='utf_8'))
        #self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

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
        print('Size: ' + str(list_size))

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

def run(server_class=HTTPServer, handler_class=Server, port=80, hostname='localhost'):
    server_address = (hostname, port)
    httpd = server_class(server_address, handler_class)
    logging.basicConfig(level=logging.INFO)

    print(time.asctime(), 'Server UP - %s:%s' % (hostname, port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - %s:%s' % (hostname, port))
    
if __name__ == "__main__":
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
