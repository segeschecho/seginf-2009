from persistencia import get_session, RequestHTTP, ResponseHTTP
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from reporte import Reporte
import CairoPlot
import plot
from collections import defaultdict
from enthought.pyface.message_dialog import MessageDialog
from enthought.pyface.progress_dialog import ProgressDialog
from enthought.traits.ui.menu import OKButton, CancelButton
from latex import LatexFactory

#import psyco
import tempfile
#psyco.full()

#TODO: un poco de refactor no vendria mal


class ListaNegra(Reporte):
    dicc = None
    render = LatexFactory
    categoria = Str
    lista = File
    plotInfraccionesPorUsuario = Bool(True)
    plotDominiosVistados = Bool(True)
    plotDominiosVistadosPorUsuario = Bool(True)
    plotPorcentajeDeRequests = Bool(True)
    plotPorcentajePorUsuario = Bool(True)
    plotPorcentajeDeTrafico = Bool(True)
    verbose = Bool(False)
    directorio = None

    
    
        
    view = View(Item('categoria',style='readonly'),
                'lista', 'plotInfraccionesPorUsuario',
                'plotDominiosVistados',
                'plotDominiosVistadosPorUsuario',
                'plotPorcentajeDeRequests',
                'plotPorcentajePorUsuario',
                'plotPorcentajeDeTrafico',
                buttons=[OKButton, CancelButton])
    

        
    def cargarLista(self):
       
        try:
            f = open(self.lista,'r')
        except Exception, e:
            MessageDialog(message="Imposible cargar el reporte a partir del archivo").open()
            raise e
        
        lineas = f.readlines()
      
        self.dicc = set((unicode(x[:-1]) for x in lineas))
        f.close()

        
            
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
                return cand
            cand = '.'+cand
        return None
            
    def ejecutar(self,desde,hasta):
        self.render = LatexFactory()
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
            if self.verbose:
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
            dominiosXHeader = {}
            for each in requests:
                if 'host' in each.headers:
                    
                    domain = self.esta(each.headers['host'])
                    if domain != None:
                        dominiosXHeader[each.headers['host']] = domain
                        if self.verbose:
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
                if self.verbose:
                    self.render.texto("\\item No hubo accesos a sitios de esta categoria\n")
                    self.render.texto("\\end{itemize}\n")
                return self.render.generarOutput()
            if self.verbose:               
                self.render.texto("\\end{itemize}\n")
            
            del self.dicc
            
            self.plotearPorcentaje(len(requests), visitasTotales,desde,hasta)
            self.plotearPorcentajePorUsuario(infractores, infracciones, requestsPorUsuarios)
            self.plotearInfraccionesPorUsuario(infractores,infracciones,visitasTotales)
            self.plotearDominiosVisitadosPorUsuario(infractores,dominiosVisitadosPorUsuario,visitasPorUsuario)
            self.plotearDominiosVistados(dominiosVisitados, visitasADominios,visitasTotales,desde,hasta)
            self.plotearTrafico(requestsInfractores,dominiosVisitados,desde,hasta,dominiosXHeader)
            s = self.render.generarOutput()
            del self.render
            return s
            
    
    
    def plotearInfraccionesPorUsuario(self,infractores,infracciones,totales):
        y = [infracciones[i] for i in infractores]
        self.render.section('Infracciones por usuario en la categoria %s'%\
                            self.categoria)
        maximo = max(y)
        self.render.texto('Las siguientes son las infracciones por usuario para\
                          sitios de la categoria %s'%self.categoria)
        aux = dict(zip(infracciones,y))
        self.render.itemize(aux, 'requests')
        if self.plotearInfraccionesPorUsuario:
            nombre = self.directorio+'/Infracciones_Usuario_%s.png'%self.categoria.replace(' ', '')
            CairoPlot.bar_plot (nombre,
            y, 400, 300, 
            border = 20, grid = True, rounded_corners = True,
            h_labels=infractores,
            v_labels = ['0',str(maximo/4.0),str(maximo/2.0)
            ,str(3*maximo/4.0),str(maximo)],three_dimension=True)
            self.render.figure("%s"%(nombre), caption = \
                    'Cantidad de infracciones por usuario para la categoria %s,\
                    sobre un total de %s'%(self.categoria, totales))
        
        
    def plotearDominiosVisitadosPorUsuario(self,infractores,
                                           dominiosVisitadosPorUsuario,
                                           visitasPorUsuario):

        for each in infractores:
            self.visitadosPara(each,dominiosVisitadosPorUsuario[each],
                                 visitasPorUsuario[each])


    def visitadosPara(self,usr,dominios,cantPorDominio):
        # Si son muchos dominios nos quedamos con el top ten
        if len(dominios) > 10:
            dominios = list(dominios)
            dominios.sort(lambda x,y:1 if cantPorDominio[x] < cantPorDominio[y] \
                                  else -1 if cantPorDominio[x] > cantPorDominio[y] \
                                  else 0)
            cantResto = sum((cantPorDominio[x] for x in dominios[10:]))
            dominios = dominios[0:10]
            dominios.append('otros')
            cantPorDominio['otros'] = cantResto
                                  
        d = dict([(dom, cantPorDominio[dom]) for dom in dominios])
        total = sum([cantPorDominio[dom] for dom in dominios])
        
        self.render.section('Dominios visitados para la categoria %s por el usuario %s'\
                            %(self.categoria,usr))
        self.render.texto('Los dominios visitados por el usuario %s son:'%usr)
        self.render.itemize(d, 'requests')
        if self.plotDominiosVistadosPorUsuario:
            nombre = self.directorio + "/dominios_%s_%s.png" % (self.categoria.replace(' ',''),usr.replace('.',''))
            plot.pie_plot(nombre,d, 1000,500,gradient=True,
                shadow=True
               )
            self.render.figure(nombre, caption = \
                           'Dominios visitados por %s, categoria %s(total de requests: %s)'\
                           %(usr,self.categoria,total))
        
    
            
        
    
    def plotearPorcentajePorUsuario(self,infractores, infracciones,
                                    requestsPorUsuarios):
        for each in infractores:
             self.pocentajePara(each,infracciones[each],requestsPorUsuarios[each])
    
    def pocentajePara(self,usr,infracciones,total):

        d = {'Resto':total - infracciones, 'Infraccion':infracciones}
        self.render.section('Porcenteja de requests en infraccion para el usuario %s en la categoria %s'\
                            %(usr,self.categoria))
        d1 = dict(((x,1.0*d[x]/total) for x in d))                    
        self.render.itemize(d1,'requests')                    
        
        if self.plotPorcentajePorUsuario:
            nombre = self.directorio +"/porcentaje_%s_%s.png" % (self.categoria.replace(' ',''),usr.replace('.',''))
            plot.pie_plot(nombre,d, 800,500,shadow=True,gradient=True)

            self.render.figure(nombre, caption = \
                           'Porcentaje de requests infractoras para %s, categoria %s(total de requests: %s)'\
                           %(usr,self.categoria,total))
                
        
    
    def plotearPorcentaje(self,total, infraccion,desde,hasta):
        d = { 'Resto':total-infraccion,'Infraccion':infraccion}
        self.render.section('Porcentaje de requests infractores para la categoria %s'\
                            %self.categoria)
        d1 = dict(((x,1.0*d[x]/total) for x in d))                    
        self.render.itemize(d1,'requests')                    
        if self.plotPorcentajeDeRequests:
            nombre = self.directorio + "/porcentaje_%s.png" % self.categoria.replace(' ','')
            plot.pie_plot(nombre,d, 800, 500,shadow=True,gradient=True)
            self.render.figure(nombre, caption = \
                          'Porcentaje de requests infractoras categoria %s (total de requests: %s)'\
                           %(self.categoria,total))

        
        
        
                
    def plotearDominiosVistados(self,dominios,cantPorDominio,totales,desde,hasta):
        if dominios == []:
            return ""
        
        if len(dominios) > 10:   
            dominios = list(dominios)
            dominios.sort(lambda x,y:1 if cantPorDominio[x] < cantPorDominio[y] \
                                  else -1 if cantPorDominio[x] > cantPorDominio[y] \
                                  else 0)
            cantResto = sum((cantPorDominio[x] for x in dominios[10:]))
            dominios = dominios[0:10]
            dominios.append('otros')
            cantPorDominio['otros'] = cantResto
        
        d = dict([(x,cantPorDominio[x]) for x in dominios])
        self.render.section('Dominos visitados en infraccion para la categoria %s'\
                            %self.categoria)
        self.render.texto('Los dominios visitados en infraccion son:')
        self.render.itemize(d, 'requests')
        if self.plotDominiosVistados:
            nombre = self.directorio +"/Dominios_visitados_%s.png" % self.categoria.replace(' ', '')
            plot.pie_plot(nombre,d, 1000,500,gradient=True,
                shadow=True
               )
            self.render.figure(nombre, caption = \
                           'Dominios visitados sobre %s (sobre un total de %s requests en infraccion)'\
                           %(self.categoria,totales) )



        
        
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
        
    
    def plotearTrafico(self, requests,dominios,desde,hasta,dominiosXHeader):
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
                traficoInfraccion[dominiosXHeader[each.headers['host']]] += traficoReq
                traficoInfraccion[dominiosXHeader[each.headers['host']]] += traficoResp
        traficoResto = traficoTotal - sum([traficoInfraccion[a] for a in dominios])
        d = {'resto':traficoResto}
        if len(dominios) > 10:
            dominios = list(dominios)
            dominios.sort(lambda x, y: 1 if traficoInfraccion[x] < traficoInfraccion[y] \
                                        else -1 if  traficoInfraccion[x] > traficoInfraccion[y] \
                                        else 0)
            sumaOtros = sum((traficoInfraccion[x] for x in dominios[10:]))
            dominios = dominios[:10]
            dominios.append('otros')
            traficoInfraccion['otros'] = sumaOtros
        self.render.section('Porcentaje del trafico en infraccion para la categoria %s'%self.categoria)
        for each in dominios:
            d[each] = traficoInfraccion[each]
        self.render.itemize(d,'bytes')
        if self.plotPorcentajeDeTrafico:
            nombre = self.directorio + "/trafico_%s.png" % self.categoria.replace(' ','')
            plot.pie_plot(nombre,d, 800, 500,shadow=True,gradient=True)
            self.render.figure(nombre, caption =' Porcentaje del trafico en infraccion para la categoria %s (total de trafico: %s bytes)'%(self.categoria,traficoTotal))

