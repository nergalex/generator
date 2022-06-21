from http.server import BaseHTTPRequestHandler, HTTPServer
from routes.main import get_routes, post_routes
import cgi
import requests
import os
import logging
import time
import json

from random import randint

# Get Env vars
try:
    PREFIX = os.environ.get('PREFIX')
    if type(PREFIX)== type(None) :
        PREFIX = ""
except:
    PREFIX = ""
try:
    NAMESPACE = os.environ.get('NAMESPACE')
    if type(NAMESPACE) == type(None) :
        NAMESPACE = ""
except:
    NAMESPACE = ""
try:
    SITE_ENV = os.environ.get('SITE_ENV')
    if type(SITE_ENV) == type(None) :
        SITE_ENV = ""
except:
    SITE_ENV = ""
try:
    SITE_ENV_MESSAGE = os.environ.get('SITE_ENV_MESSAGE')
    if type(SITE_ENV_MESSAGE) == type(None) :
        SITE_ENV_MESSAGE = ""
except:
    SITE_ENV_MESSAGE = ""

class Server(BaseHTTPRequestHandler):

    # Handle Head  
    def do_HEAD(self):
        logging.info("HEAD request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        return
        
    # Handle GET
    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        
        status = 200
        content_type = "text/plain"
        response_content = ""

        routes = get_routes
        
        if self.path in routes:
            print(routes[self.path])
            match routes[self.path]:
                case "health":
                    response_content = "health OK\n"
                case "sentence":
                    content_type = 'application/json'
                    response_content = json.dumps(get_sentence())
                case _:
                    content_type = 'application/json'
                    response_content = json.dumps(get_words(routes[self.path]))
        else:
            status = 404
            content_type = "text/plain"
            response_content = "404 not found"
        
        # Append Env vars
        if SITE_ENV != "":
            test = json.loads(response_content)
            test.update({"env" : SITE_ENV})
            print(test)

        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.respond(bytes(response_content, "UTF-8"))
        return
           

    # POST echoes the message adding a JSON field
    def do_POST(self):

        ctype, _ = cgi.parse_header(self.headers['content-type'])
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\nBody:\n%s\n", str(self.path), str(self.headers), post_data.decode('utf-8'))

        status = 200
        content_type = 'application/json'
        response_content = ""
        # read the message and convert it into a python dictionary
        message = json.loads(post_data)

        routes = post_routes

        if self.path in routes and "value" in message:
             # refuse to receive non-json content
            if ctype != 'application/json':
                self.send_response(400)
                self.end_headers()
                return
            
            successful, info = post_word(routes[self.path], message["value"])
            if successful:
                message['accepted'] = "true"
                message['info'] = info
                response_content = json.dumps(message)
            else:
                status = 400
                message['accepted'] = "false"
                message['info'] = info
                response_content = json.dumps(message)
            # match routes[self.path]:
            #     case "adjectives":
            #         successful, info = post_word("adjectives", message["value"])
            #         if successful:
            #             message['accepted'] = "true"
            #             message['info'] = info
            #             response_content = json.dumps(message)
            #         else:
            #             status = 400
            #             message['accepted'] = "false"
            #             message['info'] = info
            #             response_content = json.dumps(message)
            #     case "animals":
            #         successful, info = post_word("animals", message["value"])
            #         if successful:
            #             message['accepted'] = "true"
            #             message['info'] = info
            #             response_content = json.dumps(message)
            #         else:
            #             status = 400
            #             message['accepted'] = "false"
            #             message['info'] = info
            #             response_content = json.dumps(message)
            #     case "colors":
            #         successful, info = post_word("animals", message["value"])
            #         if successful:
            #             message['accepted'] = "true"
            #             message['info'] = info
            #             response_content = json.dumps(message)
            #         else:
            #             status = 400
            #             message['accepted'] = "false"
            #             message['info'] = info
            #             response_content = json.dumps(message)
            #     case "locations":
            #         successful, info = post_word("adjectives", message["value"])
            #         if successful:
            #             message['accepted'] = "true"
            #             message['info'] = info
            #             response_content = json.dumps(message)
            #         else:
            #             status = 400
            #             message['accepted'] = "false"
            #             message['info'] = info
            #             response_content = json.dumps(message)
            #     case _:
            #         print("method not allowed")
            #         status = 405
            #         content_type = "text/plain"
            #         response_content = "405 " + self.command + " not allowed" 
        else:
            status = 404
            content_type = "text/plain"
            response_content = "404 not found"                
                
        # send the message back
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.respond(bytes(response_content, "UTF-8"))
        return
    
    def respond(self, content):
        self.wfile.write(content)
        print("Responded")
        return


def get_sentence():
    generated_name = {}
    attributes_list = ['adjectives', 'animals', 'colors', 'locations']
    for attribute in attributes_list:
        words = get_words(attribute)
        print(words)
        words_size = len(words)
        #print(str(words_size))
        if words_size == 0 : #error api_size
            generated_name[attribute] = "null"
        else:
            index = randint(0, words_size-1)
            #print(index)
            name = words[index]['name']
            generated_name[attribute] = name
    return generated_name

def get_words(attribute):
    content_type = 'application/json'

    uri = 'http://' + PREFIX + '-' + attribute + '.' + NAMESPACE + '/' + attribute

    headers = {
        'content-type': content_type,
    }

    try:
        response = requests.get(uri, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        return []
    
    if (response.status_code >= 200 and response.status_code <= 299):
        print(uri + ' Accepted')

        print('Response: ' + str(response))
        return response.json()
    else:
        print(uri + ' not accepted')
        print("Response code: {}".format(response.status_code))
        print('Response: ' + str(response))
        return {}

def get_word(attribute, index = None, query = None):
    
    content_type = 'application/json'
    
    if(index is not None and query is not None):
        raise ValueError("should have index or query, but not both")
    elif (index is not None):
        uri = 'http://' + PREFIX + '-' + attribute + '.' + NAMESPACE + '/' + attribute + '/' + str(index)
    elif (query is not None):
        uri = 'http://' + PREFIX + '-' + attribute + '.' + NAMESPACE + '/' + attribute + '?q=' + query

    headers = {
        'content-type': content_type,
    }
    print("index " + str(index))

    try:
        response = requests.get(uri, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        return []

    if (response.status_code >= 200 and response.status_code <= 299):
        print(uri + ' Accepted')
        print('Response: ' + str(response))
        json_data = response.json()
        print(str(json_data))
    else:
        print("Response code: {}".format(response.status_code))
    return response.json()

def post_word(attribute, value):

    # Find if duplicate exists
    word = get_word(attribute, query=value)

    if (len(word) != 0): #word exists
        print(value + " Exists in " + str(word))
        return (False, "Error: " + value + " already exists")

    uri = 'http://' + PREFIX + '-' + attribute + '.' + NAMESPACE + '/' + attribute

    headers = {
        'content-type': 'application/json'
    }

    data = {
        'name': value
    }

    try:
        response = requests.post(uri, data=json.dumps(data), headers=headers)
    except requests.exceptions.RequestException as e:
        print(e.response)
        return (False, str(e)) 
    
    if (response.status_code >= 200 and response.status_code <= 299):
        print(uri + ' Accepted')

        print('Response: ' + str(response))

        return (True, "")
    else:
        print("Response code: {}".format(response.status_code))
        return (False, "Response code: {}".format(response.status_code))
    

def run(server_class=HTTPServer, handler_class=Server, port=8080, hostname=''):
    server_address = ('', port)
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
