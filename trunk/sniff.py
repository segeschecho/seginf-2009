#!/usr/bin/env python

from scapy.all import *
from dpkt.http import Request, Response

from persistencia import get_session, RequestHTTP, ResponseHTTP, MensajeHTTP, Conversacion
import sys
import cStringIO
import datetime

STANDARD_PORT = 8080
DEFAULT_CAP ='captura.cap'

# Clase base de sniffer
# Permite agregarle callbacks para que se llamen cada vez que llegue un paquete
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
            
# Clase que permite sniffear trafico tcp al puerto donde atiende el proxy
class HTTPandHTTPSSniffer(Sniffer):
    def __init__(self,port=STANDARD_PORT):
        self.callbacks=[]
        self.port = port
        
    def sniffear(self,count = None):
        if count == None:
            sniff(prn=self.callCallbacks, filter='tcp port %s'%(self.port))
        else:
            sniff(prn=self.callCallbacks, filter='tcp port %s'%(self.port), count = count)

#Clase que guarda las response y request que vamos capturando en una base de datos
class PersistidorHTTP(object):
    def __init__(self):
        s = get_session()
        self.ultimoId = s.query(MensajeHTTP).count()
    
    def persistirResponse(self,cuadrupla, mensaje,timestamp):
        self.persistirMensaje(cuadrupla,mensaje,ResponseHTTP,timestamp,mensaje.status,mensaje.reason)
        
    
    def persistirRequest(self,cuadrupla, mensaje, timestamp):
        self.persistirMensaje(cuadrupla,mensaje,RequestHTTP,timestamp,mensaje.method,mensaje.uri)
        
    
    def persistirMensaje(self,cuadrupla, mensaje, clase, timestamp,arg0,arg1):
        try:
            s = get_session()
            ipOrigen, ipDestino, portOrigen, portDestino = cuadrupla
            s.add(clase(ipOrigen, ipDestino, portOrigen, portDestino, mensaje.version,
                              mensaje.headers,mensaje.body, timestamp,arg0,arg1))
            s.commit()
            self.ultimoId +=1
        except Exception, e:
            print e
            sys.exit(-1)
            
    def persistirConversacion(self,req,resp,timestamp):
        try:
            s = get_session()
            
            s.add(Conversacion(req,resp,timestamp))
            s.commit()
        except Exception, e:
            print e
            sys.exit(-1)
            

