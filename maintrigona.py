import os
import random
import subprocess
import paramiko
from scp import SCPClient
import datetime

#scp -P 5000 -i ~/.ssh/id_rsa /home/ubuntu/Desktop/maintrigona.py ubuntu@34.44.250.143:/home/ubuntu/maintrigona.py
# ssh -p 5000 -i ~/.ssh/id_rsa 34.44.250.143
#gcloud compute scp --port=5000 --zone=us-central1-a --recurse /home/ubuntu/ us-central1-ipv6-instances-0:/home/ubuntu/

ip = '193.19.205.98'

# List of regions
'''#regions = ['us-west2', 'southamerica-east1', 'europe-west3', 'me-west1', 'asia-east2']'''
regions = ['us-central1']

#List of clusters and the number it will have in each region(subnet)
'''#clusters = {
#    'ipv6-control': 1,
#    'ipv6-requests': 2,
#    'ipv6-dns': 2,
#    'ipv6-lan': 1,
#    'ipv4-instances': 1
#}'''
clusters = {'ipv6-requests': 2}

networks = ['net-trigona-ipv4', 'net-trigona-ipv6']

# Function to configure the initial setup
def createInitConfig():
    # Authenticate with Google Cloud
    os.system('gcloud auth login --no-browser')
    # List the available projects
    os.system('\ngcloud projects list')
    projectID = str(input("Write your PROJECT ID: "))
    # Set the project ID
    os.system(f'gcloud config set project {projectID}')

# Function to get the list of instances
def getInstances():
    # Run the command to get the list of instances and extract the instance names and zones
    getInstances =  subprocess.Popen("gcloud compute instances list --format='value(name,zone)'", shell=True, stdout=subprocess.PIPE).stdout
    instances = getInstances.read().decode().split('\n')
    instances.pop()
    instances = [instance.split('\t') for instance in instances]
    instance_names = [instance[0] for instance in instances]
    instance_zones = [instance[1] for instance in instances]
    print(instance_names)
    print(instance_zones)
    return instance_names, instance_zones


# Function to connect to an instance
def connectToInstance():
    instances, zones = getInstances()
    print("Instances:")
    for i, instance in enumerate(instances):
        print(f"{i+1}. {instance} ({zones[i]})")
    
    choice = int(input("Choose an instance to connect to: "))
    porta = int(input("Porta: "))
    if choice >= 1 and choice <= len(instances):
        instanceName = instances[choice-1]
        zone = zones[choice-1]
        print(instanceName, zone)
        os.system(f'gcloud compute ssh {instanceName} --zone={zone} --ssh-flag="-p {porta}"')
    else:
        print("Invalid choice. Please try again.")


# Function to delete an instance
def deleteInstance():
    instances, zones = getInstances()
    print("Instances:")
    for i, instance in enumerate(instances):
        print(f"{i+1}. {instance} ({zones[i]})")
    
    choice = int(input("Choose an instance to delete: "))
    if choice >= 1 and choice <= len(instances):
        instanceName = instances[choice-1]
        zone = zones[choice-1]
        os.system(f"gcloud compute instances delete {instanceName} --zone={zone} --quiet")
        print(f"Instance {instanceName} in zone {zone} deleted successfully.")
    else:
        print("Invalid choice. Please try again.")


#Function to list the instances
def listSubnets():
    os.system('gcloud compute networks subnets list')

#Function to list the networks
def listNetworks():
        os.system('gcloud compute networks list')

#Function to list the firewall rules
def checkFirewall():
    os.system('gcloud compute firewall-rules list')



