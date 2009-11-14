#!/usr/bin/env python

from scapy.all import *
from dpkt.http import Request, Response

from persistencia import get_session, RequestHTTP, ResponseHTTP, MensajeHTTP, RequestNoHTTP, ResponseNoHTTP
import sys
import cStringIO
import datetime

STANDARD_PORT = 8080
DEFAULT_CAP ='captura.cap'

#TODO: hacer la tabla de victoria
#FIXME: ojo con las requests sin responses

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
        self.persistirMensaje(cuadrupla,mensaje,ResponseHTTP,timestamp,
                              mensaje.status,mensaje.reason)
        
    
    def persistirRequest(self,cuadrupla, mensaje, timestamp,response):
        self.persistirMensaje(cuadrupla,mensaje,RequestHTTP,timestamp,
                              mensaje.method,mensaje.uri,response)
        
        
        
    def persistirMensaje(self,cuadrupla, mensaje, clase, timestamp,arg0,arg1,arg2=None):
        try:
            s = get_session()
            ipOrigen, ipDestino, portOrigen, portDestino = cuadrupla
            
            if arg2 is None:
                print "aca tb llego"
                s.add(clase(ipOrigen, ipDestino, portOrigen, portDestino, mensaje.version,
                              mensaje.headers,mensaje.body, timestamp,arg0,arg1))
            else:
                
                s.add(clase(ipOrigen, ipDestino, portOrigen, portDestino, mensaje.version,
                              mensaje.headers,mensaje.body, timestamp,arg0,arg1,arg2))
            s.commit()
            self.ultimoId +=1
        except Exception, e:
            print e
            sys.exit(-1)
      
            

class Conversacion(object):

    persistidor = PersistidorHTTP()
    
    def __init__(self):
        self.cuadrupla = None
        self.request = None
        self.response= None
        self.datetimeRequest = None
        self.datetimeResponse = None
        
    def terminada(self):
        (ipDestino, ipOrigen, portDestino, portOrigen) = self.cuadrupla
        idResp = None
        if self.response:
            cuadruplaRepsonse = (ipOrigen, ipDestino, portOrigen, portDestino)
            self.persistidor.persistirResponse(cuadruplaRepsonse, self.response,
                                           self.datetimeResponse)
            idResp = self.persistidor.ultimoId
        if self.request:
            self.persistidor.persistirRequest(self.cuadrupla,self.request,
                                          self.datetimeRequest, idResp)
        
        

class Conexion(object):
    def __init__(self,paquete,secuencia,datetime):
        self.datetime = datetime
        self.paquetes = paquete
        self.secuencias = secuencia
        

class IdentificadorDeHTTP(object):
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
    
    _proto = 'HTTP'
    
    #Cheque que un paquete pueda ser el comienzo de un request
    def _comienzoDeRequest(self,buf):
        f = cStringIO.StringIO(buf)
        line = f.readline()
        l = line.strip().split()
        return not( len(l) != 3 or l[0] not in self._methods or \
           not l[2].startswith(self._proto))
            
        
    #Chequea que un paquete pueda ser el comienzo de una response
    def _comienzoDeResponse(self,buf):
        f = cStringIO.StringIO(buf)
        line = f.readline()
        l = line.strip().split(None, 2)
        return not(len(l) < 2 or not l[0].startswith(self._proto)\
                   or not l[1].isdigit())
    
    
class ConexionPotencialmenteNoHTTP(object):
    
    def __init__(self,cuadrupla):
        self.body = ""
        self.cuadrupla = cuadrupla
        self.conBody = False
        self.datetime = datetime.datetime.now()
        self.identificadorHTTP = IdentificadorDeHTTP()
        self.seQueNoEs = None
        
    
    def noEsHTTP(self):
        if not self.conBody:
            return True
        elif self.seQueNoEs:
            return seQueNoEs
        elif self.seQueNoEs == None:
            self.seQueNoEs = not (self.identificadorHTTP._comienzoDeRequest(self.body) \
                             or self.identificadorHTTP._comienzoDeResponse(self.body))
        return seQueNoEs
            

    def agregarPaquete(self,chunk):
        self.body += chunk.load
            
    
class PersistidorNoHTTP(object):
    
    def __init__(self,port=STANDARD_PORT):
        self.port = port
    
    def persistir(self, mensaje):
        s = get_session()
        ipOrigen, ipDestino, portOrigen, portDestino = mensaje.cuadrupla
        if portOrigen == self.port:
            s.add(ResponseNoHTTP(ipOrigen, ipDestino, portOrigen, portDestino,mensaje.body,mensaje.datetime))
        else:
            s.add(RequestNoHTTP(ipOrigen, ipDestino, portOrigen, portDestino,mensaje.body,mensaje.datetime))
        s.commit()


