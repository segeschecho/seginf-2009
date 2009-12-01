
from persistencia import *
import re
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.traits.ui.menu import OKButton, CancelButton
from latex import LatexFactory
from reporte import Reporte
import CairoPlot

class NonHTTP(Reporte):
    verbose = Bool(False)
    render = Instance(LatexFactory)
    plotTraficoPorUsuario = Bool(True)
    cantInfractores = Range(value=5,low=1,high=10)

    view = View('verbose', 'plotTraficoPorUsuario', 'cantInfractores', buttons=[OKButton, CancelButton])

    
    def ejecutar(self,desde,hasta):
        self.render = LatexFactory()
        self.render.chapter("Protocolos de aplicacion utilizados")
            
        self.render.negrita("Periodo: %s - %s"%(desde,hasta))
        self.render.nuevaLinea()
        distribucionTrafico = self.obtenerDistribucionTrafico(desde,hasta)
        self.render.section("Distribucion del trafico segun protocolo de aplicacion")
        self.render.figure(self.graficar(distribucionTrafico["trafico"], "/Distribucion_trafico.png"))
        infractores = self.obtenerInfractores(distribucionTrafico)
        if not distribucionTrafico["huboInfracciones"]:
            self.render.negrita("No hubo usuarios que utilizaran SSH")
        else:
            if self.verbose:
                self.render.negrita("IPs desde los cuales se utilizo el servicio de SSH")
                self.render.itemize(infractores, "requests")
            clientes = self.obtenerClientes(distribucionTrafico)
            if clientes != []:
                self.render.section("Clientes de software mas utilizados")
                self.render.figure(self.graficar(clientes,'/ClientesSSH.png'))
            #if self.plotTraficoPorUsuario:
                #masInfractores = self.obtenerLosMasInfractores(infractores)
                #self.graficarVarios()
                
        return self.render.generarOutput()

    def obtenerInfractores(self, distribucionTrafico):
        return distribucionTrafico["traficoPorUsuario"]

    def obtenerClientes(self, distribucionTrafico):
        return distribucionTrafico["clientes"]
        
    def obtenerDistribucionTrafico(self, desde,hasta):
        distribucionTrafico = dict()
        clientes = dict()
        trafico = dict()
        traficoPorUsuario = dict()
        a = self.obtenerRequestsNoHTTP(desde,hasta)
        requestTotales = 0
        requestSSH = 0
        requestSSL = 0
        requestHTTP = 0
        huboInfracciones = False
        for each in a:
            requestTotales+=1
            if "SSH-" in each.body:
                huboInfracciones = True
                requestSSH+=1
                matcher = re.search('SSH-\d.\d+-(\w+)', each.body)
                cliente = matcher.group(1)
                if cliente in clientes:
                    clientes[cliente]= clientes[cliente] + 1
                else:
                    clientes[cliente] = 1
                infractor = each.ipOrigen
                self.agregarTrafico(traficoPorUsuario,each.ipOrigen,"traficoSSH")
            else:
                self.agregarTrafico(traficoPorUsuario,each.ipOrigen,"otros")

        a = self.obtenerRequests(desde,hasta)
        for each in a:
            requestTotales+=1
            requestHTTP+=1
            usuario = each.ipOrigen
            self.agregarTrafico(traficoPorUsuario,usuario,"traficoHTTP")
        a = self.obtenerResponses(desde,hasta)
        for each in a:
            requestTotales+=1
            requestHTTP+=1
            usuario = each.ipDestino
            self.agregarTrafico(traficoPorUsuario,usuario,"traficoHTTP")

        a = self.obtenerResponsesNoHTTP(desde,hasta)
        for each in a:
            requestTotales+=1
            if "SSH-" in each.body:
                huboInfracciones = True
                requestSSH+=1
                infractor = each.ipDestino
                self.agregarTrafico(traficoPorUsuario,infractor,"traficoSSH")
            else:
                self.agregarTrafico(traficoPorUsuario,each.ipOrigen,"otros")
                
        trafico["traficoSSH"] = requestSSH
        trafico["traficoSSL"] = requestSSL
        trafico["traficoHTTP"] = requestHTTP
        trafico["otros"] = requestTotales - requestSSH - requestSSL - requestHTTP
        distribucionTrafico["trafico"] = trafico
        distribucionTrafico["clientes"] = clientes
        distribucionTrafico["traficoPorUsuario"] = traficoPorUsuario
        distribucionTrafico["huboInfracciones"] = huboInfracciones
        return distribucionTrafico

    def graficar(self, distribucionTrafico, nombrePng):
        nombre = self.directorio + nombrePng
        CairoPlot.pie_plot(nombre, distribucionTrafico, 800, 500,shadow = True, gradient = True)
        return nombre

    def agregarTrafico(self, dic, usuario, trafico):
        if (usuario in dic) and (trafico in dic[usuario]):
            dic[usuario][trafico] += 1
        else:
            if not (usuario in dic):
                dic[usuario] = dict()
            dic[usuario][trafico] = 1

    def obtenerLosMasInfractores(infractores, cantInfractores):
        cantInfracciones = dict()
        for infractor in infractores:
            cantI = infractor["traficoSSH"]
            if cantI in cantInfracciones:
                cantInfracciones[cantI] = cantInfracciones[cantI].append(infractor)
            else:
                cantInfracciones[cantI] = [].append(infractor)
        


