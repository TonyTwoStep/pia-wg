#! /usr/bin/env python3
import argparse
import sys
from datetime import datetime
from getpass import getpass

from environs import Env, EnvError
from pick import pick

from piawg import piawg

# Setup CLI argument parser
parser = argparse.ArgumentParser(description='hsand/pia-wg modified by TonyTwoStep to include optional CLI args and '
                                             'env var usage for quality of life and use in automation')
parser.add_argument('-l', '--list', action='store_true', help='List available PIA server endpoints', required=False)
parser.add_argument('-s', '--server', help='PIA server to use', required=False)
args = vars(parser.parse_args())


pia = piawg()
env = Env()

# Generate public and private key pair
pia.generate_keys()

# Select region
title = 'Please choose a region: '
options = sorted(list(pia.server_list.keys()))

# CLI list arg specified: List out the server options and exit
if args['list']:
    print("PIA Server Options\nIndex\tServer Name\n-------------------------------")
    for index, server_option in enumerate(options):
        print(f"{index}\t{server_option}")
    sys.exit(0)


# CLI server arg was specified
if args['server']:
    # Handling for server option not valid
    if args['server'].lower() not in [option.lower() for option in options]:
        print(f"Server option '{args['server']}' is not in the options list... try running the script again with"
              f" the --list parameter to see the available options.")
        sys.exit(1)

    # Get the index of the chosen option
    index = options.index(args['server'])
    option = args['server']

    pia.set_region(option)
    print(f"Selected {option}({index}) server successfully.")

else:
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
