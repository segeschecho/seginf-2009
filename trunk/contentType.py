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


class ContentType(Reporte):

    plotPorTrafico = Bool
    plotPorAplicacion = Bool
    plotPorAudio = Bool
    plotPorImagenes = Bool
    plotPorVideo = Bool
    plotPorTexto = Bool
    plotPorMultipart = Bool
    plotPorUsuario = Bool
    plotPorUsuario = Bool
    
    usuariosTop = 10
    sitiosTop = 10
   
    #ContentTypeAplicacion = [unicode('application/atom+xml'), \
    #                         unicode('application/iges'), \
    #                         unicode('application/javascript'), \
    #                         unicode('application/dxf'), \
    #                         unicode('application/mp4'), \
    #                         unicode('application/iges'), \
    #                         unicode('application/octet-stream'), \
    #                         unicode('application/msword'), \
    #                         unicode('application/pdf'), \
    #                         unicode('application/postscript'), \
    #                         unicode('application/rtf'), \
    #                         unicode('application/sgml'), \
    #                         unicode('application/vnd.ms-excel'), \
    #                         unicode('application/vnd.ms-powerpoint'), \
    #                         unicode('application/xml'), \
    #                         unicode('application/x-tar'), \
    #                         unicode('application/zip')]
    #
    #ContentTypeAudio =  [unicode('audio/basic'), \
    #                     unicode('audio/mpeg'), \
    #                     unicode('audio/mp4'), \
    #                     unicode('audio/x-aiff'), \
    #                     unicode('audio/x-wav')]
    #
    #ContentTypeImagen = [unicode('image/gif'), \
    #                    unicode('image/jpeg'), \
    #                    unicode('image/png'), \
    #                    unicode('image/tiff'), \
    #                    unicode('image/x-portable-bitmap'), \
    #                    unicode('image/x-portable-graymap'), \
    #                    unicode('image/x-portable-pixmap')]
    #
    #ContentTypeComp =   [unicode('multipart/x-zip'), \
    #                    unicode('multipart/x-gzip')]
    #
    #ContentTypeTexto =  [unicode('text/css'), \
    #                    unicode('text/csv'), \
    #                    unicode('text/html'), \
    #                    unicode('text/plain'), \
    #                    unicode('text/richtext'), \
    #                    unicode('text/rtf'), \
    #                    unicode('text/tab-separated-value'), \
    #                    unicode('text/xml')]
    #
    #ContentTypeVideo = [unicode('video/h264'), \
    #                    unicode('video/dv'), \
    #                    unicode('video/mpeg'), \
    #                    unicode('video/quicktime'), \
    #                    unicode('video/msvideo')]    
    
    ContentTypeAplicacion = [unicode('application')]    
    ContentTypeAudio =  [unicode('audio')]    
    ContentTypeImagen = [unicode('image')]    
    ContentTypeComp =   [unicode('multipart')]    
    ContentTypeTexto =  [unicode('text')]    
    ContentTypeVideo = [unicode('video')]
        
    ########################################################################################################################

    def subreporteTrafico(self,responsesDeAplicacion,requestsDeAplicacion,responsesDeAudio,requestsDeAudio,responsesDeImagen,requestsDeImagen,responsesDeVideo,requestsDeVideo,responsesDeTexto,requestsDeTexto,responsesDeMultipart,requestsDeMultipart):
        
        #Calculo el trafico de aplicacion
        traficoAplicacion = sum((len(x.body) for x in requestsDeAplicacion)) + \
                            sum((len(x.body) for x in responsesDeAplicacion))
        #Calculo el trafico de audio
        traficoAudio = sum((len(x.body) for x in requestsDeAudio)) + \
                            sum((len(x.body) for x in responsesDeAudio))
        #Calculo el trafico de imagen
        traficoImagen = sum((len(x.body) for x in requestsDeImagen)) + \
                            sum((len(x.body) for x in responsesDeImagen))
        #Calculo el trafico de video
        traficoVideo = sum((len(x.body) for x in requestsDeVideo)) + \
                       sum((len(x.body) for x in responsesDeVideo))
        #Calculo el trafico de texto
        traficoTexto = sum((len(x.body) for x in requestsDeTexto)) + \
                       sum((len(x.body) for x in responsesDeTexto))
        #Calculo el trafico multipart
        traficoMultipart = sum((len(x.body) for x in requestsDeMultipart)) + \
                            sum((len(x.body) for x in responsesDeMultipart))
    
        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()
    
        #Titulo de la seccion
        seccion.section("Tipo de Trafico")
    
        #Estadisticas de trafico de aplicacion
        seccion.texto("Estadisticas:")
        seccion.itemize({'Trafico de Aplicacion':str(traficoAplicacion), 'Trafico de Audio':str(traficoAudio), 'Trafico de Imagen':str(traficoImagen), 'Trafico de Video':str(traficoVideo), 'Trafico de Texto':str(traficoTexto), 'Trafico Multipart':str(traficoMultipart)})
    
        #Si se quiso hacer un grafico en el reporte lo hago
        if self.plotPorTrafico:
            d = {'Trafico de Aplicacion': traficoAplicacion, 'Trafico de Audio': traficoAudio, 'Trafico de Imagen': traficoImagen, 'Trafico de video': traficoVideo, 'Trafico de Texto': traficoTexto, 'Trafico Multipart': traficoMultipart}
            archivoSalida = "trafico.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)
    
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida)
    
        return seccion.generarOutput()

    ########################################################################################################################

    def subreporteTraficoDeAplicacion(self,requests,responses,responsesDeAplicacion,requestsDeAplicacion):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        
        #Trafico de aplicacion
        traficoAplicacion = 0

        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()

        #diccionario de usuarios, que contendran el trafico usado
        diccUsuarios = {}
        
        #genero los datos que despues voy a mostrar en el informe
        for each in requestsDeAplicacion:
            #sumo el trafico aplicacion
            traficoAplicacion += len(each.body)
            
            #recorro todos los responses y genero un diccionario con los usuarios            
            usuario = each.ipOrigen
            #guardo el dominio al cual se hizo el request
            host = each.headers["host"]
            #guardo el id de las respuestas
            id = each.response
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)                        
            
        
        for each in responsesDeAplicacion:
            #sigo sumando el trafico de aplicacion
            traficoAplicacion += len(each.body)
            
            #recorro todos los request y genero un diccionario con los usuarios            
            usuario = each.ipDestino
            id = each.id
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)        
        
        #creo una lista de tuplas(trafico, usuario) para ordenar y hacer el top
        listUsuariosTrafico = []
        
        traficoDeUsu = 0
        
        for usr in diccUsuarios:
            traficoDeUsu = diccUsuarios[usr]
            listUsuariosTrafico.append((traficoDeUsu, usr))
        
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
        
        #######################################################################
        ##################    comienzo del informe  ###########################
        #######################################################################
        #Titulo de la seccion
        seccion.section("Trafico de tipo Aplicacion")

        #Estadisticas de aplicacion
        seccion.texto("Estadisticas:")
        seccion.texto("En los textos siguientes se mostrar'a informaci'on del \
                      uso de la red con relaci'on al trafico de tipo Aplicacion, \
                      estos en algunos casos pueden ocupar una porci'on significativa \
                      del trafico total.\
                      A continuaci'on se puede ver esta informaci'on, donde se \
                      muestra el trafico total (en Bytes) y el trafico de tipo aplicacion, \
                      (tambi'en en Bytes). Estos valores pueden ser muy utiles \
                      a la hora de tener una idea general de cuanto es el tr'afico \
                      din'amico dentro de la red.")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico de Aplicacion':str(traficoAplicacion)}, "Bytes")

        #Si se quiso hacer un grafico del trafico de aplicacion
        if self.plotPorAplicacion and traficoAplicacion > 0:
            #hago el grafico para el trafico
            d = {'Trafico Aplicacion': traficoAplicacion, 'Trafico no Aplicacion': trafico - traficoAplicacion}
            archivoSalida = "traficoAplicacion.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)            
            seccion.texto("En el siguiente gr'afico se puede apreciar mejor este volumen de trafico.")
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Aplicacion \
                            con respecto al total.")                
        
        if traficoAplicacion > 0:
            #muestro los usuarios y sus gastos.
            seccion.section("Trafico de Aplicaci'on por usuario")
            seccion.texto("En esta secci'on se mostrar'a el trafico de aplicaci'on \
                          que utiliza cada usuario. Para mayor comodidad, solo se \
                          visualizar'an los " + str(self.usuariosTop) + " primeros \
                          segun se configur'o en el archivo contentType.py.")
            
            texto = "\\begin{enumerate}\n"
            for i in range(cantUsuariosTop):
                texto += "\\item %s: %s %s\n"%(listUsuariosTrafico[i][1], listUsuariosTrafico[i][0], "Bytes")
            texto += "\\end{enumerate}\n"
            seccion.texto(texto)
            
            print texto
            
        else:
            seccion.section("Trafico de Aplicaci'on por usuario")
            seccion.texto("No hay tr'afico de aplicaci'on")
        
        
        #Si se quiso hacer un grafico por usuario
        if self.plotPorUsuario and traficoAplicacion > 0:
            #hago el grafico para los usuarios
            archivoSalida = "traficoAplicacionUsuarios.png"
            CairoPlot.pie_plot(archivoSalida, usuariosTop, 800, 500, shadow = True, gradient = True)
            
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Aplicaci'on \
                           utilizado por cada usuario.")
        
        
        return seccion.generarOutput()
        
    ########################################################################################################################
        
    def subreporteTraficoDeAudio(self,requests,responses,responsesDeAudio,requestsDeAudio):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        
        #Trafico de audio
        traficoAudio = 0

        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()

        #diccionario de usuarios, que contendran el trafico usado
        diccUsuarios = {}
        
        #genero los datos que despues voy a mostrar en el informe
        for each in requestsDeAudio:
            #sumo el trafico audio
            traficoAudio += len(each.body)
            
            #recorro todos los responses y genero un diccionario con los usuarios            
            usuario = each.ipOrigen
            #guardo el dominio al cual se hizo el request
            host = each.headers["host"]
            #guardo el id de las respuestas
            id = each.response
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)                        
            
        
        for each in responsesDeAudio:
            #sigo sumando el trafico de audio
            traficoAudio += len(each.body)
            
            #recorro todos los request y genero un diccionario con los usuarios            
            usuario = each.ipDestino
            id = each.id
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)        
        
        #creo una lista de tuplas(trafico, usuario) para ordenar y hacer el top
        listUsuariosTrafico = []
        
        traficoDeUsu = 0
        
        for usr in diccUsuarios:
            traficoDeUsu = diccUsuarios[usr]
            listUsuariosTrafico.append((traficoDeUsu, usr))
        
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
        
        #######################################################################
        ##################    comienzo del informe  ###########################
        #######################################################################
        #Titulo de la seccion
        seccion.section("Trafico de tipo Audio")

        #Estadisticas de audio
        seccion.texto("Estadisticas:")
        seccion.texto("En los textos siguientes se mostrar'a informaci'on del \
                      uso de la red con relaci'on al trafico de tipo Audio, \
                      estos en algunos casos pueden ocupar una porci'on significativa \
                      del trafico total.\
                      A continuaci'on se puede ver esta informaci'on, donde se \
                      muestra el trafico total (en Bytes) y el trafico de tipo audio, \
                      (tambi'en en Bytes). Estos valores pueden ser muy utiles \
                      a la hora de tener una idea general de cuanto es el tr'afico \
                      din'amico dentro de la red.")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico de Audio':str(traficoAudio)}, "Bytes")

        #Si se quiso hacer un grafico del trafico de audio
        if self.plotPorAudio:
            #hago el grafico para el trafico
            d = {'Trafico Audio': traficoAudio, 'Trafico no audio': trafico - traficoAudio}
            archivoSalida = "traficoAudio.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)

            if cantUsuariosTop > 0:
                seccion.texto("En el siguiente gr'afico se puede apreciar mejor este volumen de trafico.")
                seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Audio \
                               con respecto al total.")        
        
        if cantUsuariosTop > 0:
            #muestro los usuarios y sus gastos.
            seccion.section("Trafico de Audio por usuario")
            seccion.texto("En esta secci'on se mostrar'a el trafico de audio \
                          que utiliza cada usuario. Para mayor comodidad, solo se \
                          visualizar'an los " + str(self.usuariosTop) + " primeros \
                          segun se configur'o en el archivo contentType.py.")
            
            texto = "\\begin{enumerate}\n"
            for i in range(cantUsuariosTop):
                texto += "\\item %s: %s %s\n"%(listUsuariosTrafico[i][1], listUsuariosTrafico[i][0], "Bytes")
            texto += "\\end{enumerate}\n"
            seccion.texto(texto)
            
            print texto
            
        else:
            seccion.section("Trafico de Audio por usuario")
            seccion.texto("No hay tr'afico de audio")
        
        
        #Si se quiso hacer un grafico por usuario
        if self.plotPorUsuario and cantUsuariosTop > 0:
            #hago el grafico para los usuarios
            archivoSalida = "traficoAudioUsuarios.png"
            CairoPlot.pie_plot(archivoSalida, usuariosTop, 800, 500, shadow = True, gradient = True)
            
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Audio \
                           utilizado por cada usuario.")
        
        
        return seccion.generarOutput()
    
    ########################################################################################################################
    
    def subreporteTraficoDeImagen(self,requests,responses,responsesDeImagen,requestsDeImagen):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        
        #Trafico de imagen
        traficoImagen = 0

        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()

        #diccionario de usuarios, que contendran el trafico usado
        diccUsuarios = {}
        
        #genero los datos que despues voy a mostrar en el informe
        for each in requestsDeImagen:
            #sumo el trafico imagen
            traficoImagen += len(each.body)
            
            #recorro todos los responses y genero un diccionario con los usuarios            
            usuario = each.ipOrigen
            #guardo el dominio al cual se hizo el request
            host = each.headers["host"]
            #guardo el id de las respuestas
            id = each.response
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)                        
            
        
        for each in responsesDeImagen:
            #sigo sumando el trafico de imagen
            traficoImagen += len(each.body)
            
            #recorro todos los request y genero un diccionario con los usuarios            
            usuario = each.ipDestino
            id = each.id
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)        
        
        #creo una lista de tuplas(trafico, usuario) para ordenar y hacer el top
        listUsuariosTrafico = []
        
        traficoDeUsu = 0
        
        for usr in diccUsuarios:
            traficoDeUsu = diccUsuarios[usr]
            listUsuariosTrafico.append((traficoDeUsu, usr))
        
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
        
        #######################################################################
        ##################    comienzo del informe  ###########################
        #######################################################################
        #Titulo de la seccion
        seccion.section("Trafico de tipo Imagen")

        #Estadisticas de imagen
        seccion.texto("Estadisticas:")
        seccion.texto("En los textos siguientes se mostrar'a informaci'on del \
                      uso de la red con relaci'on al trafico de tipo Imagen, \
                      estos en algunos casos pueden ocupar una porci'on significativa \
                      del trafico total.\
                      A continuaci'on se puede ver esta informaci'on, donde se \
                      muestra el trafico total (en Bytes) y el trafico de tipo imagen, \
                      (tambi'en en Bytes). Estos valores pueden ser muy utiles \
                      a la hora de tener una idea general de cuanto es el tr'afico \
                      din'amico dentro de la red.")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico de Imagen':str(traficoImagen)}, "Bytes")

        #Si se quiso hacer un grafico del trafico de imagen
        if self.plotPorImagenes:
            #hago el grafico para el trafico
            d = {'Trafico Imagen': traficoImagen, 'Trafico no Imagen': trafico - traficoImagen}
            archivoSalida = "traficoImagen.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)

            if cantUsuariosTop > 0:
                seccion.texto("En el siguiente gr'afico se puede apreciar mejor este volumen de trafico.")
                seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Imagen \
                               con respecto al total.")        
        
        if cantUsuariosTop > 0:
            #muestro los usuarios y sus gastos.
            seccion.section("Trafico de Imagen por usuario")
            seccion.texto("En esta secci'on se mostrar'a el trafico de imagen \
                          que utiliza cada usuario. Para mayor comodidad, solo se \
                          visualizar'an los " + str(self.usuariosTop) + " primeros \
                          segun se configur'o en el archivo contentType.py.")
            
            texto = "\\begin{enumerate}\n"
            for i in range(cantUsuariosTop):
                texto += "\\item %s: %s %s\n"%(listUsuariosTrafico[i][1], listUsuariosTrafico[i][0], "Bytes")
            texto += "\\end{enumerate}\n"
            seccion.texto(texto)
            
            print texto
            
        else:
            seccion.section("Trafico de Imagen por usuario")
            seccion.texto("No hay tr'afico de imagen")
        
        
        #Si se quiso hacer un grafico por usuario
        if self.plotPorUsuario and cantUsuariosTop > 0:
            #hago el grafico para los usuarios
            archivoSalida = "traficoImagenUsuarios.png"
            CairoPlot.pie_plot(archivoSalida, usuariosTop, 800, 500, shadow = True, gradient = True)
            
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Imagen \
                           utilizado por cada usuario.")
        
        
        return seccion.generarOutput()
    
    ########################################################################################################################
    
    def subreporteTraficoDeVideo(self,requests,responses,responsesDeVideo,requestsDeVideo):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        
        #Trafico de video
        traficoVideo = 0

        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()

        #diccionario de usuarios, que contendran el trafico usado
        diccUsuarios = {}
        
        #genero los datos que despues voy a mostrar en el informe
        for each in requestsDeVideo:
            #sumo el trafico video
            traficoVideo += len(each.body)
            
            #recorro todos los responses y genero un diccionario con los usuarios            
            usuario = each.ipOrigen
            #guardo el dominio al cual se hizo el request
            host = each.headers["host"]
            #guardo el id de las respuestas
            id = each.response
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)                        
            
        
        for each in responsesDeVideo:
            #sigo sumando el trafico de video
            traficoVideo += len(each.body)
            
            #recorro todos los request y genero un diccionario con los usuarios            
            usuario = each.ipDestino
            id = each.id
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)        
        
        #creo una lista de tuplas(trafico, usuario) para ordenar y hacer el top
        listUsuariosTrafico = []
        
        traficoDeUsu = 0
        
        for usr in diccUsuarios:
            traficoDeUsu = diccUsuarios[usr]
            listUsuariosTrafico.append((traficoDeUsu, usr))
        
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
        
        #######################################################################
        ##################    comienzo del informe  ###########################
        #######################################################################
        #Titulo de la seccion
        seccion.section("Trafico de tipo Video")

        #Estadisticas de video
        seccion.texto("Estadisticas:")
        seccion.texto("En los textos siguientes se mostrar'a informaci'on del \
                      uso de la red con relaci'on al trafico de tipo Video, \
                      estos en algunos casos pueden ocupar una porci'on significativa \
                      del trafico total.\
                      A continuaci'on se puede ver esta informaci'on, donde se \
                      muestra el trafico total (en Bytes) y el trafico de tipo video, \
                      (tambi'en en Bytes). Estos valores pueden ser muy utiles \
                      a la hora de tener una idea general de cuanto es el tr'afico \
                      din'amico dentro de la red.")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico de Video':str(traficoVideo)}, "Bytes")

        #Si se quiso hacer un grafico del trafico de video
        if self.plotPorVideo:
            #hago el grafico para el trafico
            d = {'Trafico Video': traficoVideo, 'Trafico no Video': trafico - traficoVideo}
            archivoSalida = "traficoVideo.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)

            if cantUsuariosTop > 0:
                seccion.texto("En el siguiente gr'afico se puede apreciar mejor este volumen de trafico.")
                seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Video \
                               con respecto al total.")        
        
        if cantUsuariosTop > 0:
            #muestro los usuarios y sus gastos.
            seccion.section("Trafico de Video por usuario")
            seccion.texto("En esta secci'on se mostrar'a el trafico de video \
                          que utiliza cada usuario. Para mayor comodidad, solo se \
                          visualizar'an los " + str(self.usuariosTop) + " primeros \
                          segun se configur'o en el archivo contentType.py.")
            
            texto = "\\begin{enumerate}\n"
            for i in range(cantUsuariosTop):
                texto += "\\item %s: %s %s\n"%(listUsuariosTrafico[i][1], listUsuariosTrafico[i][0], "Bytes")
            texto += "\\end{enumerate}\n"
            seccion.texto(texto)
            
            print texto
            
        else:
            seccion.section("Trafico de Video por usuario")
            seccion.texto("No hay tr'afico de Video")
        
        
        #Si se quiso hacer un grafico por usuario
        if self.plotPorUsuario and cantUsuariosTop > 0:
            #hago el grafico para los usuarios
            archivoSalida = "traficoVideoUsuarios.png"
            CairoPlot.pie_plot(archivoSalida, usuariosTop, 800, 500, shadow = True, gradient = True)
            
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Video \
                           utilizado por cada usuario.")
        
        
        return seccion.generarOutput()
    
    ########################################################################################################################
    
    def subreporteTraficoDeTexto(self,requests,responses,responsesDeTexto,requestsDeTexto):
       #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        
        #Trafico de texto
        traficoTexto = 0

        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()

        #diccionario de usuarios, que contendran el trafico usado
        diccUsuarios = {}
        
        #genero los datos que despues voy a mostrar en el informe
        for each in requestsDeTexto:
            #sumo el trafico texto
            traficoTexto += len(each.body)
            
            #recorro todos los responses y genero un diccionario con los usuarios            
            usuario = each.ipOrigen
            #guardo el dominio al cual se hizo el request
            host = each.headers["host"]
            #guardo el id de las respuestas
            id = each.response
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)                        
            
        
        for each in responsesDeTexto:
            #sigo sumando el trafico de texto
            traficoTexto += len(each.body)
            
            #recorro todos los request y genero un diccionario con los usuarios            
            usuario = each.ipDestino
            id = each.id
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)        
        
        #creo una lista de tuplas(trafico, usuario) para ordenar y hacer el top
        listUsuariosTrafico = []
        
        traficoDeUsu = 0
        
        for usr in diccUsuarios:
            traficoDeUsu = diccUsuarios[usr]
            listUsuariosTrafico.append((traficoDeUsu, usr))
        
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
        
        #######################################################################
        ##################    comienzo del informe  ###########################
        #######################################################################
        #Titulo de la seccion
        seccion.section("Trafico de tipo Texto")

        #Estadisticas de texto
        seccion.texto("Estadisticas:")
        seccion.texto("En los textos siguientes se mostrar'a informaci'on del \
                      uso de la red con relaci'on al trafico de tipo Texto, \
                      estos en algunos casos pueden ocupar una porci'on significativa \
                      del trafico total.\
                      A continuaci'on se puede ver esta informaci'on, donde se \
                      muestra el trafico total (en Bytes) y el trafico de tipo texto, \
                      (tambi'en en Bytes). Estos valores pueden ser muy utiles \
                      a la hora de tener una idea general de cuanto es el tr'afico \
                      din'amico dentro de la red.")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico de Texto':str(traficoTexto)}, "Bytes")

        #Si se quiso hacer un grafico del trafico de texto
        if self.plotPorTexto:
            #hago el grafico para el trafico
            d = {'Trafico Texto': traficoTexto, 'Trafico no Texto': trafico - traficoTexto}
            archivoSalida = "traficoTexto.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)

            if cantUsuariosTop > 0:
                seccion.texto("En el siguiente gr'afico se puede apreciar mejor este volumen de trafico.")
                seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Texto \
                               con respecto al total.")        
        
        if cantUsuariosTop > 0:
            #muestro los usuarios y sus gastos.
            seccion.section("Trafico de Texto por usuario")
            seccion.texto("En esta secci'on se mostrar'a el trafico de texto \
                          que utiliza cada usuario. Para mayor comodidad, solo se \
                          visualizar'an los " + str(self.usuariosTop) + " primeros \
                          segun se configur'o en el archivo contentType.py.")
            
            texto = "\\begin{enumerate}\n"
            for i in range(cantUsuariosTop):
                texto += "\\item %s: %s %s\n"%(listUsuariosTrafico[i][1], listUsuariosTrafico[i][0], "Bytes")
            texto += "\\end{enumerate}\n"
            seccion.texto(texto)
            
            print texto
            
        else:
            seccion.section("Trafico de Texto por usuario")
            seccion.texto("No hay tr'afico de texto")
        
        
        #Si se quiso hacer un grafico por usuario
        if self.plotPorUsuario and cantUsuariosTop > 0:
            #hago el grafico para los usuarios
            archivoSalida = "traficoTextoUsuarios.png"
            CairoPlot.pie_plot(archivoSalida, usuariosTop, 800, 500, shadow = True, gradient = True)
            
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Texto \
                           utilizado por cada usuario.")
        
        
        return seccion.generarOutput()
    
    ########################################################################################################################
    
    def subreporteTraficoMultipart(self,requests,responses,responsesDeMultipart,requestsDeMultipart):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        
        #Trafico de multipart
        traficoMultipart = 0

        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()

        #diccionario de usuarios, que contendran el trafico usado
        diccUsuarios = {}
        
        #genero los datos que despues voy a mostrar en el informe
        for each in requestsDeMultipart:
            #sumo el trafico multipart
            traficoMultipart += len(each.body)
            
            #recorro todos los responses y genero un diccionario con los usuarios            
            usuario = each.ipOrigen
            #guardo el dominio al cual se hizo el request
            host = each.headers["host"]
            #guardo el id de las respuestas
            id = each.response
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)                        
            
        
        for each in responsesDeMultipart:
            #sigo sumando el trafico de multipart
            traficoMultipart += len(each.body)
            
            #recorro todos los request y genero un diccionario con los usuarios            
            usuario = each.ipDestino
            id = each.id
            
            #si el usuario ya estaba en el dicc sumo lo que uso
            if usuario in diccUsuarios.keys():
                diccUsuarios[usuario] += len(each.body)
            #sino agrego al usuario al diccionario
            else:
                diccUsuarios[usuario] = len(each.body)        
        
        #creo una lista de tuplas(trafico, usuario) para ordenar y hacer el top
        listUsuariosTrafico = []
        
        traficoDeUsu = 0
        
        for usr in diccUsuarios:
            traficoDeUsu = diccUsuarios[usr]
            listUsuariosTrafico.append((traficoDeUsu, usr))
        
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
        
        #######################################################################
        ##################    comienzo del informe  ###########################
        #######################################################################
        #Titulo de la seccion
        seccion.section("Trafico de tipo Multipart")

        #Estadisticas de multipart
        seccion.texto("Estadisticas:")
        seccion.texto("En los textos siguientes se mostrar'a informaci'on del \
                      uso de la red con relaci'on al trafico de tipo Multipart, \
                      estos en algunos casos pueden ocupar una porci'on significativa \
                      del trafico total.\
                      A continuaci'on se puede ver esta informaci'on, donde se \
                      muestra el trafico total (en Bytes) y el trafico de tipo multipart, \
                      (tambi'en en Bytes). Estos valores pueden ser muy utiles \
                      a la hora de tener una idea general de cuanto es el tr'afico \
                      din'amico dentro de la red.")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico de Multipart':str(traficoMultipart)}, "Bytes")

        #Si se quiso hacer un grafico del trafico de multipart
        if self.plotPorMultipart:
            #hago el grafico para el trafico
            d = {'Trafico Multipart': traficoMultipart, 'Trafico no Multipart': trafico - traficoMultipart}
            archivoSalida = "traficoMultipart.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)

            if cantUsuariosTop > 0:
                seccion.texto("En el siguiente gr'afico se puede apreciar mejor este volumen de trafico.")
                seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Multipart \
                               con respecto al total.")        
        
        if cantUsuariosTop > 0:
            #muestro los usuarios y sus gastos.
            seccion.section("Trafico de Multipart por usuario")
            seccion.texto("En esta secci'on se mostrar'a el trafico de multipart \
                          que utiliza cada usuario. Para mayor comodidad, solo se \
                          visualizar'an los " + str(self.usuariosTop) + " primeros \
                          segun se configur'o en el archivo contentType.py.")
            
            texto = "\\begin{enumerate}\n"
            for i in range(cantUsuariosTop):
                texto += "\\item %s: %s %s\n"%(listUsuariosTrafico[i][1], listUsuariosTrafico[i][0], "Bytes")
            texto += "\\end{enumerate}\n"
            seccion.texto(texto)
            
            print texto
            
        else:
            seccion.section("Trafico de multipart por usuario")
            seccion.texto("No hay tr'afico de multipart")
        
        
        #Si se quiso hacer un grafico por usuario
        if self.plotPorUsuario and cantUsuariosTop > 0:
            #hago el grafico para los usuarios
            archivoSalida = "traficoMultipartUsuarios.png"
            CairoPlot.pie_plot(archivoSalida, usuariosTop, 800, 500, shadow = True, gradient = True)
            
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida, "Proporci'on de trafico de Multipart \
                           utilizado por cada usuario.")
        
        
        return seccion.generarOutput()
    
    
            
    def ejecutar(self,desde,hasta):
        #obtengo todos los request y responses dentro de las fechas que me pasan
        requests, responses = self._obtenerTodoEnRango(desde,hasta)
                              
        #genero un diccionario donde las claves son los id de las respuestas
        requestsDict = dict(((each.response, each) for each in requests))

        responsesDeAplicacion = []
        requestsDeAplicacion = []
        if self.plotPorAplicacion:            
        
            # Obtenemos los responses de aplicacion
            #responsesDeAplicacion = []
            for each in responses:
                if 'content-type' in each.headers:
                    #me fijo si el tipo es del que quiero
                    if (each.headers['content-type'].split(';')[0]).split('/')[0] in self.ContentTypeAplicacion:
                        responsesDeAplicacion.append(each)
                    #print each.headers['content-type'].__repr__()
             
            # Obtenemos los request asociados a esos responses
            #requestsDeAplicacion = []
            for each in responsesDeAplicacion:
                if each.id in requestsDict:
                    requestsDeAplicacion.append(requestsDict[each.id])
                    
        ####################################################################################
            
        responsesDeAudio = []
        requestsDeAudio = []
        if self.plotPorAudio:            
        
            # Obtenemos los responses de audio            
            for each in responses:
                if 'content-type' in each.headers:
                    #me fijo si el tipo es del que quiero
                    if (each.headers['content-type'].split(';')[0]).split('/')[0] in self.ContentTypeAudio:
                        responsesDeAudio.append(each)
                    #print each.headers['content-type'].__repr__()
             
            # Obtenemos los request asociados a esos responses            
            for each in responsesDeAudio:
                if each.id in requestsDict:
                    requestsDeAudio.append(requestsDict[each.id])
                    
        ####################################################################################
        
        responsesDeImagen = []
        requestsDeImagen = []
        if self.ContentTypeImagen:
        
            # Obtenemos los responses de imagen            
            for each in responses:
                if 'content-type' in each.headers:
                    #me fijo si el tipo es del que quiero
                    if (each.headers['content-type'].split(';')[0]).split('/')[0] in self.ContentTypeImagen:
                        responsesDeImagen.append(each)
                    #print each.headers['content-type'].__repr__()
             
            # Obtenemos los request asociados a esos responses            
            for each in responsesDeImagen:
                if each.id in requestsDict:
                    requestsDeImagen.append(requestsDict[each.id])
                    
        ####################################################################################
        
        responsesDeMultipart = []
        requestsDeMultipart = []
        if self.plotPorMultipart:
        
            # Obtenemos los responses de archivos multipart            
            for each in responses:
                if 'content-type' in each.headers:
                    #me fijo si el tipo es del que quiero
                    if (each.headers['content-type'].split(';')[0]).split('/')[0] in self.ContentTypeComp:
                        responsesDeMultipart.append(each)
                    #print each.headers['content-type'].__repr__()
             
            # Obtenemos los request asociados a esos responses            
            for each in responsesDeMultipart:
                if each.id in requestsDict:
                    requestsDeMultipart.append(requestsDict[each.id])
                    
        ####################################################################################
        
        responsesDeTexto = []
        requestsDeTexto = []
        if self.plotPorTexto:
        
            # Obtenemos los responses de texto            
            for each in responses:
                if 'content-type' in each.headers:
                    #me fijo si el tipo es del que quiero
                    if (each.headers['content-type'].split(';')[0]).split('/')[0] in self.ContentTypeTexto:
                        responsesDeTexto.append(each)
                    #print each.headers['content-type'].__repr__()
             
            # Obtenemos los request asociados a esos responses            
            for each in responsesDeTexto:
                if each.id in requestsDict:
                    requestsDeTexto.append(requestsDict[each.id])
                    
        ####################################################################################
        
        responsesDeVideo = []
        requestsDeVideo = []
        if self.plotPorVideo:
        
            # Obtenemos los responses de video            
            for each in responses:
                if 'content-type' in each.headers:
                    #me fijo si el tipo es del que quiero
                    if (each.headers['content-type'].split(';')[0]).split('/')[0] in self.ContentTypeVideo:
                        responsesDeVideo.append(each)
                    #print each.headers['content-type'].__repr__()
             
            # Obtenemos los request asociados a esos responses            
            for each in responsesDeVideo:
                if each.id in requestsDict:
                    requestsDeVideo.append(requestsDict[each.id])
                    
        ####################################################################################
            
        #borro el diccionario por que ya no me sirve
        del requestsDict
        
        ####################################################################################

                        
        
        #comienzo a generar el reporte        
        res = "\\chapter{Tipo de trafico}\n"
        res += self.subreporteTrafico(responsesDeAplicacion,requestsDeAplicacion,responsesDeAudio,requestsDeAudio,responsesDeImagen,requestsDeImagen, responsesDeVideo,requestsDeVideo,responsesDeTexto,requestsDeTexto,responsesDeMultipart,requestsDeMultipart)
        res += self.subreporteTraficoDeAplicacion(requests,responses,responsesDeAplicacion,requestsDeAplicacion)
        res += self.subreporteTraficoDeAudio(requests,responses,responsesDeAudio,requestsDeAudio)
        res += self.subreporteTraficoDeImagen(requests,responses,responsesDeImagen,requestsDeImagen)
        res += self.subreporteTraficoMultipart(requests,responses,responsesDeMultipart,requestsDeMultipart)
        res += self.subreporteTraficoDeTexto(requests,responses,responsesDeTexto,requestsDeTexto)
        res += self.subreporteTraficoDeVideo(requests,responses,responsesDeVideo,requestsDeVideo)        

        print res


        return res
        

