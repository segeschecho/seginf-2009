#!/usr/bin/env python

from scapy.all import *
from dpkt.http import Request, Response

from persistencia import get_session, RequestHTTP, ResponseHTTP
import sys
import cStringIO

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
    def __init__(self,port=8080):
        self.callbacks=[]
        self.port = port
        
    def sniffear(self,count = None):
        if count == None:
            sniff(prn=self.callCallbacks, filter='tcp port %s'%(self.port))
        else:
            sniff(prn=self.callCallbacks, filter='tcp port %s'%(self.port), count = count)
        
class HTTPAssembler(object):
    
    _methods = dict.fromkeys((
        'GET', 'PUT', 'ICY',
        'COPY', 'HEAD', 'LOCK', 'MOVE', 'POLL', 'POST',
        'BCOPY', 'BMOVE', 'MKCOL', 'TRACE', 'LABEL', 'MERGE',
        'DELETE', 'SEARCH', 'UNLOCK', 'REPORT', 'UPDATE', 'NOTIFY',
        'BDELETE', 'CONNECT', 'OPTIONS', 'CHECKIN',
        'PROPFIND', 'CHECKOUT', 'CCM_POST',
        'SUBSCRIBE', 'PROPPATCH', 'BPROPFIND',
        'BPROPPATCH', 'UNCHECKOUT', 'MKACTIVITY',
        'MKWORKSPACE', 'UNSUBSCRIBE', 'RPC_CONNECT',
        'VERSION-CONTROL',
        'BASELINE-CONTROL'
        ))
    _proto = 'HTTP'
    
    def __init__(self,port=8080):
        self.port = port
        self.paquetes={}
        self.ultimoPaquete = None
    
        
    def nuevo_paquete(self,pkt):
        
        #HACK: parece que scapy escucha 2 veces los paquetes si el proxy esta en su mismo host
        if self.ultimoPaquete == pkt:
            return
        self.ultimoPaquete = pkt
        
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
        
    def _comienzoDeRequest(self,buf):
        f = cStringIO.StringIO(buf)
        line = f.readline()
        l = line.strip().split()
        if len(l) != 3 or l[0] not in self._methods or \
           not l[2].startswith(self._proto):
            return False
        else:
            return True
    
    def _comienzoDeResponse(self,buf):
        f = cStringIO.StringIO(buf)
        line = f.readline()
        l = line.strip().split(None, 2)
        if len(l) < 2 or not l[0].startswith(self.__proto) or not l[1].isdigit():
            return False
        else:
            True
        
    def request(self,pkt):
        cuadrupla = self._get_cuadrupla(pkt)
        if not cuadrupla in self.paquetes and not self._comienzoDeRequest(pkt.getlayer(Raw).load):
            return
        self._agregarPaquete(pkt)
        try:
            r = Request(self.paquetes[cuadrupla])
            del self.paquetes[cuadrupla]
            self._persistirRequest(cuadrupla,r)

        except:
            pass
        
        
    def response(self,pkt):
        cuadrupla = self._get_cuadrupla(pkt)
        if not cuadrupla in self.paquetes and not self._comienzoDeResponse(pkt.getlayer(Raw).load):
            return
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
hs.sniffear()
print ha.paquetes


    