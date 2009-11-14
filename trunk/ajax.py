from persistencia import get_session, MensajeHTTP, RequestHTTP, ResponseHTTP
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from reporte import Reporte
import CairoPlot
import os
from enthought.pyface.message_dialog import MessageDialog
from enthought.pyface.progress_dialog import ProgressDialog
from enthought.traits.ui.menu import OKButton, CancelButton



class Ajax(Reporte):
    
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
        
            
    
    plotPorUsuario = Bool
    plotTrafico = Bool
    plotPorDominios = Bool
    plotDominiosPorUsuario = Bool
    
    def subreporteTrafico(self,requests,responses,responsesAjax,requestsAjax):
        trafico = sum((len(x.body) for x in requests)) + \
                  sum((len(x.body) for x in responses))
        traficoAjax = sum((len(x.body) for x in requestsAjax)) + \
                      sum((len(x.body) for x in responsesAjax))        
        res = \
        """
        \\section{Trafico Ajax}
        Estadisticas:
        \\begin{itemize}
        \\item Trafico Total: %s bytes
        \\item Trafico Ajax: %s bytes
        \\end{itemize}
        
        """ % (trafico,traficoAjax)
        if self.plotTrafico:
            d = {'Trafico Ajax': traficoAjax, 'Trafico no Ajax': trafico - traficoAjax}
            nombre = "traficoAjax.png"
            CairoPlot.pie_plot(nombre,d, 800, 500, shadow=True, gradient=True)
            res += \
            """
            \\begin{figure}[H]
            \\centering
            \\includegraphics[width=12cm]{%s/%s}
            \\caption{Porcentaje de trafico Ajax}
            \\end{figure}
            
            """%(os.getcwdu(),nombre)
        return res        
                   
        
        
    def ejecutar(self,desde,hasta):
        requests, responses = self._obtenerTodoEnRango(desde,hasta)
        
        requestsDict = dict(((each.response, each) for each in requests))
        # Obtenemos los response ajax
        
        responsesAjax = []
        for each in responses:
            if 'content-type' in each.headers:
                if each.headers['content-type'].split(';')[0] in [unicode('application/json'),
                                                    unicode('application/xml'),
                                                    unicode('application/javascript')]:
                
                    responsesAjax.append(each)
                print each.headers['content-type'].__repr__()
         
        # Obtenemos los request asociados a esos responses
        requestsAjax = []
        for each in responsesAjax:
            if each.id in requestsDict:
                requestsAjax.append(requestsDict[each.id])
        
        del requestsDict
        res = "\\chapter{Uso de Ajax}\n"
           
        res +=self.subreporteTrafico(requests,responses,responsesAjax,requestsAjax)
        return res
        
        
        
        
        
            
        
        
        
     
