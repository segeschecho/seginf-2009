from persistencia import get_session, RequestHTTP, ResponseHTTP
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from reporte import Reporte
import CairoPlot
from collections import defaultdict
import os
from enthought.pyface.message_dialog import MessageDialog
from enthought.pyface.progress_dialog import ProgressDialog
from enthought.traits.ui.menu import OKButton, CancelButton
from latex import LatexFactory

import psyco

psyco.full()

#TODO: un poco de refactor no vendria mal
#TODO: mostrar datos junto con los graficos
#TODO: abstraer el latex a funciones q lo generen y no que sea inline de los metodos

class ListaNegra(Reporte):
    dicc = None
    render = LatexFactory()
    categoria = Str
    lista = File
    plotInfraccionesPorUsuario = Bool
    plotDominiosVistados = Bool
    plotDominiosVistadosPorUsuario = Bool
    plotPorcentajeDeRequests = Bool
    plotPorcentajePorUsuario = Bool
    plotPorcentajeDeTrafico = Bool
        
    view = View(Item('categoria',style='readonly'),
                'lista', 'plotInfraccionesPorUsuario',
                'plotDominiosVistados',
                'plotDominiosVistadosPorUsuario',
                'plotPorcentajeDeRequests',
                'plotPorcentajePorUsuario',
                'plotPorcentajeDeTrafico',
                buttons=[OKButton, CancelButton])
    
    
    def cargarLista(self):
        if self.dicc != None:
            return
        try:
            f = open(self.lista,'r')
        except Exception, e:
            MessageDialog(message="Imposible cargar el reporte a partir del archivo").open()
            raise e
        #self.dicc = Trie()
        
        lineas = f.readlines()
      
        self.dicc = set((unicode(x[:-1]) for x in lineas))

        
            
    def obtenerRequests(self,desde,hasta):
        s = get_session()
        d = datetime(desde.year,desde.month,desde.day)
        h = datetime(hasta.year,hasta.month,hasta.day)
        query = s.query(RequestHTTP)
        query.filter(RequestHTTP.datetime >= str(d) )
        query.filter(RequestHTTP.datetime <= str(h) )
        return query.all()
        
    
    def esta(self,nombre):
        nombre = unicode(nombre)
        cand = ""
        for each in reversed(nombre.split('.')):
            cand = each + cand
            if cand in self.dicc:
                print cand
                return cand
            cand = '.'+cand
        return None
            
    def ejecutar(self,desde,hasta):
    
        try:
            self.cargarLista()
        except Exception, e:
            print e
            return ""
        requests = self.obtenerRequests(desde,hasta)
        textito = 'Visitas a paginas prohibidas de la categoria %s'%self.categoria
        self.render.chapter(textito)
        self.render.negrita('Periodo: %s - %s'%(desde,hasta))
        self.render.nuevaLinea()
        if requests == []:
            self.render.negrita("No hay infracciones")
            return self.render.generarOutput
        
        else:
            self.render.texto("\\begin{itemize}\n")
            infractores = set()
            infracciones = defaultdict(lambda:0)
            requestsPorUsuarios = defaultdict(lambda:0)
            visitasADominios = defaultdict(lambda:0)
            dominiosVisitados = set()
            dominiosVisitadosPorUsuario = defaultdict(lambda:set())
            visitasPorUsuario = defaultdict(lambda:defaultdict(lambda:0))
            visitasTotales = 0
            encontre = False
            requestsInfractores = []
            for each in requests:
                if 'host' in each.headers:
                    print "host", each.headers['host']
                    domain = self.esta(each.headers['host'])
                    if domain != None:
                        self.render.texto("\\item IP: %s \n\n Sitio: %s \n\n fecha: %s" % \
                               (each.ipOrigen, domain, each.datetime))
                        infractores.add(each.ipOrigen)
                        infracciones[each.ipOrigen] += 1
                        dominiosVisitadosPorUsuario[each.ipOrigen].add(domain)
                        dominiosVisitados.add(domain)
                        visitasADominios[domain] += 1
                        visitasTotales +=1
                        visitasPorUsuario[each.ipOrigen][domain] +=1
                        encontre = True
                        requestsInfractores.append(each.id)
                requestsPorUsuarios[each.ipOrigen] += 1
            if not encontre:
                self.render.texto("\\item No hubo accesos a sitios de esta categoria\n")
                self.render.texto("\\end{itemize}\n")
                return self.render.generarOutput()
            self.render.texto("\\end{itemize}\n")
            
            
            self.plotearPorcentaje(len(requests), visitasTotales,desde,hasta)
            self.plotearPorcentajePorUsuario(infractores, infracciones, requestsPorUsuarios)
            self.plotearInfraccionesPorUsuario(infractores,infracciones,visitasTotales)
            self.plotearDominiosVisitadosPorUsuario(infractores,dominiosVisitadosPorUsuario,visitasPorUsuario)
            self.plotearDominiosVistados(dominiosVisitados, visitasADominios,visitasTotales,desde,hasta)
            self.plotearTrafico(requestsInfractores,dominiosVisitados,desde,hasta)
 
            return self.render.generarOutput()
    
    
    def plotearInfraccionesPorUsuario(self,infractores,infracciones,totales):
        y = [infracciones[i] for i in infractores]
        self.render.section('Infracciones por usuario en la categori %s'%\
                            self.categoria)
        maximo = max(y)
        self.render.texto('Las siguientes son las infracciones por usuario para\
                          sitios de la categoria %s'%self.categoria)
        aux = dict(zip(infracciones,y))
        self.render.itemize(aux, 'requests')
        if self.plotearInfraccionesPorUsuario:
            nombre = 'Infracciones_Usuario_%s.png'%self.categoria
            CairoPlot.bar_plot (nombre,
            y, 400, 300, 
            border = 20, grid = True, rounded_corners = True,
            h_labels=infractores,
            v_labels = ['0',str(maximo/4.0),str(maximo/2.0)
            ,str(3*maximo/4.0),str(maximo)],three_dimension=True)
            self.render.figure("%s/%s"%(os.getcwdu(), nombre), caption = \
                    'Cantidad de infracciones por usuario para la categoria %s,\
                    sobre un total de %s'%(self.categoria, totales))
        
        
    def plotearDominiosVisitadosPorUsuario(self,infractores,
                                           dominiosVisitadosPorUsuario,
                                           visitasPorUsuario):
        res = ""
        for each in infractores:
            res += self.visitadosPara(each,dominiosVisitadosPorUsuario[each],
                                 visitasPorUsuario[each])
        return res

    def visitadosPara(self,usr,dominios,cantPorDominio):
        d = dict([(dom, cantPorDominio[dom]) for dom in dominios])
        total = sum([cantPorDominio[dom] for dom in dominios])
        nombre = "dominios_%s_%s.png" % (self.categoria,usr.replace('.',''))
        CairoPlot.pie_plot(nombre,d, 1000,500,gradient=True,
            shadow=True
            )
        return \
        """
        \\begin{figure}[H]
        \\centering
        \\includegraphics[width=12cm]{%s/%s}
        \\caption{Dominios visitados por %s, categoria %s(total de requests: %s)}
        \\end{figure}
        

        """%(os.getcwdu(),nombre,usr,self.categoria,total)
        
        
            
        
    
    def plotearPorcentajePorUsuario(self,infractores, infracciones,
                                    requestsPorUsuarios):
        res = ""
        for each in infractores:
            res += self.pocentajePara(each,infracciones[each],requestsPorUsuarios[each])
        return res
    
    def pocentajePara(self,usr,infracciones,total):

        d = {'Resto':total - infracciones, 'Infraccion':infracciones}
        nombre = "porcentaje_%s_%s.png" % (self.categoria,usr.replace('.',''))
        CairoPlot.pie_plot(nombre,d, 800,500,shadow=True,gradient=True)
        return \
        """
        \\begin{figure}[H]
        \\centering
        \\includegraphics[width=12cm]{%s/%s}
        \\caption{Porcentaje de requests infractoras para %s, categoria %s(total de requests: %s)}
        \\end{figure}
        

        """%(os.getcwdu(),nombre,usr,self.categoria,total)
        
        
        
    
    def plotearPorcentaje(self,total, infraccion,desde,hasta):
        d = { 'Resto':total-infraccion,'Infraccion':infraccion}
        nombre = "porcentaje_%s.png" % self.categoria
        CairoPlot.pie_plot(nombre,d, 800, 500,shadow=True,gradient=True)
        res = \
        """
        \\section{Porcentaje de requests infractores %s}
        En esta seccion se muestra que porcentaje de todos los requests hechos,
        corresponden a requests a sitios infractores.
        
        \\begin{figure}[H]
        \\centering
        \\includegraphics[width=12cm]{%s/%s}
        \\caption{Porcentaje de requests infractoras categoria %s (total de requests: %s)}
        \\label{%s}
        \\end{figure}
     
        """%(self.categoria,os.getcwdu(),nombre, self.categoria,total,
            "Porcentaje_%s" % self.categoria)
        res += "\\begin{itemize}\n"
        res += "\\item En infraccion %s\n"%(1.0*infraccion/total)
        res += "\\item Resto %s\n"%(1.0*(total-infraccion)/total)
        res += "\\end{itemize}\n"
        res += "\n\n"
        return res
        
        
        
                
    def plotearDominiosVistados(self,dominios,visitas,totales,desde,hasta):
        if dominios == []:
            return ""
        
        d = dict([(x,visitas[x]) for x in dominios])
        
        nombre = "Dominios_visitados_%s.png" % self.categoria
        CairoPlot.pie_plot(nombre,d, 800, 500, shadow=True, gradient=True)
        res = \
                      """
                       \\section{Dominos visitados en infraccion %s}
                       \\begin{figure}[H]
                       \\centering
                       \\includegraphics[width=12cm]{%s/%s}
                       \\caption{Dominios visitados (sobre un total de %s requests en infraccion)}
                       \\label{%s}
                       \\end{figure}\n
                       """%(self.categoria,os.getcwdu(),nombre,totales,
                            "Dominios_visitados_%s" % self.categoria)
        res += self.armarItemize(d,'visitas')
        return res
        
        
    def _obtenerTodoEnRango(self,d,h):
        s = get_session()
        query = s.query(RequestHTTP)
        query.filter(RequestHTTP.datetime >= str(d) )
        query.filter(RequestHTTP.datetime <= str(h) )
        requestsAll = query.all()
        query = s.query(ResponseHTTP)
        query.filter(ResponseHTTP.datetime >= str(d) )
        query.filter(ResponseHTTP.datetime <= str(h) )
        responsesAll = query.all()
        return (requestsAll, responsesAll)
        
    
    def plotearTrafico(self, requests,dominios,desde,hasta):
        requestAll, responseAll = self._obtenerTodoEnRango(desde,hasta)
        responses = dict([(each.id,each) for each in responseAll])
        
        traficoTotal = 0
        traficoInfraccion = defaultdict(lambda:0)
        for each in requestAll:
            traficoReq = len(each.body)
            traficoResp = len(responses[each.response].body) \
                          if each.response in responses else 0
            traficoTotal += traficoReq
            traficoTotal += traficoResp
            if each.id in requests:
                traficoInfraccion[each.headers['host']] += traficoReq
                traficoInfraccion[each.headers['host']] += traficoResp
        traficoResto = traficoTotal - sum([traficoInfraccion[a] for a in dominios])
        d = {'resto':traficoResto}
        for each in dominios:
            d[each] = traficoInfraccion[each]
        nombre = "trafico_%s.png" % self.categoria
        CairoPlot.pie_plot(nombre,d, 800, 500,shadow=True,gradient=True)
        res = \
                      """
                       \\begin{figure}[H]
                       \\centering
                       \\includegraphics[width=12cm]{%s/%s}
                       \\caption{Porcentaje del trafico en infraccion para la categoria %s (total de trafico: %s bytes)}
                       \\end{figure}
      
                       """%(os.getcwdu(),nombre,self.categoria,traficoTotal)
        
        res += self.armarItemize(d,'bytes')
        return res
        
        
    def armarItemize(self,d, unidad):
        res = ""
        res += "\n\\begin{itemize}\n"
        for c in d:
            res += "\\item %s : %s %s \n"%(c,d[c],unidad)
        res += "\\end{itemize}\n"
        return res
        
    
    
            
            
                    
                    

                    
                
                
        
