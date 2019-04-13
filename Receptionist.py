# coding: utf-8

import time
import pickle
import socket
import uuid
import logging
import queue
# import argparse
import threading
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Receptionist(Node):
    def __init__(self, own_id, address, root_id, root_address,timeout=3):
        super().__init__(1, address, root_id, root_address, timeout=3)
        self.queueIn = queue.Queue
        self.queueOut = queue.Queue
        self.CookAddr = ('locahost', 5002)
        self.CookID = 2
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.socket.bind((self.address))
        self.logger = logging.getLogger("Rececionista {}".format(self.own_id))

    def receiveRequest(self,objeto): 
        # adicionar a fila de pedidos a entregar ao cook, ex msg: {'method': 'ORDER', 'args': {'hamburger': 1, 'idDestino': 1}}
        objeto['args']['idDestino']=self.CookID
        msg = {'method':'ORDER_RECVD', 'args': str(uuid.uuid1())} #send clients unique ticket
        p = pickle.dumps(msg)
        self.logger.debug("Object: %s is now in the queue", objeto)
        #self.queueOut.put(objeto)
        self.socket.send(p, objeto['args']['clientAddr'])

    def deliverOrder(self,args,address):
        pass

    def send(self, o, address):
        p = pickle.dumps(o)
        self.socket.sendto(p, address)

    def recv(self):
        try:
            p, addr = self.socket.recvfrom(1024)
        except socket.timeout:
            return None, None
        else:
            if len(p) == 0:
                return None, addr
            else:
                return p, addr

    def run(self):
        done = False
        while not done:
            p, addr = self.recv()
            if p is not None:
                o = pickle.loads(p)
                self.logger.debug('Received Object: %s', o)
                if o['method'] == 'TOKEN' and o['args']['args']['idDestino']==self.own_id: #vamos enviar o objeto todo e usamos no args do method:token
                    self.logger.debug("This token is for me")
                    if o['args']['method']=='ORDER':
                        self.receiveRequest(o['args'])


def main():
    recept = Receptionist(1, ('localhost', 5001), 0, ('localhost', 5000))
    recept.run()

if __name__ == '__main__':
    main()
