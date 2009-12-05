from persistencia import get_session, MensajeHTTP, RequestHTTP, ResponseHTTP
from latex import LatexFactory #para generar el codigo en latex
from enthought.traits.api import *
from enthought.traits.ui.api import *
from reporte import Reporte
import CairoPlot #para dibujar los graficos del reporte
import os


class TraficoEnGral(Reporte):
    plotSitiosTop = Bool
    
    sitiosTop = Range(value=5,low=1,high=10)
    
    view = View('plotSitiosTop',
                'sitiosTop')
    
    #Para escribir la seccion del reporte
    seccion = LatexFactory()
    
    def obtenerDominio(self, host):
    
        #corto el uri para que me quede solo el dominio
        dominio = ""
        #separo todas las cadenas entre los puntos
        div = host.split(".")
        
        #si es de la forma yyy.xxxxxx.com o yyy.xxxxx.net etc
        if len(div[-2]) > 3:
            dominio = host[ host.index(div[-2]) : len(host) ]
        #sino si es de la forma xxxx.com.zz o xxxx.gob.zz etc
        else:
            dominio = host[ host.index(div[-3]) : len(host) ]
            
        return dominio
    
    
    #funcion llamada desde la interfaz.
    def ejecutar(self,desde,hasta):
        
        #obtengo todos los request y responses dentro de las fechas que me pasan
        requests, responses = self._obtenerTodoEnRango(desde,hasta)
        
        #recorro los requests y genero un dicc, para despues sumar los bytes
        #y luego obtener los sitios top para mostrar.
        diccIds = {}
        for each in requests:
            dominio = self.obtenerDominio(each.headers["host"])
            idResponse = each.response
                        
            if not idResponse in diccIds.keys():
                diccIds[idResponse] = dominio
        
        #ahora recorro los requests y voy sumando el trafico entre los dominios
        #genero un nuevo dicc, para guardar lo usado por cada dominio
        diccDominios = {}
        
        for each in responses:
            idResponse = each.id
            dominio = diccIds[idResponse]
            bytes = len(each.body)
    
            #sumo los bytes del la respuesta
            if dominio in diccDominios.keys():
                diccDominios[dominio][0] += bytes
            else:
                diccDominios[dominio] = [bytes, dominio]
    
        del diccIds
        #armo una lista con lo que tengo en el dicc
        listConsumo = diccDominios.values()
        listConsumo.sort()
        listConsumo.reverse()
        
        #ahora escribo esto en un latex
        self.seccion.chapter("Sitios con mas trafico")
        self.seccion.texto("En este parte se mostrar'an los sitios con mas trafico \
                   desde la fecha deinicio seleccionada hasta la fecha final.")
        self.seccion.tabular(listConsumo, self.sitiosTop, "Bytes")
        
        #si se quiso hacer un grafico lo hago
        if self.plotSitiosTop:
            #paso los datos de la lista a un dicc
            diccTemp = {}
            
            largo = min(self.sitiosTop, len(listConsumo))
            for i in range(largo):
                dominio = listConsumo[i][1]
                consumo = listConsumo[i][0]
                diccTemp[dominio] = consumo
                
            #hago el grafico
            archivoSalida = self.directorio + "/traficoEnGral.png"
            CairoPlot.pie_plot(archivoSalida, diccTemp, 800, 500, shadow = True, gradient = True)
            self.seccion.figure(archivoSalida, "Proporci'on de trafico entre los dominios.")
        
        return self.seccion.generarOutput()