def createInstances():
    createNetwork()
    createSubnets()
    createFirewallRules()
    try:
        for region in regions:
            print(f"Creating instances in region {region}")
            for cluster, count in clusters.items():
                print(f"Creating instances in cluster {region}-{cluster}")
                for i in range(count):
                    instance_name = f"{region}-{cluster}-{i}"
                    if cluster =='ipv4-instances':
                        print(f"Creating instance {instance_name}")
                        os.system(f'''
                            gcloud compute instances create {instance_name} \
                            --zone={region}-a \
                            --machine-type=e2-small \
                            --image=debian-11-bullseye-v20230912 \
                            --image-project=debian-cloud \
                            --boot-disk-size=20 \
                            --subnet={region}-{cluster}-{networks[0]} \
                            --stack-type=IPV4_IPV6
                        ''')
                    
                    else:
                        print(f"Creating instance {instance_name}")
                        os.system(f'''
                            gcloud compute instances create {instance_name} \
                            --zone={region}-a \
                            --machine-type=e2-small \
                            --image=debian-11-bullseye-v20230912 \
                            --image-project=debian-cloud \
                            --boot-disk-size=20 \
                            --subnet={region}-{cluster}-{networks[1]} \
                            --stack-type=IPV4_IPV6
                        ''')
                    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return



#Function to create a network
def createNetwork():
    for network in networks:
        try:
            print(f"Creating network {network}")
            os.system(f'''
            gcloud compute networks create {network} \
            --subnet-mode=custom \
            --enable-ula-internal-ipv6 \
            --bgp-routing-mode=regional''')
        except Exception as e:
            print(f"An error occurred: {str(e)}")


def createSubnets():
    try:
        for region in regions:
            print(f"Creating subnets for region {region}")
            for cluster in clusters:
                print(f"Creating subnets for cluster {cluster}")
                for network in networks:
                    print(f"Creating subnet for network {network}")
                    os.system(f'''
                    gcloud compute networks subnets create {region}-{cluster}-{network} \
                    --network={network} \
                    --range=10.0.0.0/20 \
                    --stack-type=IPV4_IPV6 \
                    --ipv6-access-type=EXTERNAL \
                    --region={region}
                    ''')
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def createFirewallRules():
    try:
        print("Creating firewall rules")
        os.system(f'''
        gcloud compute firewall-rules create {networks[0]}-allow-ipv4\
        --network {networks[0]}\
        --priority 1000 \
        --direction ingress \
        --action allow \
        --rules=tcp:22,tcp:80,tcp:443,tcp:5432,tcp:161,tcp:110,tcp:23,tcp:5000 \
        --source-ranges 0.0.0.0/0''')

        os.system(f'''
        gcloud compute firewall-rules create {networks[1]}-allow-ipv6\
        --network {networks[1]} \
        --priority 1000 \
        --direction ingress \
        --action allow \
        --rules=tcp:22,tcp:80,tcp:443,tcp:5432,tcp:161,tcp:110,tcp:23 \
        --source-ranges 0::/0''')

        os.system(f'''
        gcloud compute firewall-rules create {networks[1]}-allow-ipv4\
        --network {networks[1]}\
        --priority 1000 \
        --direction ingress \
        --action allow \
        --rules=tcp:2222 \
        --source-ranges {ip}''')

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        


def configureInstance():
    try:
        instances, zones = getInstances()
        for instanceName, zone in zip(instances, zones):
            print(f"Configuring instance {instanceName}")
            '''os.system(f"gcloud compute ssh {instanceName} --zone={zone} --command='sudo apt-get remove --purge man-db -y'")#consume too much time in the update process
            os.system(f"gcloud compute ssh {instanceName} --zone={zone} --command='sudo apt-get update -y'")
            os.system(f"gcloud compute ssh {instanceName} --zone={zone} --command='sudo apt-get upgrade -y'")
            os.system(f"gcloud compute ssh {instanceName} --zone={zone} --command='sudo sed -i '/^#Port 22/c\Port 5000' /etc/ssh/sshd_config && sudo systemctl restart sshd'")

            os.system(f'gcloud compute ssh {instanceName} --zone={zone} --ssh-flag="-p 5000" --command="sudo apt-get install docker.io -y"')

            os.system(f'gcloud compute ssh {instanceName} --zone={zone} --ssh-flag="-p 5000" --command="sudo docker pull luantmundim/trigona:2.0"')'''

            os.system (f'gcloud compute ssh {instanceName} --zone={zone} --ssh-flag="-p 5000" --command="sudo docker run -d -t -p [::]:23:2223 -p [::]:22:2222 -p [::]:110:110 -p [::]:143:143 -p [::]:161:161 -p [::]:443:443 -p [::]:5432:5432 -p [::]:80:80 --hostname {instanceName} --name trigona luantmundim/trigona:2.0"')

            #os.system(f'gcloud compute ssh {instanceName} --zone={zone} --ssh-flag="-p 5000" --command="sudo docker stop trigona"')
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return

