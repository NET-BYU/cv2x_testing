#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Bryson Schiel - @schielb (GitHub)
# Created Date: Feb 1, 2023
# Latest Update: Feb 15, 2023
# version ='1.0'
# ---------------------------------------------------------------------------
""" 
    A python file to clear the Mini-Circuits Mesh Attenuator
"""
# ---------------------------------------------------------------------------

from mesh_class import MeshClass
import sys
from yaml import safe_load

# It is anticipated that this file be run from the cv2x_testing folder as "python3 resources/clear_mesh.py"
with open("./resources/mesh_ip.yml") as f:
    yaml_data = safe_load(f)

ip_address = yaml_data["ip_address"]

mesh = MeshClass(ip_address)

port1s = ['A', 'B', 'C', 'D', 'E', 'F']
port2s = ['A', 'B', 'C', 'D', 'E', 'F']

att_to_set = 0
args = sys.argv

if len(args) == 1:
    pass
elif len(args) == 2:
    if args[1] == "--reset":
        att_to_set = 95
    else:
        print("Error: incorrect arg passed - expecting nothing or '--reset'", file=sys.stderr)
        exit(1)
else:
    print("Error: too many args passed - expecting nothing or '--reset'", file=sys.stderr)
    exit(1)

for port1 in port1s:
    for port2 in port2s:
        if port1 != port2:
            mesh.set_att(port1, port2, att_to_set)