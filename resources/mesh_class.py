#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Jon Backman - @backmanj (GitHub)
# Created Date: Sep 30, 2022
# version ='1.0'
# ---------------------------------------------------------------------------
""" 
    A python file to create a class that will interact with the Mini-Circuits
    ZTMN-0695B-S.
"""
# ---------------------------------------------------------------------------

import requests
# import pycurl
import urllib3

channels = {
    "AA": (0, 0),
    "AB": (1, 1),
    "AC": (1, 4),
    "AD": (1, 2),
    "AE": (2, 4),
    "AF": (2, 2),
    "BA": (1, 1),
    "BB": (0, 0),
    "BC": (1, 3),
    "BD": (2, 1),
    "BE": (2, 3),
    "BF": (4, 1),
    "CA": (1, 4),
    "CB": (1, 3),
    "CC": (0, 0),
    "CD": (3, 1),
    "CE": (4, 4),
    "CF": (4, 2),
    "DA": (1, 2),
    "DB": (2, 1),
    "DC": (3, 1),
    "DE": (3, 2),
    "DD": (0, 0),
    "DF": (4, 3),
    "EA": (2, 4),
    "EB": (2, 3),
    "EC": (4, 4),
    "ED": (3, 2),
    "EE": (0, 0),
    "EF": (3, 3),
    "FA": (2, 2),
    "FB": (4, 1),
    "FC": (4, 2),
    "FD": (4, 3),
    "FE": (3, 3),
    "FF": (0, 0),
}

index = {
    1: 'A',
    2: 'B',
    3: 'C',
    4: 'D'
}


