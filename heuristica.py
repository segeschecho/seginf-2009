from persistencia import get_session, RequestHTTP, MensajeHTTP
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.traits.ui.menu import OKButton, CancelButton
from latex import LatexFactory
from reporte import Reporte
import CairoPlot
from collections import defaultdict
from enthought.pyface.message_dialog import MessageDialog

class Heuristica(Reporte):
    archivo = File
    view = View('archivo',Item('categoria',style='readonly'),
                 buttons=[OKButton, CancelButton])
    render = LatexFactory()
    categoria=Str()
    def ejecutar(self,desde,hasta):
        self.render=LatexFactory()
        try:
            f = open(self.archivo,'r')
        except Exception, e:
            MessageDialog(message="Imposible cargar el reporte a partir del archivo").open()
            raise e
        
        palabras = [x[:-1] for x in f.readlines() if x != '']
        f.close()
        
        reqs, resps = self._obtenerTodoEnRango(desde,hasta)
        reqsPorUsuario = defaultdict(lambda:[])
        respsPorUsuario = defaultdict(lambda:[])
        for each in reqs:
            reqsPorUsuario[each.ipOrigen].append(each)    

        for each in resps:
            respsPorUsuario[each.ipDestino].append(each)

        matches = defaultdict(lambda:defaultdict(lambda:0))
        print palabras
        #Obtengo cantidad requests sospechosas
        for each in reqsPorUsuario:
            dic = matches[each]
            for mensaje in reqsPorUsuario[each]:
                for palabra in palabras:
                    if palabra in mensaje.body or palabra in mensaje.uri or \
                       ('host' in mensaje.headers and palabra in mensaje.headers['host']):
                        
                        dic[palabra] +=1
        

        #Obtengo cantidad de responses sospechosos
        for each in respsPorUsuario:
            dic = matches[each]

            for mensaje in respsPorUsuario[each]:
                for palabra in palabras:
                    if palabra in mensaje.body:
                        dic[palabra] +=1

                        
        #Para cada usuario grafico las 5 palabras que mas matchearon
        self.render.chapter('Matches por usuarios para la categoria %s'%self.categoria)
        if len(matches) == 0 or all((len(matches[x])==0 for x in matches)):
            self.render.texto('No hubo ningun match para la categoria %s'%self.categoria)
            return self.render.generarOutput()
        
        for each in matches:
            if len(matches[each]) == 0:
                pass
            else:
                dic = matches[each]
                l = [k for k in dic]
                l.sort(lambda x,y:1 if dic[x] < dic[y] \
                                else -1 if dic[x] > dic[y] \
                                else 0)
                candidatas = l[0:5]
                print 'matches',matches
                print 'l',l
                data = dict(((x,dic[x]) for x in candidatas))
                print data
                self.render.section('Matches de la categoria %s para %s'%(self.categoria, each))
                self.render.itemize(data, 'matches')
                nombre = self.directorio + ('/matches%s%s.png'%(self.categoria.replace(' ',''),each.replace('.','')))
                CairoPlot.pie_plot(nombre,data,800,600,gradient=True,shadow=True)
                self.render.figure(nombre,"Principales matches para el usuario %s"%each)
        
        return self.render.generarOutput()
            
            
            
        
                    
        
