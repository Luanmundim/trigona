import socket
import socketserver
import datetime
from html import escape
import json
import os
import traceback
import logging
from logging.handlers import TimedRotatingFileHandler

import http.server
import urllib.parse as urlparse

# Ensure the directory exists
log_directory = "/home/ubuntu/log/server"
os.makedirs(log_directory, exist_ok=True)

hostname = socket.gethostname()
log_filename = f"{log_directory}/{hostname}-server.log"

# Create a rotating log handler
log_handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=30)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Create a logger and add the log handler
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

def get_ipv6_address():
    # Get the host name
    hostname = socket.gethostname()
    # Fetch addresses associated with the host
    addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET6)
    for address in addr_info:
        # Extract the IPv6 address
        ipv6_address = address[4][0]
        return ipv6_address

def log_attempt(self, username, password, method, status_code, user_agent, destinationIP):
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

    logger.info(json.dumps(log_message, indent=4))

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
            
            log_attempt(self, '', '', 'GET', '200', user_agent, destinationIP)
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
            log_attempt(self, username, password, 'POST', status_code, user_agent, destinationIP)
        except Exception as e:
            logger.error(str(e))

if __name__ == '__main__':
    try:
        destinationIP = get_ipv6_address()
        server_address = ('::', 8080)
        httpd = IPv6Server(server_address, MyHandler)
        print(f'''Server running on http://[{destinationIP}]:8080''')
        logger.info(f"Server starts at {datetime.datetime.now()}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info(f"Server stops at {datetime.datetime.now()}")
        print('Server stopped')
    except Exception as e:
        logger.error(str(e))
