import socket
import socketserver
import datetime
from html import escape
import json
import os
import traceback
import http.server
import urllib.parse as urlparse

# Ensure the directory exists
log_directory = "/home/ubuntu/log/server"
os.makedirs(log_directory, exist_ok=True)

def get_ipv6_address():
    # Get the host name
    hostname = socket.gethostname()
    # Fetch addresses associated with the host
    addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET6)
    for address in addr_info:
        # Extract the IPv6 address
        ipv6_address = address[4][0]
        return ipv6_address


def create_log_files():
    hostname = socket.gethostname()
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d")
    log_filename = f"{log_directory}/{hostname}-{current_datetime}-server.log"
    json_filename = f"{log_directory}/{hostname}-{current_datetime}-server.json"
    errors_filename = f"{log_directory}/{hostname}-{current_datetime}-errors.log"

    if not os.path.exists(log_filename):
        with open(log_filename, 'w') as file:
            json.dump([], file)
        print(f"Log file {log_filename} created.")

    if not os.path.exists(json_filename):
        with open(json_filename, 'w') as file:
            json.dump([], file)
        print(f"JSON file {json_filename} created.")
    
    if not os.path.exists(errors_filename):
        with open(errors_filename, 'w') as file:
            json.dump([], file)
        print(f"Errors file {errors_filename} created.")

# Call the function before using the log_attempt and write_server_log functions


def write_server_log(condition):
    timestamp = datetime.datetime.now()
    log_message = {
        "Event": f"Server {condition}",
        "Timestamp": str(timestamp)
    }

    hostname = socket.gethostname()
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{log_directory}/{hostname}-{current_datetime}-server.log"
    with open(filename, 'r+') as file:
        logs = json.load(file)
        logs.append(log_message)
        file.seek(0)
        json.dump(logs, file, indent=4)
        file.truncate()
        print(f"Server log saved in {filename}")


def log_error(error_message):
    timestamp = datetime.datetime.now()
    log_message = {
        "Event": "Error",
        "Timestamp": str(timestamp),
        "Error Message": error_message,
        "Line": traceback.format_exc().splitlines()[-1]
    }
    hostname = socket.gethostname()
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{log_directory}/{hostname}-{current_datetime}-errors.log"
    with open(filename, 'r+') as file:
        logs = json.load(file)
        logs.append(log_message)
        file.seek(0)
        json.dump(logs, file, indent=4)
        file.truncate()
        print(f"Error logged in {filename}")


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

    hostname = socket.gethostname()
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{log_directory}/{hostname}-{current_datetime}-server.json"
    with open(filename, 'r+') as file:
        logs = json.load(file)
        logs.append(log_message)
        file.seek(0)
        json.dump(logs, file, indent=4)
        file.truncate()
        print(f"Log saved in {filename}")


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
            log_error(str(e))

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
            log_error(str(e))


if __name__ == '__main__':
    try:
        create_log_files()
        destinationIP = get_ipv6_address()
        server_address = ('::', 8080)
        httpd = IPv6Server(server_address, MyHandler)
        print(f'''Server running on http://[{destinationIP}]:8080''')
        write_server_log('starts')
        httpd.serve_forever()
    except KeyboardInterrupt:
        write_server_log('stops')
        print('Server stopped')
    except Exception as e:
        log_error(str(e))