class MeshClass:
    def __init__(self, address):
        """
        MeshClass uses python libraries requests and urllib3 to make http commands

        Functions in this class:\n
            set_att\n
            check_att\n
            sweep_setup\n
            sweep_config\n
            sweep_start\n
            sweep_stop\n
            hop_setup\n
            hop_point_config\n
            hop_start\n
            hop_stop\n
        """
        self.address = address

        ports = channels["AB"]
        block = ports[0]
        channel = ports[1]

        http = urllib3.PoolManager()
        response = http.request(
            'GET', f"http://{self.address}/:0{block}:CHAN:{channel}:ATT?")

        if response.status != 200:
            raise ValueError('Device at %s is not a viable mesh attenuator.' % address)


    def set_att(self, port1: str, port2: str, atten: float):
        """
        set_att:
            This lets you change the attentuation level in on any connection between ports A-F\n
            It needs three arguments: port1, port2, atten\n
            port1 and port2 represent which ports you want to connect and atten represents the attenuation level\n
            Example: set_att('B','D', 50) will set attenuation for the connection between port B and port D to 50\n
            Using the function set_att('B','D', 50) and set_att('D', 'B', 50) will give you the same results\n
            If port1 and port2 arguments are the same, you will get an error\n
            atten is any number between 0-95 db
        """
        string = port1+port2
        ports = channels[string]
        block = ports[0]
        channel = ports[1]

        if(ports[0] == 0):
            print("Invalid Arguments for Ports")
        elif(atten < 0 or atten > 95):
            print("Invalid Argument for Attenuation")
        else:
            requests.get(
                f'http://{self.address}/:0{block}:CHAN:{channel}:SETATT:{atten}')
            print(f"Ports:{port1} {port2}; Atten:{atten}")

    def check_att(self, port1: str, port2: str):
        """
        check_att:
            This lets you check what the attenuation is for any connection between ports A-F\n
            It needs two arguments: port1, port2\n
            port1 and port2 represent which ports you want to connect\n
            Example: check_att('B', 'D') will tell you the attenuatioln between ports B and D\n
            Using check_att('B', 'D') and check_att('D', B') will give you the same results\n
            If port1 and port2 arguments are the same, you will get an error\n
            The results are returned by the http command and will include the attenuator block\n
            Example of results: 01:30.0 this is showing that on the first attenuator block the attenuation is 30 db
        """
        string = port1+port2
        ports = channels[string]
        block = ports[0]
        channel = ports[1]

        if(ports[0] == 0):
            print("Invalid Arguments for Ports")

        else:
            http = urllib3.PoolManager()
            response = http.request(
                'GET', f"http://{self.address}/:0{block}:CHAN:{channel}:ATT?")
            print(response.data.decode('utf-8'))

    def sweep_setup(self, direct: int):
        """
        sweep_setup:
            This will set the direction of your sweep function\n
            It has one argument: direct\n
            direct will choose what direction you are sweeping\n
            Options are 0 for lowest to highest value, 1 for highest to lowest, and 2 for bi-directional sweep--a sweep forward and then backwards\n
            Example: sweep_setup(0) this will set your sweep to go from lowest to highest value
        """
        requests.get(f'http://{self.address}/:SWEEP:DIRECTION:{direct}')

    def sweep_config(self, units: str, time: int, low: int, high: int, step: float, port1: str, port2: str):
        """
        sweep_config:
            This will set the time and units, the range and the ports for the sweep function\n
            It has six arguments: units, time, low, high, port1, port2\n
            units will determine what units of time it will use.\n
            Options are 'U' for microseconds, 'M' for milliseconds and 'S' for seconds\n
            time is an integer that will be determine the length in units how long till it takes the next step\n
            The maximum time in 'S' is 4. Its kind of jank but that's been my experience with it\n
            step is the stepsize for your sweeping function in db.\n
            low determines your lowest value on your sweep. high determines your highest value on your sweep\n
            port1 and port2 represent which ports you want to connect together\n
            Example: sweep_run('M', 300, 10, 50, 0.5, 'C', 'E') will run a sweep for 300 mils from 10 db to 50 db with 0.5 db stepsize on ports C and E
        """
        string = port1+port2
        ports = channels[string]
        block = ports[0]
        channel = index[ports[1]]
        if(ports[0] == 0):
            print("Invalid Arguments for Ports")
        else:
            requests.get(f'http://{self.address}/:SWEEP:DWELL_UNIT:{units}')
            requests.get(f'http://{self.address}/:SWEEP:DWELL:{time}')
            requests.get(f'http://{self.address}/:SWEEP:START:{low}')
            requests.get(f'http://{self.address}/:SWEEP:STOP:{high}')
            requests.get(f'http://{self.address}/:SWEEP:STEPSIZE:{step}')
            requests.get(f'http://{self.address}/:SWEEP:NOOFCHANNELS:1')
            requests.get(f'http://{self.address}/:SWEEP:CHANNEL_INDEX:0')
            requests.get(
                f'http://{self.address}/:SWEEP:CHANNEL_ADDRESS:0{block}{channel}')

    def sweep_start(self):
        """
        sweep_start:
            This will start the sweep. It will run indefinitely until stopped\n
        """
        requests.get(f'http://{self.address}/:SWEEP:MASTERMODE:ON')

    def sweep_stop(self):
        """
        sweep_stop:
            This will stop the sweep.\n
        """
        requests.get(f'http://{self.address}/:SWEEP:MASTERMODE:OFF')

    def hop_setup(self, points: int, direct: int):
        """
        hop_setup:
            This will set the number of hop points and direction for hopping\n
            It has two arguments: points, direct\n
            points will determine how many points you have in your hopping sequence\n
            direct will choose what direction you are hopping\n
            Options are 0 for lowest index to highest index, 1 for highest index to lowest index, and 2 for bi-directional hopping\n
            Example: hop_points(2,'S', 120) will run for 120 seconds and run from lowest to highest value\n
        """
        requests.get(f'http://{self.address}/:HOP:POINTS:{points}')
        requests.get(f'http://{self.address}/:HOP:DIRECTION:{direct}')

    def hop_point_config(self, point: int, units: str, time: int, atten: int, port1: str, port2: str):
        """
        hop_point:
            This will set a point at a given index the units of time, time duration, attenuation and port connections\n
            It has six arguments: point, units, time, atten, port1, port2\n
            point will choose which index on your sequence of points that you will modify\n
            units will determine what units of time it will use.\n
            Options are 'U' for microseconds, 'M' for milliseconds and 'S' for seconds\n
            time is an integer that will be determine the length in units how long it will dwell on one point\n
            The maximum time in 'S' is 4. Its kind of jank but that's been my experience with it\n
            atten is the attenuation at this point in your hop sequence\n
            port1 and port2 represent which ports you want to connect together\n
            Example: hop_point(0, 'U', 600, 20, 'A', 'C') will modify my first point on my sequence to run for 600 microseconds with an\n
            attenuation of 20 db on the connection between ports A and C\n
        """
        string = port1+port2
        ports = channels[string]
        block = ports[0]
        channel = index[ports[1]]
        if(ports[0] == 0):
            print("Invalid Arguments for Ports")
        requests.get(f'http://{self.address}/:HOP:POINT:{point}')
        requests.get(f'http://{self.address}/:HOP:DWELL_UNIT:{units}')
        requests.get(f'http://{self.address}/:HOP:DWELL:{time}')
        requests.get(f'http://{self.address}/:HOP:ATT:{atten}')
        requests.get(f'http://{self.address}/:HOP:NOOFCHANNELS:1')
        requests.get(f'http://{self.address}/:HOP:CHANNEL_INDEX:0')
        requests.get(
            f'http://{self.address}/:HOP:CHANNEL_ADDRESS:0{block}{channel}')

    def hop_start(self):
        """
        hop_start:
            This will start the hopping. It will run indefinitely until stopped\n
        """
        requests.get(f'http://{self.address}/:HOP:MASTERMODE:ON')

    def hop_stop(self):
        """
        sweep_start:
            This will stop the sweeping.\n
        """
        requests.get(f'http://{self.address}/:HOP:MASTERMODE:OFF')
