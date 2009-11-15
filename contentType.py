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
    plotPorComprimidos = Bool  
   
   
    ContentTypeAplicacion = [unicode('application/atom+xml'), \
                             unicode('application/iges'), \
                             unicode('application/javascript'), \
                             unicode('application/dxf'), \
                             unicode('application/mp4'), \
                             unicode('application/iges'), \
                             unicode('application/octet-stream'), \
                             unicode('application/msword'), \
                             unicode('application/pdf'), \
                             unicode('application/postscript'), \
                             unicode('application/rtf'), \
                             unicode('application/sgml'), \
                             unicode('application/vnd.ms-excel'), \
                             unicode('application/vnd.ms-powerpoint'), \
                             unicode('application/xml'), \
                             unicode('application/x-tar'), \
                             unicode('application/zip')]
    
    ContentTypeAudio =  [unicode('audio/basic'), \
                         unicode('audio/mpeg'), \
                         unicode('audio/mp4'), \
                         unicode('audio/x-aiff'), \
                         unicode('audio/x-wav')]
    
    ContentTypeImagen = [unicode('image/gif'), \
                        unicode('image/jpeg'), \
                        unicode('image/png'), \
                        unicode('image/tiff'), \
                        unicode('image/x-portable-bitmap'), \
                        unicode('image/x-portable-graymap'), \
                        unicode('image/x-portable-pixmap')]
    
    ContentTypeComp =   [unicode('multipart/x-zip'), \
                        unicode('multipart/x-gzip')]
    
    ContentTypeTexto =  [unicode('text/css'), \
                        unicode('text/csv'), \
                        unicode('text/html'), \
                        unicode('text/plain'), \
                        unicode('text/richtext'), \
                        unicode('text/rtf'), \
                        unicode('text/tab-separated-value'), \
                        unicode('text/xml')]
    
    ContentTypeVideo = [unicode('video/h264'), \
                        unicode('video/dv'), \
                        unicode('video/mpeg'), \
                        unicode('video/quicktime'), \
                        unicode('video/msvideo')]
   
   
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
        
    ########################################################################################################################

    def subreporteTrafico(self,responsesDeAplicacion,requestsDeAplicacion,responsesDeAudio,requestsDeAudio,responsesDeImagen,requestsDeImagen,responsesDeVideo,requestsDeVideo,responsesDeTexto,requestsDeTexto,responsesDeComprimidos,requestsDeComprimidos):
        
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
        #Calculo el trafico de archivos comprimidos
        traficoComprimido = sum((len(x.body) for x in requestsDeComprimidos)) + \
                            sum((len(x.body) for x in responsesDeComprimidos))
    
        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()
    
        #Titulo de la seccion
        seccion.section("Tipo de Trafico")
    
        #Estadisticas de trafico de aplicacion
        seccion.texto("Estadisticas:")
        seccion.itemize({'Trafico de Aplicacion':str(traficoAplicacion), 'Trafico de Audio':str(traficoAudio), 'Trafico de Imagen':str(traficoImagen), 'Trafico de Video':str(traficoVideo), 'Trafico de Texto':str(traficoTexto), 'Trafico Comprimido':str(traficoComprimido)})
    
        #Si se quiso hacer un grafico en el reporte lo hago
        if self.plotPorTrafico:
            d = {'Trafico de Aplicacion': traficoAplicacion, 'Trafico de Audio': traficoAudio, 'Trafico de Imagen': traficoImagen, 'Trafico de video': traficoVideo, 'Trafico de Texto': traficoTexto, 'Trafico Comprimido': traficoComprimido}
            archivoSalida = "trafico.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)
    
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida)
    
        return seccion.generarOutput()

    ########################################################################################################################

    def subreporteTraficoDeAplicacion(self,requests,responses,responsesDeAplicacion,requestsDeAplicacion):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        #Calculo el trafico de aplicacion
        traficoAplicacion = sum((len(x.body) for x in requestsDeAplicacion)) + \
                            sum((len(x.body) for x in responsesDeAplicacion))
    
        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()
    
        #Titulo de la seccion
        seccion.section("Trafico de tipo Aplicacion")
    
        #Estadisticas de trafico de aplicacion
        seccion.texto("Estadisticas:")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico de Aplicacion':str(traficoAplicacion)})
    
        #Si se quiso hacer un grafico en el reporte lo hago
        if self.plotPorAplicacion:
            d = {'Trafico de Aplicacion': traficoAplicacion, 'Trafico no Aplicacion': trafico - traficoAplicacion}
            archivoSalida = "traficoAplicacion.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)
    
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida)
    
        return seccion.generarOutput()
        
    ########################################################################################################################
        
    def subreporteTraficoDeAudio(self,requests,responses,responsesDeAudio,requestsDeAudio):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        #Calculo el trafico de audio
        traficoAudio = sum((len(x.body) for x in requestsDeAudio)) + \
                            sum((len(x.body) for x in responsesDeAudio))
    
        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()
    
        #Titulo de la seccion
        seccion.section("Trafico de tipo Audio")
    
        #Estadisticas de trafico de audio
        seccion.texto("Estadisticas:")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico de Audio':str(traficoAudio)})
    
        #Si se quiso hacer un grafico en el reporte lo hago
        if self.plotPorAudio:
            d = {'Trafico de Audio': traficoAudio, 'Trafico no Audio': trafico - traficoAudio}
            archivoSalida = "traficoAudio.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)
    
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida)
    
        return seccion.generarOutput()
    
    ########################################################################################################################
    
    def subreporteTraficoDeImagen(self,requests,responses,responsesDeImagen,requestsDeImagen):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        #Calculo el trafico de imagen
        traficoImagen = sum((len(x.body) for x in requestsDeImagen)) + \
                            sum((len(x.body) for x in responsesDeImagen))
    
        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()
    
        #Titulo de la seccion
        seccion.section("Trafico de tipo Imagen")
    
        #Estadisticas de trafico de imagen
        seccion.texto("Estadisticas:")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico de Imagen':str(traficoImagen)})
    
        #Si se quiso hacer un grafico en el reporte lo hago
        if self.plotPorImagenes:
            d = {'Trafico de Imagen': traficoImagen, 'Trafico no Imagen': trafico - traficoImagen}
            archivoSalida = "traficoImagen.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)
    
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida)
    
        return seccion.generarOutput()
    
    ########################################################################################################################
    
    def subreporteTraficoDeVideo(self,requests,responses,responsesDeVideo,requestsDeVideo):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        #Calculo el trafico de video
        traficoVideo = sum((len(x.body) for x in requestsDeVideo)) + \
                       sum((len(x.body) for x in responsesDeVideo))
    
        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()
    
        #Titulo de la seccion
        seccion.section("Trafico de tipo Video")
    
        #Estadisticas de trafico de video
        seccion.texto("Estadisticas:")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico de Video':str(traficoVideo)})
    
        #Si se quiso hacer un grafico en el reporte lo hago
        if self.plotPorVideo:
            d = {'Trafico de Video': traficoVideo, 'Trafico no Video': trafico - traficoVideo}
            archivoSalida = "traficoVideo.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)
    
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida)
    
        return seccion.generarOutput()
    
    ########################################################################################################################
    
    def subreporteTraficoDeTexto(self,requests,responses,responsesDeTexto,requestsDeTexto):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        #Calculo el trafico de texto
        traficoTexto = sum((len(x.body) for x in requestsDeTexto)) + \
                       sum((len(x.body) for x in responsesDeTexto))
    
        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()
    
        #Titulo de la seccion
        seccion.section("Trafico de tipo Texto")
    
        #Estadisticas de trafico de texto
        seccion.texto("Estadisticas:")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico de Texto':str(traficoTexto)})
    
        #Si se quiso hacer un grafico en el reporte lo hago
        if self.plotPorTexto:
            d = {'Trafico de Texto': traficoTexto, 'Trafico no Texto': trafico - traficoTexto}
            archivoSalida = "traficoTexto.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)
    
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida)
    
        return seccion.generarOutput()
    
    ########################################################################################################################
    
    def subreporteTraficoComprimido(self,requests,responses,responsesDeComprimidos,requestsDeComprimidos):
        #Calculo el trafico total en bytes sumando los bodys
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        #Calculo el trafico de archivos comprimidos
        traficoComprimido = sum((len(x.body) for x in requestsDeComprimidos)) + \
                            sum((len(x.body) for x in responsesDeComprimidos))
    
        #Comienzo a escribir la seccion del reporte
        seccion = LatexFactory()
    
        #Titulo de la seccion
        seccion.section("Trafico Comprimido")
    
        #Estadisticas de trafico de archivos comprimidos
        seccion.texto("Estadisticas:")
        seccion.itemize({'Trafico Total':str(trafico), 'Trafico Comprimido':str(traficoComprimido)})
    
        #Si se quiso hacer un grafico en el reporte lo hago
        if self.plotPorComprimidos:
            d = {'Trafico Comprimido': traficoComprimido, 'Trafico no Comprimido': trafico - traficoComprimido}
            archivoSalida = "traficoComprimido.png"
            CairoPlot.pie_plot(archivoSalida, d, 800, 500, shadow = True, gradient = True)
    
            seccion.figure(str(os.getcwdu()) + "/" + archivoSalida)
    
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
                    if each.headers['content-type'].split(';')[0] in self.ContentTypeAplicacion:
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
                    if each.headers['content-type'].split(';')[0] in self.ContentTypeAudio:
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
                    if each.headers['content-type'].split(';')[0] in self.ContentTypeImagen:
                        responsesDeImagen.append(each)
                    #print each.headers['content-type'].__repr__()
             
            # Obtenemos los request asociados a esos responses            
            for each in responsesDeImagen:
                if each.id in requestsDict:
                    requestsDeImagen.append(requestsDict[each.id])
                    
        ####################################################################################
        
        responsesDeComprimidos = []
        requestsDeComprimidos = []
        if self.plotPorComprimidos:
        
            # Obtenemos los responses de archivos comprimidos            
            for each in responses:
                if 'content-type' in each.headers:
                    #me fijo si el tipo es del que quiero
                    if each.headers['content-type'].split(';')[0] in self.ContentTypeComp:
                        responsesDeComprimidos.append(each)
                    #print each.headers['content-type'].__repr__()
             
            # Obtenemos los request asociados a esos responses            
            for each in responsesDeComprimidos:
                if each.id in requestsDict:
                    requestsDeComprimidos.append(requestsDict[each.id])
                    
        ####################################################################################
        
        responsesDeTexto = []
        requestsDeTexto = []
        if self.plotPorTexto:
        
            # Obtenemos los responses de texto            
            for each in responses:
                if 'content-type' in each.headers:
                    #me fijo si el tipo es del que quiero
                    if each.headers['content-type'].split(';')[0] in self.ContentTypeTexto:
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
                    if each.headers['content-type'].split(';')[0] in self.ContentTypeVideo:
                        responsesDeVideo.append(each)
                    #print each.headers['content-type'].__repr__()
             
            # Obtenemos los request asociados a esos responses            
            for each in responsesDeVideo:
                if each.id in requestsDict:
                    requestsDeVideo.append(requestsDict[each.id])
                    
        ####################################################################################
            
        #borro el diccionario por que ya no me sirve
        del requestsDict

        #comienzo a generar el reporte        
        res = "\\chapter{Tipo de trafico}\n"
        res += self.subreporteTrafico(responsesDeAplicacion,requestsDeAplicacion,responsesDeAudio,requestsDeAudio,responsesDeImagen,requestsDeImagen, responsesDeVideo,requestsDeVideo,responsesDeTexto,requestsDeTexto,responsesDeComprimidos,requestsDeComprimidos)
        res += self.subreporteTraficoDeAplicacion(requests,responses,responsesDeAplicacion,requestsDeAplicacion)
        res += self.subreporteTraficoDeAudio(requests,responses,responsesDeAudio,requestsDeAudio)
        res += self.subreporteTraficoDeImagen(requests,responses,responsesDeImagen,requestsDeImagen)
        res += self.subreporteTraficoComprimido(requests,responses,responsesDeComprimidos,requestsDeComprimidos)
        res += self.subreporteTraficoDeTexto(requests,responses,responsesDeTexto,requestsDeTexto)
        res += self.subreporteTraficoDeVideo(requests,responses,responsesDeVideo,requestsDeVideo)


        print res


        return res
        

