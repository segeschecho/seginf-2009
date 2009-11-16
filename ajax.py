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


    def subReporteTrafico(self,requests,responses,responsesAjax,requestsAjax):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        
        #Trafico ajax
        traficoAjax = 0

        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()

        #diccionario de usuarios, que contendran el trafico usado
        diccUsuarios = {}
        diccDominios = {}
        
        #genero los datos que despues voy a mostrar en el informe
        for each in requestsAjax:
            #sumo el trafico ajax
            traficoAjax += len(each.body)
            
            #recorro todos los responses y genero un diccionario con los usuarios            
            usuario = each.ipOrigen
            dominio = each.host
            id = each.id
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)
                        
            #si el dominio ya estaba en el dicc sumo lo que uso
            if id in diccDominios.keys():
                diccDominios[id][1] += len(each.body)
            else:
                diccDominios[id] = (dominio, len(each.body))
            
            
        
        for each in responsesAjax:
            #sigo sumando el trafico ajax
            traficoAjax += len(each.body)
            
            #recorro todos los request y genero un diccionario con los usuarios            
            usuario = each.ipDestino
            id = each.id
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)
            
            #sumo los body de las respuestas a las peticiones ajax
            if id in diccDominios.keys():
                diccDominios[id][1] += len(each.body)



        #Titulo de la seccion
        seccion.section("Trafico de tipo Ajax")

        #Estadisticas de trafico
        seccion.texto("Estadisticas:")
        seccion.texto("En la siguiente informaci'on se mostrar'a el trafico total en bytes \
                      y el trafico de tipo ajax, tambi'en en bytes. Estos valores pueden ser \
                      muy utiles a la hora de tener una idea general de cuanto es el tr'afico \
                      din'amico dentro de la red.")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico Ajax':str(traficoAjax)}, "Bytes")

        #Si se quiso hacer un grafico del trafico ajax
        if self.plotTrafico:
            d = {'Trafico Ajax': traficoAjax, 'Trafico no Ajax': trafico - traficoAjax}
            archivoSalida = "traficoAjax.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)

            seccion.texto("En el siguiente gr'afico se puede apreciar mejor este volumen de trafico.")
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico Ajax \
                           con respecto al total.")

        #Si se quiso hacer un grafico por usuario
        if self.plotPorUsuario:
            
            #muestro los usuarios y sus gastos.
            seccion.texto("En esta parte se mostrara el trafico ajax por usuarios.")
            seccion.itemize(diccUsuarios, "Bytes")
                        
        #Si se quiso hacer un grafico por dominio
        
        if self.plotPorDominios:
            
            #muestro los dominios
            texto = ""
            texto = "\\begin{itemize}\n"
            for each in diccDominios:              
                texto += "\\item %s: %s %s\n"%(str(diccDominios[each][0]), \
                                               str(diccDominios[each][1]), \
                                                "Bytes")
            texto += "\\end{itemize}\n"
            
            seccion.texto(texto)
            
        
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
        res += self.subReporteTrafico(requests,responses,responsesAjax,requestsAjax)


        print res


        return res
        

