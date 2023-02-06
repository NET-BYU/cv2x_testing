from mesh_class import MeshClass

ip_address = '192.168.0.1'

mesh = MeshClass(ip_address)

port1s = ['A', 'B', 'C', 'D', 'E', 'F']
port2s = ['A', 'B', 'C', 'D', 'E', 'F']

for port1 in port1s:
    for port2 in port2s:
        if port1 != port2:
            mesh.set_att(port1, port2, 0)