class NoHTTPAssembler(object):
    
    def __init__(self,port=STANDARD_PORT):
        self.port = port
        
        self.conexiones = {}
        
        self.identificadorHTTP = IdentificadorDeHTTP()
        
        self.ultimoPaquete = None
        
        self.persistidorNoHTTP = PersistidorNoHTTP(self.port)
    
    def _get_cuadrupla(self,pkt):
        pktIP = pkt.getlayer(IP)
        ipOrigen = pktIP.src
        ipDestino = pktIP.dst
        pktTCP = pktIP.getlayer(TCP)
        portOrigen = pktTCP.sport
        portDestino = pktTCP.dport
        return (ipOrigen,ipDestino,portOrigen,portDestino)
        
    def nuevoPaquete(self,pkt):
        #HACK: parece que scapy escucha 2 veces los paquetes si el proxy esta en su mismo host
        if self.ultimoPaquete == pkt:
            return
        self.ultimoPaquete = pkt 
        cuadrupla = self._get_cuadrupla(pkt)
        if pkt.getlayer(TCP).flags & 2 > 0: #flag de syn
            self.conexiones[cuadrupla] = ConexionPotencialmenteNoHTTP(cuadrupla)
        if cuadrupla in self.conexiones:
            if pkt.lastlayer().haslayer(Raw):
                self.conexiones[cuadrupla].agregarPaquete(pkt.getlayer(Raw))
                if not self.conexiones[cuadrupla].noEsHTTP():
                    del self.conexiones[cuadrupla]
                    return
            if (pkt.getlayer(TCP).flags & 1) > 0: #flag de fin    
                self.persistidorNoHTTP.persistir(self.conexiones[cuadrupla])
                del self.conexiones[cuadrupla]
                return
            if (pkt.getlayer(TCP).flags & 4) > 0: #flag de reset    
                del self.conexiones[cuadrupla]
                return

        
        
            
            

class HTTPAssembler(object):
    


    def __init__(self,port=STANDARD_PORT):
        # port -> Puerto del proxy al que le vamos a prestar atencion
        self.port = port
        
        self.conexiones = {}
        # HACK: esta variable la usamos por si corremos el sniffer en la misma
        # maquina que el proxy y scappy se vuelve loco
        self.ultimoPaquete = None
        
        self.identificadorHTTP = IdentificadorDeHTTP()
    
        
        
        self.conversaciones = {}
        
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
        if cuadrupla in self.conexiones:
            if pkt.getlayer(TCP).seq in self.conexiones[cuadrupla].secuencias:
                return
            self.conexiones[cuadrupla].paquetes+=pkt.getlayer(Raw).load
            self.conexiones[cuadrupla].secuencias.append(pkt.getlayer(TCP).seq)
        else:
            self.conexiones[cuadrupla] = Conexion(pkt.getlayer(Raw).load,
                                                   [pkt.getlayer(TCP).seq],
                                                   datetime.datetime.now())

            

    #Metodo para atender paquetes que son potenciales request        
    def request(self,pkt):
        cuadrupla = self._get_cuadrupla(pkt)
        #Si no tenemos la cuadrupla ya guardada, entonces tiene q iniciarse una request
        if not cuadrupla in self.conexiones and not self.identificadorHTTP._comienzoDeRequest(pkt.getlayer(Raw).load):
            return
        #Agrego el fragmento que llego
        self._agregarPaquete(pkt)
        try:
            #Intento armar una request
            r = Request(self.conexiones[cuadrupla].paquetes)
            timestamp = self.conexiones[cuadrupla].datetime
            #Si pude, borro los fragmentos
            self._borrarCuadrupla(cuadrupla)
            if not cuadrupla in self.conversaciones:
                self.conversaciones[cuadrupla] = Conversacion()
                self.conversaciones[cuadrupla].request = r
                self.conversaciones[cuadrupla].datetimeRequest = timestamp
                self.conversaciones[cuadrupla].cuadrupla = cuadrupla
            

        except Exception, e:
            #No pude armar el request todavia
            print e, "pataaaa"
            pass
        
    #Saca a una cuadrupla de los diccionarios de paquetes y secuencias
    def _borrarCuadrupla(self, cuadrupla):
        del self.conexiones[cuadrupla]
    
    #Metodo para atender potenciales responses (similar al de las requests)
    def response(self,pkt):
        cuadrupla = self._get_cuadrupla(pkt)
        if not cuadrupla in self.conexiones and not self.identificadorHTTP._comienzoDeResponse(pkt.getlayer(Raw).load):
            return
        self._agregarPaquete(pkt)
        try:
            r = Response(self.conexiones[cuadrupla].paquetes)
            timestamp = self.conexiones[cuadrupla].datetime
            self._borrarCuadrupla(cuadrupla)
            (ipDestino, ipOrigen, portDestino, portOrigen) = cuadrupla
            cuadruplaRequest = (ipOrigen, ipDestino, portOrigen, portDestino)

            if cuadruplaRequest in self.conversaciones:
                self.conversaciones[cuadruplaRequest].response = r
                self.conversaciones[cuadruplaRequest].datetimeResponse = timestamp
                
                self.conversaciones[cuadruplaRequest].terminada()
                
                del self.conversaciones[cuadruplaRequest]
            else:
                c = Conversacion()
                c.response = r
                c.datetimeResponse = timestamp
                c.cuadrupla = cuadruplaRequest
                c.terminada()
                
                
        except Exception, e:
            print e, "pitaaaa"
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
hn = NoHTTPAssembler(port = puerto)
hs.addCallback(hn.nuevoPaquete)
hs.sniffear()

if options.dump_file:
    ca.dumpear()

#vaciamos los requests que quedaron sin respuesta (esto hay q mejorarlo)
for each in ha.conversaciones:
    ha.conversaciones[each].terminada()


    