def modifyservices(command):
    try:
        instances, zones = getInstances()
        for instanceName, zone in zip(instances, zones):
            print(f"Starting instance {instanceName}")
            os.system(f'gcloud compute ssh {instanceName} --zone="{zone}" --ssh-flag="-p 5000" --command="sudo docker {command} trigona"')
            os.system(f'gcloud compute ssh {instanceName} --zone={zone} --ssh-flag="-p 5000" --command="sudo docker exec --user cowrie trigona /home/cowrie/cowrie/bin/cowrie {command}"')

            os.system(f'gcloud compute ssh {instanceName} --zone={zone} --ssh-flag="-p 5000" --command="sudo docker exec trigona /bin/bash -c "cd /home/scripts/qeeqbox/ && ./screen-qeeqbox-{command}.sh""')

            os.system(f'gcloud compute ssh {instanceName} --zone={zone} --ssh-flag="-p 5000" --command="sudo docker exec trigona /bin/bash -c "cd /home/scripts/tcpdump/ && ./screen-tcpdump-{command}.sh""')
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return


def modifyTrigona(command):
    try:
        instances, zones = getInstances()
        for instanceName, zone in zip(instances, zones):
            print(f"Starting instance {instanceName}")
            os.system(f'gcloud compute ssh {instanceName} --zone="{zone}" --ssh-flag="-p 5000" --command="sudo docker {command} trigona"')

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return


def generateAndSendSSHKeys():
    # Generate SSH keys
    os.system('ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""')
    
    # Send public key to gcloud for authentication
    os.system('gcloud compute os-login ssh-keys add --key-file ~/.ssh/id_rsa.pub')


def updateFirewallRules():
    # List all firewall rules
    os.system('gcloud compute firewall-rules list')
    
    # Prompt user to choose a firewall rule to update
    rule_name = input("Enter the name of the firewall rule to update: ")
    
    # Prompt user to enter their IPv4 address
    ipv4_address = input("Enter your IPv4 address: ")
    
    # Update the firewall rule with the user's IPv4 address
    os.system(f'gcloud compute firewall-rules update {rule_name} --source-ranges {ipv4_address}')


def updateCrontab():
    try:
        instances, zones = getInstances()
        for instanceName, zone in zip(instances, zones):
            os.system(f'gcloud compute ssh {instanceName} --zone="{zone}" --ssh-flag="-p 5000" --command="(crontab -l 2>/dev/null; echo \"* * * * * ls > log.txt\") | crontab -"')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return

def stopCrontab():
    try:
        instances, zones = getInstances()
        for instanceName, zone in zip(instances, zones):
            os.system(f'gcloud compute ssh {instanceName} --zone={zone} --ssh-flag="-p 5000" --command="(crontab -l 2>/dev/null | sed \'s/^/#/\') | crontab -"')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return

def scpToInstances():
    instances, zones = getInstances()
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_directory = f"log-{instance}-{current_datetime}"
    os.makedirs(log_directory)
    for instance, zone in zip(instances, zones):
        ipv4_address = subprocess.Popen(f"gcloud compute instances describe {instance} --zone={zone} --format='value(networkInterfaces[0].accessConfigs[0].natIP)'", shell=True, stdout=subprocess.PIPE).stdout
        ipv4_address = ipv4_address.read().decode().strip()
        os.system(f'scp -r -P 5000 -i ~/.ssh/id_rsa -o "StrictHostKeyChecking=no" ubuntu@{ipv4_address}:/home/ubuntu /home/ubuntu/Desktop/mestrado/log/{log_directory}')

