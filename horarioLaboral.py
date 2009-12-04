from persistencia import get_session, RequestHTTP, MensajeHTTP
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.traits.ui.menu import OKButton, CancelButton
from latex import LatexFactory
from reporte import Reporte
import CairoPlot
from collections import defaultdict

class FueraDeHorario(Reporte):
    
    minimo = 0
    maximo = 23
    semana = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
    plotHorarios = Bool
    plotUsuarios = Bool
    verbose = Bool
    horario_entrada = Range(value=8,low=0,high=23)
    horario_salida = Range(value=17,low=0,high=23)
    dias = List()
    render = Instance(LatexFactory)
    
    
    def _dias_default(self):
        return range(5)
    
    def _horario_entrada_default(self):
        return 8
    
    def _horario_salida_default(self):
        return 17
    
    view = View( 
            Item('horario_entrada', show_label=True, editor = \
                 RangeEditor(high_name = 'maximo', low_name = 'minimo',
                             mode='spinner')),
            Item('horario_salida', show_label=True,editor = \
                 RangeEditor(high_name='maximo', low_name='horario_entrada',
                             mode='spinner' )),
            Item('dias',style='custom',editor= \
                 CheckListEditor(values=[(x,semana[x]) for x in range(7)])),
            'plotUsuarios', 'plotHorarios', 'verbose',buttons=[OKButton, CancelButton]
            )
    
    
    def obtenerInfractores(self,desde,hasta):

        l = self.obtenerRequests(desde,hasta)
        res = []
        for each in l:
                if each.datetime.weekday() not in self.dias:
                    res.append(each)
                elif not (self.horario_entrada <= each.datetime.hour <= self.horario_salida):
                    res.append(each)
        return res
    
        
    def graficarUsuarios(self,desde,hasta,infractores):
        if infractores == []:
            return ""
        cant = {}
        for each in infractores:
            if each.ipOrigen not in cant:
                cant[each.ipOrigen] = 1
            else:
                cant[each.ipOrigen] +=1
        if len(cant) > 10:
            aux =cant.keys()
            aux.sort(cmp=lambda x,y: -1 if cant[x] < cant[y] else 1 if cant[x] > cant[y] else 0)
            descarte = aux[10:]
            suma = 0
            for each in descarte:
                suma += cant[each]
                del cant[each]
            cant['otros'] = suma
            
        
        self.render.section('Uso de usuarios infractores')
        self.render.texto('La cantidad de requests que hicieron los horarios infractores es:')
        self.render.nuevaLinea()
        self.render.negrita('Periodo: %s - %s'%(desde,hasta))
        self.render.itemize(cant,'requests')
        self.render.nuevaLinea()
        if self.plotUsuarios:
            nombre = self.directorio + '/FueraDeHorario_usuarios.png'
            CairoPlot.pie_plot(nombre, cant, 800, 500,shadow = True, gradient = True)
            self.render.figure(nombre,caption=\
                           'Cantidad de accesos de los usuarios infractores (sobre un total de %s pedidos)'\
                           %len(infractores))
        self.render.nuevaPagina()
        
                       
    def graficarHorarios(self,desde,hasta):
        horas = range(24)
        cant = dict(((x,0) for x in range(24)))
        pedidos = self.obtenerRequests(desde,hasta)
        if pedidos == []:
            return ""
        for each in pedidos:
            cant[each.datetime.hour]+=1
        maximo = max([cant[hora] for hora in range(24)])
        
        largo = len(pedidos)
        self.render.section('Uso de internet por horarios')
        self.render.negrita('Periodo: %s - %s'%(desde,hasta))
        self.render.nuevaLinea()
        self.render.texto('El uso de internet segun las horas es el siguiente:')
        self.render.nuevaLinea()
        cant2 = dict(((x,cant[x]) for x in cant if cant[x] > 0))
        self.render.itemize(cant2,'requests')
        self.render.nuevaLinea()
        if self.plotHorarios:
            nombre = self.directorio + '/FueraDeHorario_horarios.png'
            CairoPlot.bar_plot (nombre,
            [cant[h] for h in horas], 400, 300, 
            border = 20, grid = True, rounded_corners = True,
            h_labels=[str(x) for x in horas],
            v_labels = ['0',str(maximo/4.0),str(maximo/2.0)
            ,str(3*maximo/4.0),str(maximo)],three_dimension=True)
            self.render.figure(nombre,caption=\
                           'Distribucion de los accesos segun el horario (sobre un total de %s pedidos'\
                           %largo)

    
    def _generarItemizeVerbose(self,infractores):
        res = "\\begin{itemize}\n"
        for each in infractores:
            res +="\\item IP de origen: %s \n\n fecha: %s \n\n direccion: %s \n\n \
                      url: %s\n\n"%(each.ipOrigen, each.datetime,
                      "host desconocido" if not 'host' in each.headers \
                      else "\\verb<"+each.headers['host']+"<", "\\verb<"+each.uri+"<")
                      
        res += "\\end{itemize}\n"
        return res
        
    
    def ejecutar(self,desde,hasta):
        self.render = LatexFactory()
        infractores = self.obtenerInfractores(desde,hasta)
        self.render.chapter("Uso de internet fuera del horario laboral")
            
        self.render.negrita("Periodo: %s - %s"%(desde,hasta))
        self.render.nuevaLinea()
        if infractores == []:
                
            self.render.negrita("No hay infracciones")
            self.render.nuevaLinea()
            return self.render.generarOutput()
        else:
            if self.verbose:
                self.render.texto(self._generarItemizeVerbose(infractores))
        
            
            self.graficarHorarios(desde,hasta)
                
            
            self.graficarUsuarios(desde,hasta,infractores)            
        self.render.nuevaPagina()
                            
        return self.render.generarOutput()
        
