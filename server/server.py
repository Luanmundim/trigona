import socket
import socketserver
import datetime
from html import escape
import json
import os
import ssl
import subprocess
import traceback
import logging
from logging.handlers import RotatingFileHandler

import http.server
import urllib.parse as urlparse

# Ensure the directory exists
log_directory = "/home/ubuntu/log/serverHTTPS"
os.makedirs(log_directory, exist_ok=True)

hostname = socket.gethostname()
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d")
log_filename = f"{log_directory}/{hostname}-{current_datetime}-serverHTTPS.log"

# Configure logging
logger = logging.getLogger("serverHTTPS")
logger.setLevel(logging.INFO)

# Create a rotating file handler
handler = RotatingFileHandler(log_filename, maxBytes=1024*1024, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def get_ipv6_address():
    # Get the host name
    hostname = socket.gethostname()
    # Fetch addresses associated with the host
    addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET6)
    for address in addr_info:
        # Extract the IPv6 address
        ipv6_address = address[4][0]
        return ipv6_address

def log_attempt(self, username, password, method, status_code, user_agent):
    timestamp = datetime.datetime.now()
    log_message = {
        "Username": escape(username),
        "Password": escape(password),
        "Method": method,
        "User-Agent": user_agent,
        "Status Code": status_code,
        "Origin IP": self.client_address[0],
        "Destination IP": destinationIP,
        "Origin Port": self.client_address[1],
        "Destination Port": self.server.server_address[1],
        "URL": self.path,
        "Timestamp": str(timestamp)
    }
    logger.info(json.dumps(log_message))

class IPv6Server(socketserver.TCPServer):
    address_family = socket.AF_INET6

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            html = f"""
            <html>
            <body>
                <form action="/" method="post">
                    Username: <input name="username" type="text"><br>
                    Password: <input name="password" type="password"><br>
                    <input type="submit" value="Login">
                </form>
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            user_agent = self.headers.get('User-Agent')
            
            log_attempt(self, '', '', 'GET', '200', user_agent)
        except Exception as e:
            logger.error(str(e))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = urlparse.parse_qs(post_data.decode('utf-8'))
        username = data.get('username', [''])[0]
        password = data.get('password', [''])[0]
        
        message = "Incorrect username or password"

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
        user_agent = self.headers.get('User-Agent')
        status_code = '200'

        try:
            log_attempt(self, username, password, 'POST', status_code, user_agent)
        except Exception as e:
            logger.error(str(e))

if __name__ == '__main__':
    try:
        destinationIP = get_ipv6_address()
        server_address = ('::', 4443)
        httpd = IPv6Server(server_address, MyHandler)
        
        # Create an SSL context
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile='cert.pem', keyfile='key.pem', password='adminluan')
        
        # Wrap the HTTP server in SSL using the SSL context
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        print(f'''Server running on https://[{destinationIP}]:4443''')
        logger.info('Server starts')
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Server stops')
        print('Server stopped')
    except Exception as e:
        logger.error(str(e))
