#!/usr/bin/python
# -*- coding: utf-8 -*-
from persistencia import *
import re
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.traits.ui.menu import OKButton, CancelButton
from latex import LatexFactory
from reporte import Reporte
import CairoPlot
import operator
import binascii

class NonHTTP(Reporte):
    verbose = Bool(False)
    render = Instance(LatexFactory)
    plotTraficoPorUsuario = Bool(True)
    plotClientes = Bool(True)
    cantInfractores = Range(value=5,low=1,high=10)
    plotHost = Bool(True)

    #directorio = "tmp/reporToolTemp"

    view = View('verbose', 'plotTraficoPorUsuario', 'cantInfractores', 'plotClientes', 'plotHost', buttons=[OKButton, CancelButton])

    
    def ejecutar(self,desde,hasta):
        self.render = LatexFactory()
        self.render.chapter("Protocolos de aplicaci'on utilizados")
            
        self.render.negrita("Periodo: %s - %s"%(desde,hasta))
        self.render.nuevaLinea()
        distribucionTrafico = self.obtenerDistribucionTrafico(desde,hasta)
        if distribucionTrafico["total"] == 0:
            self.render.negrita("No hubo trafico de ning'un tipo")
            return self.render.generarOutput()
        self.render.section("Distribucion del tr'afico seg'un protocolo de aplicaci'on")
        self.render.figure(self.graficar(distribucionTrafico["trafico"], "/DistribucionTrafico.png"))
        infractores = self.obtenerInfractores(distribucionTrafico)
        if not distribucionTrafico["huboInfracciones"]:
            self.render.negrita("No hubo usuarios que utilizaran SSH")
        else:
            if self.verbose:
                self.render.negrita("IPs desde los cuales se utilizo el servicio de SSH")
                self.render.itemize(infractores, "requests")
            if self.plotClientes:
                clientes = self.obtenerClientes(distribucionTrafico)
                if clientes != []:
                    self.render.section("Clientes de software mas utilizados")
                    self.render.figure(self.graficar(clientes,'/ClientesSSH.png'))
            if self.plotTraficoPorUsuario:
                masInfractores = self.obtenerLosMasInfractores(infractores, self.cantInfractores)
                self.render.section("Distribuci'on de tr'afico seg'un protocolo de aplicaci'on por usuario")
                self.render.negrita("Se muestran los gr'aficos para (a lo sumo) los %s usuarios mas infractores"%self.cantInfractores)
                self.graficarVarios(masInfractores)
            if self.plotHost:
                self.render.section("Distribuci'on de tr'afico SSH seg'un host")
                self.render.figure(self.graficar(distribucionTrafico["hostSSH"],"/DistribucionHostSSH.png"))
                
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
        requestTotales = 0
        requestSSH = 0
        requestTLS = 0
        requestSSL = 0
        requestHTTP = 0
        hostSSH = dict()
        huboInfracciones = False
        a = self.obtenerRequestsNoHTTP(desde,hasta)
        for each in a:
            requestTotales+=1
            if self.esSSH(each.body):
                huboInfracciones = True
                requestSSH+=1
                self.obtenerCliente(each.body,clientes)
                self.obtenerHost(each, hostSSH)
                self.agregarTrafico(traficoPorUsuario,each.ipOrigen,"traficoSSH")
            else:
                if self.esSSL(each.body):
                    requestSSL+=1
                    self.agregarTrafico(traficoPorUsuario,each.ipOrigen,"traficoSSL")
                else:
                    if self.esTLS(each.body):
                        requestTLS+=1
                        self.agregarTrafico(traficoPorUsuario,each.ipOrigen,"traficoTLS")
                    else:
                        self.agregarTrafico(traficoPorUsuario,each.ipOrigen,"otros")


        a = self.obtenerRequests(desde,hasta)
        for each in a:
            requestTotales+=1
            requestHTTP+=1
            self.agregarTrafico(traficoPorUsuario,each.ipOrigen,"traficoHTTP")
            
        a = self.obtenerResponses(desde,hasta)
        for each in a:
            requestTotales+=1
            requestHTTP+=1
            self.agregarTrafico(traficoPorUsuario,each.ipDestino,"traficoHTTP")
            

        a = self.obtenerResponsesNoHTTP(desde,hasta)
        for each in a:
            requestTotales+=1
            if self.esSSH(each.body):
                huboInfracciones = True
                requestSSH+=1
                self.agregarTrafico(traficoPorUsuario,each.ipDestino,"traficoSSH")
            else:
                if self.esSSL(each.body):
                    requestSSL+=1
                    self.agregarTrafico(traficoPorUsuario,each.ipDestino,"traficoSSL")
                else:
                    if self.esTLS(each.body):
                        requestTLS+=1
                        self.agregarTrafico(traficoPorUsuario,each.ipDestino,"traficoTLS")
                    else:
                        self.agregarTrafico(traficoPorUsuario,each.ipDestino,"otros")

                
        trafico["traficoSSH"] = requestSSH
        trafico["traficoSSL"] = requestSSL
        trafico["traficoTLS"] = requestTLS
        trafico["traficoHTTP"] = requestHTTP
        trafico["otros"] = requestTotales - requestSSH - requestSSL - requestHTTP - requestTLS
        distribucionTrafico["total"] = requestTotales
        distribucionTrafico["trafico"] = trafico
        distribucionTrafico["clientes"] = clientes
        distribucionTrafico["traficoPorUsuario"] = traficoPorUsuario
        distribucionTrafico["huboInfracciones"] = huboInfracciones
        distribucionTrafico["hostSSH"] = hostSSH
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

    def obtenerLosMasInfractores(self, infractoresDic, cantInfractores):
        infractores = infractoresDic.items()
        infractores.sort(key=lambda x: ("traficoSSH" in x[1] and x[1]["traficoSSH"]) or 0, reverse = True)
        masInfractores = infractores[0:cantInfractores-1]
        return filter(lambda x: "traficoSSH" in x[1],masInfractores)

    def graficarVarios(self,masInfractores):
        for infractor in masInfractores:
            self.render.subsection("Distribuci'on del tr'afico en protocolos de aplicaci'on del usuario %s"%infractor[0])
            self.render.figure(self.graficar(infractor[1],"/Infractor%s.png"%infractor[0].replace(".","-")))

    def esSSH(self,body):
        return "SSH-" in body

    def esSSL(self,body):
        return binascii.hexlify(body[1:3]) == "0300"

    def esTLS(self,body):
        return binascii.hexlify(body[1:3]) == "0301" or binascii.hexlify(body[1:3]) == "0302" or binascii.hexlify(body[1:3]) == "0303"

    def obtenerCliente(self,body,clientes):
        matcher = re.search('SSH-\d.\d+-(\w+)', body)
        cliente = matcher.group(1)
        if cliente in clientes:
            clientes[cliente]= clientes[cliente] + 1
        else:
            clientes[cliente] = 1

    def obtenerHost(self, request, hosts):
        id = request.request
        s = get_session()
        query = s.query(MensajeHTTP).filter(MensajeHTTP.id == id)
        mensajeConnect = query.all()[0]
        host = mensajeConnect.headers["host"]
        if host in hosts:
            hosts[host]= hosts[host] + 1
        else:
            hosts[host] = 1
        
