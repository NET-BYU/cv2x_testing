#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Bryson Schiel - @schielb (GitHub)
# Created Date: Feb 6, 2023
# Latest Update: Feb 15, 2023
# version ='1.0'
# ---------------------------------------------------------------------------
""" 
    Python file to setup initial files that aren't included due to the 
    .gitignore, as well as creating directories and such.
"""
# ---------------------------------------------------------------------------
 
import os

yaml_string = \
    "# Initial RSUs YAML file\n" + \
    "# Start by retyping the IP address of the host computer receiving the forwarded V2X packets\n" \
    "# and the IP address of the attenuator mesh.\n" \
    "# For each new RSU to add to your simulation, use the following format:\n" \
    "#\n" \
    "# <rsu name>:\n" \
    "#     ip: <IPv4 ip address of RSU>\n" \
    "#     src_port: <src port at RSU>\n" \
    "#     dst_port: <destination port at host>\n" \
    "#     mesh_port: <A-F single character on mesh ports>\n" \
    "#     att_offset: <attenuation offset for RSU (float value)>\n" \
    "#\n" \
    "# An example has already been provided for you below...\n\n" \
    "################### META PARAMETERS ###################\n" \
    "# IPv4 ip address of host (this computer)\n" \
    "host_ip: <IPv4 ip address of host (this computer)>\n" \
    "\n" \
    "# IPv4 ip address of attenuator mesh\n" \
    "mesh_ip: <IPv4 ip address of attenuator mesh>\n" \
    "\n" \
    "# List of A-F single characters on mesh port of transmitter\n" \
    "static_mesh_ports: ['A']\n" \
    "\n" \
    "# List of total attenuation values to test\n" \
    "#  An example list from our lab experiment is [90, 100, 105, 107, 109, 111, 113, 115]\n" \
    "#  IMPORTANT!!! Make sure that these are all higher than any 'att_offset' in your RSUs!!!\n" \
    "attenuations: [90, 100, 105, 107, 109, 111, 113, 115]\n" \
    "\n" \
    "# Time length of a trial in seconds (integer)\n" \
    "trial_length: 900\n" \
    "\n" \
    "# Wireshark interface (ex: eth0)\n" \
    "wireshark_interface: eth0\n" \
    "\n" \
    "################### RSU DICT ###################\n" \
    "rsus:\n" \
    "    rsu_1:\n" \
    "        ip: 192.168.0.1\n" \
    "        src_port: 8080\n" \
    "        dst_port: 8081\n" \
    "        mesh_port: B\n" \
    "        att_offset: 50.0"

with open('cv2x.yml', 'w') as rsu_yaml:
    rsu_yaml.write(yaml_string)

for newpath in ['./Results', './Packet_Captures']:
    if not os.path.exists(newpath):
        os.makedirs(newpath)