#!/usr/bin/env python

from scapy.all import *
from dpkt.http import Request, Response

from persistencia import get_session, RequestHTTP, ResponseHTTP
import sys

class Sniffer(object):
    def __init__(self):
        self.callbacks=[]
        
    def addCallback(self,callback):
        self.callbacks.append(callback)
        
    def sniffear(self):
        sniff(prn=self.callCallbacks)
        
    def callCallbacks(self,pkt):
        for each in self.callbacks:
            each(pkt)
            
class HTTPandHTTPSSniffer(Sniffer):
    def __init__(self,portHTTP=80,portHTTPS=443):
        self.callbacks=[]
        self.portHTTP = portHTTP
        self.portHTTPS = portHTTPS
        
    def sniffear(self,count = None):
        if count == None:
            sniff(prn=self.callCallbacks, filter='tcp port %s or port %s'%(self.portHTTP,self.portHTTPS))
        else:
            sniff(prn=self.callCallbacks, filter='tcp port %s or port %s'%(self.portHTTP,self.portHTTPS), count = count)
        
class HTTPAssembler(object):
    def __init__(self,port=80):
        self.port = port
        self.paquetes={}
    
    def _request_methods(self):
        return
        set(Request._methods)
        
    def nuevo_paquete(self,pkt):
        #chequeo que el paquete no sea solo de padding o tcp vacio
        if not pkt.lastlayer().haslayer(Raw):
            return
        pktTCP = pkt.getlayer(TCP)
        portOrigen = pktTCP.sport
        portDestino = pktTCP.dport
        if not(portOrigen == self.port or portDestino == self.port):
            return
        if portOrigen == self.port:
            self.response(pkt)
        else:
            self.request(pkt)
    
    def _persistirResponse(self,cuadrupla, mensaje):
        try:
            s = get_session()
            ipOrigen, ipDestino, portOrigen, portDestino = cuadrupla
            tipo =  'Response' if isinstance(mensaje,Response) else 'Request'
            s.add(ResponseHTTP(ipOrigen, ipDestino, portOrigen, portDestino,
                              mensaje.headers,mensaje.body, mensaje.status,mensaje.reason))
            s.commit()
        except Exception, e:
            print e
            sys.exit(-1) 
    
    def _persistirRequest(self,cuadrupla, mensaje):
        try:
            s = get_session()
            ipOrigen, ipDestino, portOrigen, portDestino = cuadrupla
            s.add(RequestHTTP(ipOrigen, ipDestino, portOrigen, portDestino,
                              mensaje.headers,mensaje.body, mensaje.method,mensaje.uri))
            s.commit()
        except Exception, e:
            print e
            sys.exit(-1)     
    
    def _agregarPaquete(self,pkt):
        cuadrupla = self._get_cuadrupla(pkt)
        if cuadrupla in self.paquetes:
            self.paquetes[cuadrupla]+=pkt.getlayer(Raw).load
        else:
            self.paquetes[cuadrupla]=pkt.getlayer(Raw).load
        
    def request(self,pkt):
        cuadrupla = self._get_cuadrupla(pkt)
        self._agregarPaquete(pkt)
        try:
            r = Request(self.paquetes[cuadrupla])
            del self.paquetes[cuadrupla]
            self._persistirRequest(cuadrupla,r)

        except:
            pass
        
        
    def response(self,pkt):
        cuadrupla = self._get_cuadrupla(pkt)
        self._agregarPaquete(pkt)
        try:
            r = Response(self.paquetes[cuadrupla])
            del self.paquetes[cuadrupla]
            self._persistirResponse(cuadrupla,r)
        except:
            pass
            
    def _get_cuadrupla(self,pkt):
        pktIP = pkt.getlayer(IP)
        ipOrigen = pktIP.src
        ipDestino = pktIP.dst
        pktTCP = pktIP.getlayer(TCP)
        portOrigen = pktTCP.sport
        portDestino = pktTCP.dport
        return (ipOrigen,ipDestino,portOrigen,portDestino)
            
    

hs = HTTPandHTTPSSniffer()
ha = HTTPAssembler()
hs.addCallback(ha.nuevo_paquete)
hs.sniffear(count=100)


    