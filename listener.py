#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 20:11:24 2023

@author: emil
"""

from multiprocessing.connection import Listener
import os
import threading as thr
from queue import Queue
import time

class ClientHandler(thr.Thread):
    def __init__(self, conn, end_event, name, finished):
        super().__init__()
        self.conn = conn
        self.end_event = end_event
        self.name = name
        self.finished = finished
    def run(self):
        try:
            while True:
                # if self.end_event.is_set():
                #     break
                # if self.conn.poll():
                print(f"{self.name} Receiving")
                msg = self.conn.recv()
                print(f"{self.name} recv'd: {msg}")
                self.conn.send(f"{self.name} got {msg} {time.time()}")
        except EOFError:
            pass
        except:
            print(f"problem with {self.name}")
            raise
        finally:
            print(f"quitting {self.name}")
            self.conn.close()
            self.finished.put(self.name)

port_filename = 'instrument_server_port.txt'
port = 0
address = ('localhost', port)
handlers = {}
end_event = thr.Event()
handler_id = 0
finished_handlers = Queue()
try:
    while True:
        with Listener(address) as listener:
            print("Listening: ", listener.address)
            if True:
                port = listener.address[1]
                # address = ('localhost', port)
                with open(port_filename, 'w') as port_file:
                    port_file.write(str(port))
        
            conn = listener.accept()
            print(f"Accepted {listener.last_accepted}")
            handler_name = f"handler {handler_id}"
            c = ClientHandler(conn, end_event, name=handler_name,
                              finished=finished_handlers)
            handlers[handler_name] = c
            handlers[handler_name].start()
            handler_id += 1
        while not finished_handlers.empty():
            name = finished_handlers.get()
            print(f"Joining {name}")
            handlers.pop(name).join()
finally:
    end_event.set()
    for c in handlers.values():
        c.join()
    os.remove(port_filename)