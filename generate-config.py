#! /usr/bin/env python3
from datetime import datetime
from getpass import getpass

from environs import Env, EnvError
from pick import pick

from piawg import piawg

pia = piawg()
env = Env()

# Generate public and private key pair
pia.generate_keys()

# Select region
title = 'Please choose a region: '
options = sorted(list(pia.server_list.keys()))
option, index = pick(options, title)
pia.set_region(option)
print("Selected '{}'".format(option))

# Get token
while True:
    # Attempt to get username/password via env var, fallback to user prompt if not set
    try:
        username = env("PIA_USERNAME")
    except EnvError:
        print("PIA_USERNAME env var not set, falling back to user input...")
        username = input("\nEnter PIA username: ")

    try:
        password = env("PIA_PASSWORD")
    except EnvError:
        print("PIA_PASSWORD env var not set, falling back to user input")
        password = getpass()

    if pia.get_token(username, password):
        print("Login successful!")
        break
    else:
        print("Error logging in, please try again...")

# Add key
status, response = pia.addkey()
if status:
    print("Added key to server!")
else:
    print("Error adding key to server")
    print(response)

# Build config
timestamp = int(datetime.now().timestamp())
location = pia.region.replace(' ', '-')
config_file = 'PIA-{}-{}.conf'.format(location, timestamp)
print("Saving configuration file {}".format(config_file))
with open(config_file, 'w') as file:
    file.write('[Interface]\n')
    file.write('Address = {}\n'.format(pia.connection['peer_ip']))
    file.write('PrivateKey = {}\n'.format(pia.privatekey))
    file.write('DNS = {},{}\n\n'.format(pia.connection['dns_servers'][0], pia.connection['dns_servers'][1]))
    file.write('[Peer]\n')
    file.write('PublicKey = {}\n'.format(pia.connection['server_key']))
    file.write('Endpoint = {}:1337\n'.format(pia.connection['server_ip']))
    file.write('AllowedIPs = 0.0.0.0/0\n')
    file.write('PersistentKeepalive = 25\n')
