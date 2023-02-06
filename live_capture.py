import pyshark
from yaml import safe_load
from mesh_class import MeshClass
import copy
from threading import Event, Thread

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
        print(rsu + " " + str(data[rsu]) + " // ", end='')


def clear_data():
    global cur_time
    cur_time = 0
    for name in rsus.keys():
        data[name] = 0

def handle_paket(block):
    #print("Got something!")
    for rsu in rsus.keys():
        if (hasattr(block, 'ip')  
                and str(block['ip'].src) == rsus[rsu]['ip']             # RSU IP Address
                and str(block['ip'].dst) == yaml_data['host_ip']        # This IP address ### CHANGE MANUALLY IN YAML! ###
                and str(block['ip'].proto) == '17'                      # UDP Protocol number
            and hasattr(block, 'udp')
                and str(block['udp'].port) == rsus[rsu]['src_port']     # This UDP transmisison port            
                and str(block['udp'].dstport) == rsus[rsu]['dst_port']  # This UDP reception port
            and hasattr(block, 'DATA')
        ):
            # If we got in here, then this packet is a forwarded C-V2X packet from the specified RSU
            data[rsu] += 1
            #print ("Packet received: ", rsu)

cap = pyshark.LiveCapture(interface=yaml_data["wireshark_interface"], 
    bpf_filter="udp and not src host %s" % yaml_data['host_ip'])

for attenuation in yaml_data["attenuations"]:
    # Clear the data and declare the start of the trial
    clear_data()
    print("Starting trial on attenuation value\x1B[35m %d\x1B[37m db for\x1B[35m %d\x1B[37m seconds..." 
        % (attenuation, yaml_data["trial_length"]))

    # Go through and set all the attenuation values we need
    for tx_port in yaml_data["static_mesh_ports"]:
        for rsu in rsus.keys():
            rx_port = rsus[rsu]["mesh_port"]
            partial_att = rsus[rsu]["att_offset"]
            diff_att = attenuation - partial_att
            diff_att = round(diff_att * 4) / 4 # needs a multiple of 0.25

            print('dbg: mesh.set_att(%s, %s, %f)' % (tx_port, rx_port, diff_att))

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
    print("Ending trial for\x1B[35m %d\x1B[37m db" % attenuation, end="\n\n")



