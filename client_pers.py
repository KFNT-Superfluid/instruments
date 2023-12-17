#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 20:30:47 2023

@author: emil
"""

from multiprocessing.connection import Client
import time

with open('instrument_server_port.txt', 'r') as port_file:
    port = int(port_file.readline())

address = ('localhost', port)

try:
    with Client(address) as conn:
        print("connected to ", address)
        while True:
            t0 = time.time()
            print("Sending!")
            conn.send("Hello!")
            t1 = time.time()
            msg = conn.recv()
            t2 = time.time()
            print(msg, (t2 - t0)*1e6, (t1-t0)*1e6)
            time.sleep(0.5)
finally:
    conn.close()