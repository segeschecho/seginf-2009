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
    
    #cantidad de sitios a mostrar en los graficos
    sitiosTop = Range(value=5,low=1,high=10)
    #cantidad de usuarios a mostrar en los graficos
    usuariosTop = Range(value=5,low=1,high=10)
    view = View('plotPorUsuario',
                'plotTrafico',
                'plotPorDominios',
                'plotDominiosPorUsuario',
                'usuariosTop',
                'sitiosTop',
                buttons=[OKButton, CancelButton]
                )
    #Para escribir la seccion del reporte
    seccion = LatexFactory()


    #FIXME: separa esto en metodos checho
    def subReporteTrafico(self,requests,responses,responsesAjax,requestsAjax):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        
        #Trafico ajax
        traficoAjax = 0

        #diccionario de usuarios, que contendran el trafico usado
        diccUsuarios = {}
        #diccionario de ids, que tienen listas con [dominio, uso en bytes]
        diccIds = {}
        #diccionario de usuarios, que tiene un dicc {dominio, [cant requests, dominio]}
        #cuento solo los requests
        diccUsuariosDominios = {}
        
        #genero los datos que despues voy a mostrar en el informe
        for each in requestsAjax:
            #sumo el trafico ajax
            traficoAjax += len(each.body)
            
            #recorro todos los responses y genero un diccionario con los usuarios            
            usuario = each.ipOrigen
            #guardo el dominio al cual se hizo el request
            host = each.headers["host"]
            #guardo el id de las respuestas
            id = each.response
            
            #corto el uri para que me quede solo el dominio
            #posicion despues del http:// o https:// es 8
            #domAux = dominio[0 : dominio.find("/", 8, len(dominio))]
            dominio = ""
            div = host.split(".")
            #si es de la forma yyy.xxxxxx.com o yyy.xxxxx.net etc
            if len(div[-2]) > 3:
                dominio = host[ host.index(div[-2]) : len(host) ]
            #sino si es de la forma xxxx.com.zz o xxxx.gob.zz etc
            else:
                dominio = host[ host.index(div[-3]) : len(host) ]
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)
                
            #si el usuario ya estaba en el dicc sumo el dominio o lo agrego
            if not usuario in diccUsuariosDominios.keys():
                diccUsuariosDominios[usuario] = {dominio: [1, dominio]}
            
            if dominio in diccUsuariosDominios[usuario].keys():
                diccUsuariosDominios[usuario][dominio][0] += 1
            else:
                diccUsuariosDominios[usuario][dominio] = [1, dominio]
                        
            #si el dominio ya estaba en el dicc sumo lo que uso
            if id in diccIds.keys():
                diccIds[id][1] += len(each.body)
            else:
                diccIds[id] = [dominio, len(each.body)]
        
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
            if id in diccIds.keys():
                diccIds[id][1] += len(each.body)


        #si no hubo trafico del tipo ajax, no hay nada para mostrar
        if traficoAjax == 0:
            self.seccion.texto("Hasta el momento no se registr'o ning'un trafico\
                               del tipo Ajax, por este motivo en esta secci'on \
                               no se mostrar'a informaci'on.")
            return True
        
        #creo un diccionario dominio, (dominio, trafico) para despues graficar
        diccDominios = {}
        
        for each in diccIds:            
            id = diccIds[each]
            # si el dominio ya esta, sumo los bytes
            if id[0] in diccDominios.keys():
                diccDominios[id[0]] += id[1]
            else:
                diccDominios[id[0]] = id[1]
        
        del diccIds

        #creo una lista de tuplas(trafico, dominio) para ordenar y hacer el top
        listTrafico = []
        
        for dom in diccDominios:
            traficoTemp = diccDominios[dom]
            listTrafico.append((traficoTemp, dom))
        
        del diccDominios
        
        #ordeno esa lista
        listTrafico.sort()
        listTrafico.reverse()
        
        #genero los dominios top (dominio, trafico)
        dominiosTop = {}
        
        cantDominiosTop = min(len(listTrafico), self.sitiosTop)        
        for i in range(cantDominiosTop):
            tupla = listTrafico[i]
            dominiosTop[tupla[1]] = tupla[0]
        
        #creo una lista de tuplas(trafico, usuario) para ordenar y hacer el top
        listUsuariosTrafico = []
        
        for usr in diccUsuarios:
            traficoTemp = diccUsuarios[usr]
            listUsuariosTrafico.append((traficoTemp, usr))
        
        del diccUsuarios
        
        #ordeno esa lista
        listUsuariosTrafico.sort()
        listUsuariosTrafico.reverse()
        
        #genero los usuarios top (usuario, trafico)
        usuariosTop = {}
        
        cantUsuariosTop = min(len(listUsuariosTrafico), self.usuariosTop)        
        for i in range(cantUsuariosTop):
            tupla = listUsuariosTrafico[i]
            usuariosTop[tupla[1]] = tupla[0]
        
        
        #genero la info de los dominios por usuarios
        diccUsuariosDominiosTop = {}
        
        for each in diccUsuariosDominios:
            #obtengo la lista de [uso, dominio]
            listaDeUsoDom = diccUsuariosDominios[each].values()
            
            listaDeUsoDom.sort()
            listaDeUsoDom.reverse()
            
            diccUsuariosDominiosTop[each] = listaDeUsoDom
        
        
        del diccUsuariosDominios
            
        #######################################################################
        ##################    comienzo del informe  ###########################
        #######################################################################
        #Titulo de la seccion
        self.seccion.section("Trafico de tipo Ajax")

        #Estadisticas de trafico
        self.seccion.texto("Estadisticas:\n\n")
        self.seccion.texto("En los textos siguientes se mostrar'a informaci'on del \
                      uso de la red con relaci'on al trafico de tipo Ajax, \
                      estos en algunos casos pueden ocupar una porci'on significativa \
                      del trafico total.\
                      A continuaci'on se puede ver esta informaci'on, donde se \
                      muestra el trafico total (en Bytes) y el trafico de tipo ajax, \
                      (tambi'en en Bytes). Estos valores pueden ser muy utiles \
                      a la hora de tener una idea general de cuanto es el tr'afico \
                      din'amico dentro de la red.")
        self.seccion.itemize({'Trafico Total':str(trafico), 'Trafico Ajax':str(traficoAjax)}, "Bytes")

        #Si se quiso hacer un grafico del trafico ajax
        if self.plotTrafico:
            #hago el grafico para el trafico
            d = {'Trafico Ajax': traficoAjax, 'Trafico no Ajax': trafico - traficoAjax}
            archivoSalida = self.directorio + "/" + "traficoAjax.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)

            self.seccion.texto("En el siguiente gr'afico se puede apreciar mejor este volumen de trafico.")
            self.seccion.figure(archivoSalida, "Proporci'on de trafico Ajax \
                           con respecto al total.")


        #muestro los usuarios y sus gastos.
        self.seccion.section("Trafico Ajax por usuario")
        self.seccion.texto("En esta secci'on se mostrar'a el trafico ajax \
                      que utiliza cada usuario. Para mayor comodidad, solo se \
                      visualizar'an los " + str(self.usuariosTop) + " primeros \
                      segun se configur'o en el archivo ajax.py.")
        
        #FIXME: por que no usas el render? sabe hacer itemizes
        texto = "\\begin{enumerate}\n"
        for i in range(cantUsuariosTop):
            texto += "\\item %s: %s %s\n"%(listUsuariosTrafico[i][1], listUsuariosTrafico[i][0], "Bytes")
        texto += "\\end{enumerate}\n"
        self.seccion.texto(texto)
        
        #Si se quiso hacer un grafico por usuario
        if self.plotPorUsuario:
            #hago el grafico para los usuarios
            archivoSalida = self.directorio + "/traficoAjaxUsuarios.png"
            CairoPlot.pie_plot(archivoSalida, usuariosTop, 800, 500, shadow = True, gradient = True)
            
            self.seccion.figure(archivoSalida, "Proporci'on de trafico Ajax \
                           utilizado por cada usuario.")
                        
        
        #muestro los dominios
        self.seccion.section("Trafico Ajax por dominio")
        self.seccion.texto("En esta secci'on se mostrar'a el trafico ajax \
                      por dominio. Para mayor comodidad, solo se \
                      visualizar'an los " + str(self.sitiosTop) + " primeros \
                      segun se configur'o en el archivo ajax.py.")
        
        texto = "\\begin{enumerate}\n"
        for i in range(cantDominiosTop):
            texto += "\\item %s: %s %s\n"%(listTrafico[i][1], listTrafico[i][0], "Bytes")
        texto += "\\end{enumerate}\n"
        self.seccion.texto(texto)
        
        #Si se quiso hacer un grafico por dominio
        if self.plotPorDominios:           
            #hago el grafico para los dominios
            archivoSalida = self.directorio + "/traficoAjaxDominio.png"
            CairoPlot.pie_plot(archivoSalida, dominiosTop, 800, 500, shadow = True, gradient = True)
            self.seccion.figure(archivoSalida, "Proporci'on de trafico Ajax \
                           a cada dominio.")
            
        #si se quiso hacer un grafico de los usuarios por dominio
        if self.plotDominiosPorUsuario:
            self.seccion.section("Trafico Ajax dominios por usuario")
            self.seccion.texto("En esta secci'on se mostrar'a el trafico ajax \
                               separados en dominio por usuario. Se mostrar'an \
                               los " + str(self.sitiosTop) + " primeros sitios \
                               ordenados por cantidad de accesos a los mismos. \\\\")
                               
            
            for each in diccUsuariosDominiosTop:
                listaTemp = diccUsuariosDominiosTop[each]
                
                cantUsuariosDominiosTop = min(len(listaTemp), self.sitiosTop)
                
                listaTempTop = listaTemp[:cantUsuariosDominiosTop]
                
                self.seccion.texto("\\textbf{%s :}"%(each))
                self.seccion.itemize(listaTempTop, "Accesos")
        
        return True
       
        
    def ejecutar(self,desde,hasta):
        self.seccion = LatexFactory()
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
        self.seccion.chapter("Trafico utilizando Ajax")
        self.subReporteTrafico(requests,responses,responsesAjax,requestsAjax)

        return self.seccion.generarOutput()
        

