import pyshark
from yaml import safe_load
from mesh_class import MeshClass
import copy

with open("./rsus.yaml") as f:
    yaml_data = safe_load(f)

mesh = MeshClass(yaml_data["mesh_ip"])

rsus : dict = copy.deepcopy(yaml_data["rsus"])

data = {}

def clear_data():
    for name in rsus.keys():
        data[name] = 0

def handle_paket(block):
    for rsu in rsus.keys():
        if (hasattr(block, 'ip')  
                and str(block['ip'].src) == rsus[rsu]['ip']               # RSU IP Address
                and str(block['ip'].dst) == yaml_data['host_ip']    # This IP address ### CHANGE MANUALLY IN YAML! ###
                and str(block['ip'].proto) == '17'                  # UDP Protocol number
            and hasattr(block, 'udp')
                and str(block['udp'].port) == rsus[rsu]['port']           # This UDP transmisison port            
                and str(block['udp'].dstport) == rsus[rsu]['dst_port']    # This UDP reception port
            and hasattr(block, 'DATA')
        ):
            # If we got in here, then this packet is a forwarded C-V2X packet from the specified RSU
            data[rsu] += 1
            print ("Packet received: ")

cap = pyshark.LiveCapture(interface=yaml_data["wireshark_interface"], 
    bpf_filter="udp and not src host %s" % yaml_data['host_ip'])

print("Starting")

try:
    cap.apply_on_packets(handle_paket, timeout=int(yaml_data["trial_length"]))
except Exception as e:
    if e is TimeoutError:
        # This just means that a packet was caught mid-exit; not fatal to the experiment
        pass
print("Ending")