#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Bryson Schiel - @schielb (GitHub)
# Created Date: May 18, 2023
# Latest Update: May 18, 2023
# version ='1.1'
# ---------------------------------------------------------------------------
""" 
    This file tries to "zoom in" on the knee for each RSU during testing.
"""
# ---------------------------------------------------------------------------

import pyshark
from yaml import safe_load
from resources.mesh_class import MeshClass
import copy
from threading import Event, Thread
import time
import os
from datetime import datetime
import matplotlib.pyplot as plt

def call_repeatedly(interval, func, *args):
    stopped = Event()
    def loop():
        while not stopped.wait(interval): # the first call is in `interval` secs
            func(*args)
    Thread(target=loop).start()    
    return stopped.set


with open("./cv2x.yml") as f:
    yaml_data = safe_load(f)

mesh = MeshClass(yaml_data["mesh_ip"])

rsus : dict = copy.deepcopy(yaml_data["rsus"])

data = {}
cur_time : int

def display_data():
    global cur_time
    cur_time += 1
    print("\r    Time: %d // " % cur_time, end='')
    for rsu in data.keys():
        print(rsu + " ≈ " + str(data[rsu]) + " // ", end='')


def clear_data():
    global cur_time
    cur_time = 0
    for name in rsus.keys():
        data[name] = 0

def handle_paket(block):
    #print("Got something!")
    i = 0
    for rsu in rsus.keys():
        if (hasattr(block, 'ip')  
                and str(block['ip'].src) == rsus[rsu]['ip']                 # RSU IP Address
                and str(block['ip'].dst) == yaml_data['host_ip']            # This IP address ### CHANGE MANUALLY IN YAML! ###
                and str(block['ip'].proto) == '17'                          # UDP Protocol number
            and hasattr(block, 'udp')
                and str(block['udp'].dstport) == str(rsus[rsu]['dst_port']) # This UDP reception port
            and hasattr(block, 'DATA')
        ):
            # If we got in here, then this packet is a forwarded C-V2X packet from the specified RSU
            data[rsu] += 1
            #print ("Packet received: ", rsu)

def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + "(" + str(counter) + ")" + extension
        counter += 1

    return path

cap_folder_name = "Packet_Captures/" + datetime.now().strftime("%b-%d-%H:%M:%S")
res_folder_name = "Results/" + datetime.now().strftime("%b-%d-%H:%M:%S")

#See if we need to create a new folder and csv file for today for today
for newpath in [cap_folder_name, res_folder_name]:
    if not os.path.exists(newpath):
        os.makedirs(newpath)

# This is where we see some tricky stuff. We set a bottom and a top range for attenuation values, and then
#  we need to sort through each one for each RSU to find the knee of the RSU (where, for one dB value, we
#  get a reception rate above the critical safrety limit, and for the next dB, that RSU performs below the
#  critical safety limit).
#
# I think that in this case, it is fine to keep gathering from each RSU, even if we have already found a  
#  knee for the other RSUs. I think the best way is to find a middle sort option for each RSU, and in 
#  reality we need to focus on 1 RSU at a time. We will probably wind up having to go back and forth quite 
#  a bit to make it work out, but that should be okay.
bottom_att = yaml_data["att_low"]
top_att = yaml_data["att_high"]
attenuation = bottom_att

critical_safety_limit = 0.9

knee_finders = {}
for rsu in rsus:
    knee_finders[rsu] = {"bottom": bottom_att, "top": top_att, "knee_found": False}

# This set of numbers lets us make sure that we find knees iteratively, focusing on one and then the other
num_knees_found = 0
num_rsus = len(rsus)

results = {}


def midway(bottom, top):
    return int(((top - bottom) / 2) + bottom)

