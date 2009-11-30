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
    verbose = Bool
    render = Instance(LatexFactory)
    
    def ejecutar(self,desde,hasta):
        self.render = LatexFactory()
        self.render.chapter("Protocolos de aplicacion utilizados")
            
        self.render.negrita("Periodo: %s - %s"%(desde,hasta))
        self.render.nuevaLinea()
        distribucionTrafico = self.obtenerDistribucionTrafico(desde,hasta)
        self.render.section("Distribucion del trafico segun protocolo de aplicacion")
        #self.render.figure(self.graficarDistribucion(distribucionTrafico))
        infractores = self.obtenerInfractores(distribucionTrafico)

        if infractores == []:
            self.render.negrita("No hubo usuarios que utilizaran SSH")
        else:
            if self.verbose:
                self.render.negrita("IPs desde los cuales se utilizo el servivio de SSH")
                self.render.itemize(infractores, "requests")
            self.render.section("Clientes de software mas utilizados")
            clientes = self.obtenerClientes(distribucionTrafico)
            #self.render.figure(self.graficarClientes(clientes))
        return self.render.generarOutput()

    def obtenerInfractores(self, distribucionTrafico):
        return distribucionTrafico["infractores"]

    def obtenerClientes(self, distribucionTrafico):
        return distribucionTrafico["clientes"]
        
    def obtenerDistribucionTrafico(self, desde,hasta):
        distribucionTrafico = dict()
        clientes = dict()
        infractores = dict()
        trafico = dict()
        a = self.obtenerRequestsNoHTTP(desde,hasta)
        requestTotales = 0
        requestSSH = 0
        requestSSL = 0
        for each in a:
            requestTotales+=1
            if "SSH-" in each.body:
                requestSSH+=1
                matcher = re.search('SSH-\d.\d+-(\w+)', each.body)
                cliente = matcher.group(1)
                if cliente in clientes:
                    clientes[cliente]= clientes[cliente] + 1
                else:
                    clientes[cliente] = 1
                infractor = each.ipOrigen
                if infractor in infractores:
                    infractores[infractor] = infractores[infractor] + 1
                else:
                    infractores[infractor] = 1
                
        trafico["traficoSSH"] = requestSSH
        trafico["traficoSSL"] = requestSSL
        trafico["otros"] = requestTotales - requestSSH - requestSSH
        distribucionTrafico["trafico"] = trafico
        distribucionTrafico["clientes"] = clientes
        distribucionTrafico["infractores"] = infractores
        return distribucionTrafico

    def graficarDistribucion(self, distribucionTrafico):
        return CairoPlot.pie_plot("Distribucion_trafico.png", distribucionTrafico["trafico"], 800, 500,shadow = True, gradient = True)

    def graficarClientes(self, clientes):
        return CairoPlot.pie_plot("Clientes.png", clientes, 800, 500,shadow = True, gradient = True)