#TODO: refactor de esta clase, cambiar los diccionarios por clases para "conexiones"
#Clase que toma los mensajes que llegan y va armando los mensajes HTTP         
class HTTPAssembler(object):
    
    #Metodos posibles para un request
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
    
    #Nombre del protcolo que aparece en los mensajes
    _proto = 'HTTP'

    def __init__(self,port=STANDARD_PORT):
        # port -> Puerto del proxy al que le vamos a prestar atencion
        self.port = port
        # Diccionario de cuadruplas (ipOrigen,ipDestino,portOrigen,portDestino)
        # en fragmentos de mensajes HTTP
        self.paquetes={}
        # Diccionario de cuadruplas en numeros de secuencia, es para no appendear
        # a los mensajes contenido de retrasmisiones
        self.secuencias ={}
        # HACK: esta variable la usamos por si corremos el sniffer en la misma
        # maquina que el proxy y scappy se vuelve loco
        self.ultimoPaquete = None
        
        self.datetimes = {}
        
        self.persistidor = PersistidorHTTP()
        
        self.requestSinResponses = {}
        
    def nuevo_paquete(self,pkt):
        
        #HACK: parece que scapy escucha 2 veces los paquetes si el proxy esta en su mismo host
        if self.ultimoPaquete == pkt:
            return
        self.ultimoPaquete = pkt
        
        # chequeo que el paquete no sea solo de padding o tcp vacio
        # Si tiene contenido tiene capa Raw
        if not pkt.lastlayer().haslayer(Raw):
            return
        
        # Chequeamos que el paquete sea desde o hacia el proxy, sino lo ignoramos
        pktTCP = pkt.getlayer(TCP)
        portOrigen = pktTCP.sport
        portDestino = pktTCP.dport
        if not(portOrigen == self.port or portDestino == self.port):
            return
        #Si viene del proxy es un response (potencialmente), sino es un request
        if portOrigen == self.port:
            self.response(pkt)
        else:
            self.request(pkt)
    
    def _agregarPaquete(self,pkt):
        cuadrupla = self._get_cuadrupla(pkt)
        if cuadrupla in self.paquetes:
            if pkt.getlayer(TCP).seq in self.secuencias[cuadrupla]:
                return
            self.paquetes[cuadrupla]+=pkt.getlayer(Raw).load
            self.secuencias[cuadrupla].append(pkt.getlayer(TCP).seq)
        else:
            self.paquetes[cuadrupla]=pkt.getlayer(Raw).load
            self.secuencias[cuadrupla] = [pkt.getlayer(TCP).seq]
            self.datetimes[cuadrupla] = datetime.datetime.now()

    #Cheque que un paquete pueda ser el comienzo de un request
    def _comienzoDeRequest(self,buf):
        f = cStringIO.StringIO(buf)
        line = f.readline()
        l = line.strip().split()
        if len(l) != 3 or l[0] not in self._methods or \
           not l[2].startswith(self._proto):
            return False
        else:
            return True
        
    #Chequea que un paquete pueda ser el comienzo de una response
    def _comienzoDeResponse(self,buf):
        f = cStringIO.StringIO(buf)
        line = f.readline()
        l = line.strip().split(None, 2)
        if len(l) < 2 or not l[0].startswith(self._proto) or not l[1].isdigit():
            return False
        else:
            return True

    #Metodo para atender paquetes que son potenciales request        
    def request(self,pkt):
        cuadrupla = self._get_cuadrupla(pkt)
        #Si no tenemos la cuadrupla ya guardada, entonces tiene q iniciarse una request
        if not cuadrupla in self.paquetes and not self._comienzoDeRequest(pkt.getlayer(Raw).load):
            return
        #Agrego el fragmento que llego
        self._agregarPaquete(pkt)
        try:
            #Intento armar una request
            r = Request(self.paquetes[cuadrupla])
            timestamp = self.datetimes[cuadrupla]
            #Si pude, borro los fragmentos
            self._borrarCuadrupla(cuadrupla)
            # y lo persisto
            self.persistidor.persistirRequest(cuadrupla,r,timestamp)
            self.requestSinResponses[cuadrupla] = self.persistidor.ultimoId

        except:
            #No pude armar el request todavia
            pass
        
    #Saca a una cuadrupla de los diccionarios de paquetes y secuencias
    def _borrarCuadrupla(self, cuadrupla):
        del self.paquetes[cuadrupla]
        del self.secuencias[cuadrupla]
        del self.datetimes[cuadrupla]
    
    #Metodo para atender potenciales responses (similar al de las requests)
    def response(self,pkt):
        cuadrupla = self._get_cuadrupla(pkt)
        if not cuadrupla in self.paquetes and not self._comienzoDeResponse(pkt.getlayer(Raw).load):
            return
        self._agregarPaquete(pkt)
        try:
            r = Response(self.paquetes[cuadrupla])
            timestamp = self.datetimes[cuadrupla]
            self._borrarCuadrupla(cuadrupla)
            self.persistidor.persistirResponse(cuadrupla,r,timestamp)
            (ipDestino, ipOrigen, portDestino, portOrigen) = cuadrupla
            cuadruplaRequest = (ipOrigen, ipDestino, portOrigen, portDestino)
            if cuadruplaRequest in self.requestSinResponses:
                self.persistidor.persistirConversacion(self.requestSinResponses[cuadruplaRequest],self.persistidor.ultimoId,timestamp)
                del self.requestSinResponses[cuadruplaRequest]
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
            
# Clase que permite hacer un archivo.cap para poder mirarlo por ejemplo con el
# wireshark
class CapDumper(object):
    def __init__(self,file='dump.cap'):
        self.file = file
        self.list = PacketList()
    
    def nuevoPaquete(self,pkt):
        self.list.append(pkt)
        
    def dumpear(self):
        if len(self.list) > 0:
            wrpcap(self.file, self.list)
        else:
            print "No se capturaron paquetes"

class VerbosePacketHandler(object):
    def nuevoPaquete(self,pkt):
        print pkt.summary()



from optparse import OptionParser
usage = "%prog [opciones]"
parser = OptionParser(usage=usage)

parser.add_option("-p", "--port", dest="proxy_port", default=STANDARD_PORT,
                  help="Puerto donde atiende el proxy", metavar="PORT")
parser.add_option("-d", "--dump", dest="dump_file",
                  help="Generar un archivo con las capturas", metavar="DUMP")
parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true",
                  help="mostrar informacion adicional")



########
# Main #
########

(options, args) = parser.parse_args()

puerto = int(options.proxy_port)
hs = HTTPandHTTPSSniffer(port=puerto)
ha = HTTPAssembler(port=puerto)
hs.addCallback(ha.nuevo_paquete)

if options.dump_file:
    ca = CapDumper(options.dump_file)
    hs.addCallback(ca.nuevoPaquete)

if options.verbose:
    vph = VerbosePacketHandler()
    hs.addCallback(vph.nuevoPaquete)
    
hs.sniffear()

if options.dump_file:
    ca.dumpear()




    