while num_knees_found < num_rsus:
    # Clear the data and declare the start of the trial
    clear_data()
    print("\x1B[32mSetting up trial on attenuation value\x1B[35m %d\x1B[32m db for\x1B[35m %d\x1B[32m seconds...\x1B[37m" 
        % (attenuation, yaml_data["trial_length"]))

    cap_file_name = uniquify(cap_folder_name + "/attenuation_%d.pcap" % attenuation)

    cap = pyshark.LiveCapture(interface=yaml_data["wireshark_interface"], 
        bpf_filter="udp and not src host %s" % yaml_data['host_ip'],
        output_file=cap_file_name)

    

    # Go through and set all the attenuation values we need
    for tx_port in yaml_data["static_mesh_ports"]:
        for rsu in rsus.keys():
            rx_port = rsus[rsu]["mesh_port"]
            partial_att = rsus[rsu]["att_offset"]
            diff_att = attenuation - partial_att
            diff_att = round(diff_att * 4) / 4 # needs a multiple of 0.25

            #print('dbg: mesh.set_att(%s, %s, %f)' % (tx_port, rx_port, diff_att))
            mesh.set_att(tx_port, rx_port, diff_att)

    time.sleep(10) # Delay to allow new setup to settle
    print("Starting trial:")

    # Start the repeating timer
    end_timer = call_repeatedly(1, display_data)

    # Start the packet capture
    try:
        cap.apply_on_packets(handle_paket, timeout=int(yaml_data["trial_length"]))

    except Exception as e:
        if e is TimeoutError:
            # This just means that a packet was caught mid-exit; not fatal to the experiment
            pass
    finally:
        end_timer()
    #timer.cancel()
    print()
    print("\x1B[32mEnding trial for\x1B[35m %d\x1B[32m db\x1B[37m" % attenuation, end="\n")
    
    print("Saving data from trial...")
    # Save the results in their own files
    cap.close()

    results[attenuation] = {}
    
    for rsu in rsus:
        
        
        total_time_gap = yaml_data["trial_length"]
        num_packets = data[rsu]

        estimated_num_spaced = int(total_time_gap * 10)
        percent_reception = float(float(num_packets) / float(estimated_num_spaced))

        summaries_file_name = '%s/summaries_%s.txt' % (res_folder_name, rsu)

        print("Saving %s data in %s" % (rsu, summaries_file_name))

        print(file=open(summaries_file_name, 'a'))
        print("Attenuation ", attenuation, file=open(summaries_file_name, 'a'))
        print("Number of packets: ", num_packets, file=open(summaries_file_name, 'a'))
        print('Total time gap: ', total_time_gap, file=open(summaries_file_name, 'a'))
        print('Total expected packets: ', estimated_num_spaced, file=open(summaries_file_name, 'a'))
        print("Calculated missed packets: ", estimated_num_spaced - num_packets, file=open(summaries_file_name, 'a'))
        print("Percent reception: ", percent_reception, file=open(summaries_file_name, 'a'))

        # Now we focus on taking the current recpetion rate and trying to find the knee
        if percent_reception > critical_safety_limit:
            if attenuation > knee_finders[rsu]["bottom"]:
                knee_finders[rsu]["bottom"] = attenuation
        else:
            # Crucially, we don't want to record a slightly low value if a higher attenuation, for 
            #  whatever reason, gives us a better recpetion rate. 
            if attenuation < knee_finders[rsu]["top"] and attenuation > knee_finders[rsu]["bottom"]:
                knee_finders[rsu]["top"] = attenuation

        results[attenuation][rsu] = percent_reception


    
    print("Data saved 👍\n")
    # Here, we reset each knee as needed
    for rsu in list(rsus)[num_knees_found:]:
        if knee_finders[rsu]["top"] - knee_finders[rsu]["bottom"] == 1:
            knee_finders[rsu]["knee_found"] = True
            num_knees_found += 1
        else:
            if knee_finders[rsu]["top"] - knee_finders[rsu]["bottom"] < 0:
                # Error, top and bottom are switched, move top back
                knee_finders[rsu]["top"] = top_att
            # No matter what, if the current index doesn't check out, break
            break

    # Here, we need to set the "attenuation" variable for the next loop
    if num_knees_found < num_rsus:
        nkf = list(knee_finders)[num_knees_found]
        attenuation = midway(knee_finders[nkf]["bottom"], knee_finders[nkf]["top"])
        
        print("New attenuation: %d" % attenuation)

##############################################################################################
# At this point, all attenuations have been gathered, and we are ready to display the results.
##############################################################################################
for rsu in rsus:

    values = []

    num_vals = 0
    att = 0
    rec = 0.0

    for attenuation in results:
        values.append((attenuation, results[attenuation][rsu]))
    values.sort()

    attenuations = []
    reception_rates = []
    for i in values:
        attenuations.append(i[0])
        reception_rates.append(i[1] * 100.0)

    data['att'] = attenuations
    data[rsu] = {}
    data[rsu]['rate'] = reception_rates


    plt.plot(attenuations, reception_rates, marker = 'o')
    plt.xlabel("Attenuations (dB)")
    plt.ylabel("Packet Reception Rate (%)")
    plt.title("Reception Rate per Attenuation (%s)" % rsu)
    plt.ylim(-4, 104)
    plt.axhline(y=90, color='red', linestyle='--', label='Critical Safety Limit: 90%')
    plt.show()
    plt.savefig(res_folder_name + '/Attenuations-%s.png' % rsu)
    plt.clf()

for rsu in rsus:
    plt.plot(data['att'], data[rsu]['rate'], label=rsu, marker = 'o')

plt.xlabel("Attenuation (db)")
plt.ylabel("Packet Reception Rate (%)")
plt.ylim(-4, 104)
plt.title("Reception Rate per Attenuation (All RSU Comparison)")
plt.axhline(y=90, color='red', linestyle='--', label='Critical Safety Limit: 90%')
plt.legend()
plt.savefig(res_folder_name + '/Comparison-Attenuations.png')
plt.show()
plt.clf()

