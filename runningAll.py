import os
import logging
from datetime import datetime
import socket
from time import sleep
import random

def start_service(status, service, delay, privilege =''):
    # Change directory to /home/ubuntu/trigona/service/
    os.chdir(f'/home/ubuntu/trigona/{service}/')

    # Configure logging
    current_day = datetime.now().strftime("%Y-%m-%d")
    hostname = socket.gethostname()
    log_file = f'/home/ubuntu/trigona/log/{service}/{hostname}-{current_day}-logging-{service}.log'
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Run ./config-service.sh start
    os.system(f'cd /home/ubuntu/trigona/{service} && echo "{privilege}./config-{service}.sh {status}" | at now + {delay} minutes')
    logging.info(f'Started {service} with status: {status}')


def start_cowrie(status, service):
    # Change directory to /home/ubuntu/trigona/service/
    os.chdir(f'/home/cowrie/{service}/')

    # Configure logging
    current_day = datetime.now().strftime("%Y-%m-%d")
    hostname = socket.gethostname()
    log_file = f'/home/ubuntu/trigona/log/{service}/{hostname}-{current_day}-logging-{service}.log'
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Run ./config-service.sh start
    os.system(f'cd /home/ubuntu/trigona/cowrie/{service} && sudo su cowrie./bin/{service} {status}')
    logging.info(f'Started {service} with status: {status}')


def generate_number():
    return random.randint(2, 12*58)

if __name__ == '__main__':
    start_service('start', 'tcpdump', 1, 'sudo ')#must be the firtst one to start
    sleep(1)
    start_service('start', 'server', 1, 'sudo ')
    sleep(1)
    start_service('start', 'serverHTTPS', 1, 'sudo ')
    sleep(1)
    start_cowrie('start', 'cowrie')
    sleep(1)


    if ('crawler' in socket.gethostname()):
        start_service('start', 'crawler', generate_number())
        sleep(1)
    if ('dns' in socket.gethostname()):
        start_service('start', 'DNS', generate_number())
        sleep(1)
    if ('request' in socket.gethostname()):
        start_service('start', 'request', generate_number())
        sleep(1)
