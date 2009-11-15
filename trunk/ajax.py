from persistencia import get_session, MensajeHTTP, RequestHTTP, ResponseHTTP
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from reporte import Reporte
import CairoPlot #para dibujar los graficos del reporte
import os
from enthought.pyface.message_dialog import MessageDialog
from enthought.pyface.progress_dialog import ProgressDialog
from enthought.traits.ui.menu import OKButton, CancelButton
from latex import LatexFactory #para generar el codigo en latex


class Ajax(Reporte):

    plotPorUsuario = Bool
    plotTrafico = Bool
    plotPorDominios = Bool
    plotDominiosPorUsuario = Bool

    #tipos de respuesta ajax en el content type
    tiposAjax = [unicode('application/json'), \
                 unicode('application/xml'), \
                 unicode('text/javascript'), \
                 unicode('application/javascript'), \
                 unicode('application/x-javascript')]
    
    
    def _obtenerTodoEnRango(self,d,h):
        #obtengo la sesion a la base de datos
        s = get_session()
        #filtro los requests por fecha
        query = s.query(RequestHTTP)
        query.filter(RequestHTTP.datetime >= str(d) )
        query.filter(RequestHTTP.datetime <= str(h) )
        requestsAll = query.all()
        #filtro los responses por fecha
        query = s.query(ResponseHTTP)
        query.filter(ResponseHTTP.datetime >= str(d) )
        query.filter(ResponseHTTP.datetime <= str(h) )
        responsesAll = query.all()

        return (requestsAll, responsesAll)


    def subreporteTrafico(self,requests,responses,responsesAjax,requestsAjax):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        #Calculo el trafico ajax
        traficoAjax = sum((len(x.body) for x in requestsAjax)) + \
                      sum((len(x.body) for x in responsesAjax))

        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()

        #Titulo de la seccion
        seccion.section("Trafico de tipo Ajax")

        #Estadisticas de trafico
        seccion.texto("Estadisticas:")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico Ajax':str(traficoAjax)})

        #Si se quiso hacer un grafico en el reporte lo hago
        if self.plotTrafico:
            d = {'Trafico Ajax': traficoAjax, 'Trafico no Ajax': trafico - traficoAjax}
            archivoSalida = "traficoAjax.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)

            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida)

        return seccion.generarOutput()
       
        
    def ejecutar(self,desde,hasta):
        #obtengo todos los request y responses dentro de las fechas que me pasan
        requests, responses = self._obtenerTodoEnRango(desde,hasta)
        
        #genero un diccionario donde las claves son los id de las respuestas
        requestsDict = dict(((each.response, each) for each in requests))

        # Obtenemos los responses ajax
        responsesAjax = []
        for each in responses:
            if 'content-type' in each.headers:
                #me fijo si el tipo es del que quiero
                if each.headers['content-type'].split(';')[0] in self.tiposAjax:
                    responsesAjax.append(each)
                #print each.headers['content-type'].__repr__()
         
        # Obtenemos los request asociados a esos responses
        requestsAjax = []
        for each in responsesAjax:
            if each.id in requestsDict:
                requestsAjax.append(requestsDict[each.id])
        
        #borro el diccionario por que ya no me sirve
        del requestsDict

        #comienzo a generar el reporte        
        res = "\\chapter{Trafico utilizando Ajax}\n"
        res += self.subreporteTrafico(requests,responses,responsesAjax,requestsAjax)


        print res


        return res
        