def sendoFilestoInstance():
    instances, zones = getInstances()
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #log_directory = f"log-{instance}-{current_datetime}"
    #os.makedirs(log_directory)
    for instance, zone in zip(instances, zones):
        ipv4_address = subprocess.Popen(f"gcloud compute instances describe {instance} --zone={zone} --format='value(networkInterfaces[0].accessConfigs[0].natIP)'", shell=True, stdout=subprocess.PIPE).stdout
        ipv4_address = ipv4_address.read().decode().strip()
        os.system(f'scp -r -P 5000 -i ~/.ssh/id_rsa -o "StrictHostKeyChecking=no" //home/ubuntu/Desktop/mestrado/trigonadocker ubuntu@{ipv4_address}:/home/ubuntu')

def wgetIpv6Lan():
    instances, zones = getInstances()
    ipv6LanInstances = [instance for instance, zone in zip(instances, zones) if 'ipv6-lan' in instance]
    for instance, zone in zip(ipv6LanInstances, zones):
        os.system(f'gcloud compute ssh {instance} --zone={zone} --ssh-flag="-p 5000" --command="for i in $(gcloud compute instances list --filter=name=ipv6-lan --format=\'value(networkInterfaces[0].networkIP)\') ; do wget -6 http://$i:80 ; done"')

#Function to open the main menu
def run():
    print("\nWelcome to Trigona!\n Here we are going to have some fun discovering the wonderful world of clouds and honey!!\n" + 
    "\n1. Create initial configuration" +
    "\n2. List the instances" +
    "\n3. List the networks" +
    "\n4. List the subnets" +
    "\n5. List the firewall rules" +
    "\n6. Create Network, Subnets, Firewall rules and Instances" +
    "\n7. Configure Instances"
    "\n8. Configure firewall rules for IPv4 address"
    "\n9. SSH to an instance"
    "\n10. Modify Trigona (start|stop)"
    "\n11. Modify services (start|stop)"
    "\n12. Update firewall rules for IPv4 address"
    "\n13. Generate and send SSH keys to gcloud"
    "\n14. Update crontab for all instances"
    "\n15. Stop crontab for all instances"
    "\n16. SCP to instances"
    "\n17. send files to instances"
    "\n99. Delete an instance" +
    "\n100. Exit\n"
    )
    option = int(input("Choose an option: "))

    while option != 100:
        if option == 1:
            createInitConfig()
        elif option == 2:
            getInstances()
        elif option == 3:
            listNetworks()
        elif option == 4:
            listSubnets()
        elif option == 5:
            checkFirewall()
        elif option == 6:
            createInstances()
        elif option == 7:
            configureInstance()
        elif option == 8:
            createFirewallRules()
        elif option == 9:
            connectToInstance()
        elif option == 10:
            modifyTrigona(input("Type the command to start or stop the Trigona container (start|stop): "))
        elif option == 11:
            modifyservices(input("Type the command to start or stop the services (start|stop): "))
        elif option == 12:
            updateFirewallRules()
        elif option == 13:
            generateAndSendSSHKeys()
        elif option == 14:
            updateCrontab()
        elif option == 15:
            stopCrontab()
        elif option == 16:
            scpToInstances()
        elif option == 17:
            sendoFilestoInstance()
        elif option == 99:
            deleteInstance()
        elif option == 100:
            print("Bye Bye!")
        else:
            print("Invalid option, please try again.")

        run()
        option = int(input("Choose an option: "))
    exit()

if __name__ == "__main__":
    run()


'''command = 'docker ps -a'
getInstances =  subprocess.Popen("gcloud compute instances list | awk '{print $1}' | grep -v 'NAME'", shell=True, stdout=subprocess.PIPE).stdout
instances = getInstances.read().decode().split('\n')
instances.pop()
for i, instance in enumerate(instances):
    print(f"{i+1}. {instance}")
    zone = subprocess.Popen(f"gcloud compute instances list --filter=name={instance} --format='value(zone)'", shell=True, stdout=subprocess.PIPE).stdout
    zone = zone.read().decode().strip()
    if zone is not None:
        print(f"{i+1}. {instance} ({zone})")
        os.system(f'echo adminluan | gcloud compute ssh {instance} --zone="{zone}" --ssh-flag="-p 5000" --command="{command}"')'''
