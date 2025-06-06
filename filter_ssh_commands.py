#!/usr/bin/env python3
# /usr/local/bin/filter_ssh_commands.py

import sys
import os
import re

# Récupérer la commande originale
original_command = os.environ.get('SSH_ORIGINAL_COMMAND')

if original_command is None:
    sys.stderr.write("Pas de commande SSH\n")
    sys.exit(1)

# Liste des commandes autorisées
allowed = [
    "sudo systemctl restart dnsmasq",
    "sudo systemctl status dnsmasq",
    "sudo cat /etc/dnsmasq.d/dhcp_hosts.conf",
    "echo test",
    "ls"
]

allowed_regex = [
    r"echo dhcp-host=.*,.* \| sudo tee -a /etc/dnsmasq\.d/dhcp_hosts\.conf",
    r"sudo cat /etc/dnsmasq\.d/dhcp_hosts\.conf",
    r"sudo sed -i '/[A-Fa-f0-9:]{17}/d' /etc/dnsmasq\.d/dhcp_hosts\.conf",
    r"ls .*",
]


# Vérifier commandes exactes
if original_command in allowed:
    os.system(original_command)
    sys.exit(0)

# Vérifier avec regex pour echo dhcp-host
for elem in allowed_regex:
    if re.match(elem, original_command):
        os.system(original_command)
        sys.exit(0)


# Commande non autorisée
sys.stderr.write(f"Commande non autorisee: {original_command}\n")
sys.exit(1)
