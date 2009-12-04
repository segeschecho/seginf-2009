#!/usr/bin/env python
from enthought.traits.api import *
from enthought.traits.ui.api import *
from collections import defaultdict
from datetime import date
import CairoPlot
from reporte import Reporte
from enthought.traits.ui.menu import OKButton, CancelButton
from latex import LatexFactory

class EvolucionMensual(Reporte):
    sitio_1=String('www.google.com')
    sitio_2=String('www.facebook.com')
    sitio_3=String('mail.google.com')
    sitio_4=String('www.taringa.net')
    sitio_5=String('www.fotolog.com')
    render = LatexFactory()
    view = View('sitio_1','sitio_2','sitio_3','sitio_4','sitio_5',buttons=[OKButton, CancelButton])
    
    def largo(self,msj):
        res = len(msj.body)
        for each in msj.headers:
            res += len(msj.headers[each])
        return res
        
    
    
    def ejecutar(self,desde,hasta):
        self.render = LatexFactory()
        self.render.chapter("Evoluci'on del tr'afico")
        requests, responses = self._obtenerTodoEnRango(desde,hasta)
        responses = dict(((x.id,x) for x in responses))
        sitios = [self.sitio_1, self.sitio_2, self.sitio_3, self.sitio_4, self.sitio_5]
        reqsXSitio = defaultdict(lambda:[])
        respXSitio = defaultdict(lambda:[])
        
        for each in requests:
            if 'host' in each.headers:
                dominio = each.headers['host']
                if dominio in sitios:
                    reqsXSitio[dominio].append(each)
                    if each.response in responses:
                        respXSitio[dominio].append(responses[each.response])
        
        
                    
        
        requestsPorMes = defaultdict(lambda:defaultdict(lambda:0))
        traficoPorMes = defaultdict(lambda:defaultdict(lambda:0))
        for sitio in reqsXSitio:
            for req in reqsXSitio[sitio]:
                requestsPorMes[sitio][str(req.datetime.month)+"/"+str(req.datetime.year)]+=1
                traficoPorMes[sitio][str(req.datetime.month)+"/"+str(req.datetime.year)]+=self.largo(req)
                
        for sitio in respXSitio:
            for resp in respXSitio[sitio]:
                traficoPorMes[sitio][str(resp.datetime.month)+"/"+str(resp.datetime.year)]+=self.largo(resp)
                
        a = date(desde.year,desde.month,1)
        
        #creo los labels
        labels = []
        
        while a <= hasta:
            labels.append(str(a.month)+"/"+str(a.year))
            if a.month < 12:
                a = date(a.year,a.month+1,1)
            else:
                a = date(a.year+1,1,1)
        
        
        toGraph = defaultdict(lambda:[])
        toGraph2 = defaultdict(lambda:[])
        
        max = 0
        max2 = 0
        import random
        for sitio in sitios:
            dic = requestsPorMes[sitio]
            dic2 = traficoPorMes[sitio]
            for each in labels:
                toGraph[sitio].append(dic[each])
                toGraph2[sitio].append(dic2[each])
                if max < dic[each]:
                    max = dic[each]
                if max2 < dic2[each]:
                    max2 = dic2[each]
                    
        v_labels = [str(x) for x in [0 ,max/4.0,max/2.0,3.0*max/4.0,max]]
        v_labels2 = [str(x) for x in [0 ,max2/4.0,max2/2.0,3.0*max2/4.0,max2]]
        cosa = [ toGraph[c] for c in toGraph]
        cosa2 = [ toGraph2[c] for c in toGraph2]
        
        colors = [(1.0,0.0,1.0),(0.0,1.0,1.0),(1.0,0.0,0.0),(0.0,1.0,0.0),(0.0,0.0,1.0)]
        nroColor = 0
        for (r,g,b) in colors:
            self.render.definirColor("color"+str(nroColor),r,g,b)
            nroColor+=1
        
        ###########################################################
        ## Grafico por requests ##
        ###########################################################
        nombre = self.directorio+'/seguimiento_requests.png'
        
        CairoPlot.dot_line_plot(nombre,cosa,800,
            	                600,series_colors=colors,h_labels = labels, axis = True, grid=True,
                                v_labels = v_labels,dots=True, )
        self.render.figure(nombre,tamano=14,caption='Cantidad de requests por sitio')
        
        nroColor = 0
        
        for each in toGraph:
            self.render.enColor(str(each),"color"+str(nroColor))
            nroColor+=1
        
        ###########################################################
        ## Grafico por trafico ##
        ###########################################################
        
        nombre = self.directorio+'/seguimiento_trafico.png'
        CairoPlot.dot_line_plot(nombre,cosa2,800,
            	                600,series_colors=colors,h_labels = labels, axis = True, grid=True,
                                v_labels = v_labels,dots=True, )
        self.render.figure(nombre,tamano=14,caption = 'Trafico en bytes')
        nroColor = 0
        
        for each in toGraph2:
            self.render.enColor(str(each),"color"+str(nroColor))
            nroColor+=1
        res =  self.render.generarOutput()
        del self.render
        return res

