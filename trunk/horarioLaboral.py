from persistencia import get_session, RequestHTTP, MensajeHTTP
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.traits.ui.menu import OKButton, CancelButton

from reporte import Reporte
import CairoPlot
from collections import defaultdict
import os

class FueraDeHorario(Reporte):
    
    minimo = 0
    maximo = 23
    semana = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
    plotHorarios = Bool
    plotUsuarios = Bool
    horario_entrada = Range(value=8,low=0,high=23)
    horario_salida = Range(value=17,low=0,high=23)
    dias = List()
    
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
            'plotUsuarios', 'plotHorarios', buttons=[OKButton, CancelButton]
            )
    
    
    def obtenerInfractores(self,desde,hasta):
        s = get_session()

        l = s.query(RequestHTTP).all()
        res = []
        for each in l:
            if desde < date(each.datetime.year,each.datetime.month,each.datetime.day) < hasta:
                if each.datetime.weekday() not in self.dias:
                    res.append(each)
                elif not (self.horario_entrada <= each.datetime.hour <= self.horario_salida):
                    res.append(each)
        return res
    
    def obtenerPedidos(self,desde,hasta):
        s = get_session()
        res = []
        l = s.query(RequestHTTP).all()
        for each in l:
            if desde < date(each.datetime.year,each.datetime.month,each.datetime.day) < hasta:
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
        CairoPlot.pie_plot("FueraDeHorario_usuarios.png", cant, 800, 500,shadow = True, gradient = True)
        return \
                      """
                       \\section{Uso de usuarios infractores}
                       
                       \\textbf{Periodo: %s - %s}\n
                       La figura \\ref{fuerdaDeHorario_usuarios} muestra la cantidad de accesos que hicieron los usuarios fuera del horario
                       laboral
                       \\begin{figure}[H]
                       \\centering
                       \\includegraphics[width=12cm]{%s/FueraDeHorario_usuarios.png}
                       \\caption{Cantidad de accesos de los usuarios infractores (sobre un total de %s pedidos)}
                       \\label{fuerdaDeHorario_usuarios}
                       \\end{figure}
      
                       """%(desde,hasta,os.getcwdu(),len(infractores))
                       
    def graficarHorarios(self,desde,hasta):
        horas = range(24)
        cant = defaultdict(lambda:0)
        pedidos = self.obtenerPedidos(desde,hasta)
        if pedidos == []:
            return ""
        for each in pedidos:
            cant[each.datetime.hour]+=1
        maximo = max([cant[hora] for hora in range(23)])
        CairoPlot.bar_plot ('FueraDeHorario_horarios.png',
            [cant[h] for h in horas], 400, 300, 
            border = 20, grid = True, rounded_corners = True,
            h_labels=[str(x) for x in horas],
            v_labels = ['0',str(maximo/4.0),str(maximo/2.0)
            ,str(3*maximo/4.0),str(maximo)],three_dimension=True)
        largo = len(pedidos)
        return """
                \\section{Uso de internet por horarios}
                  
                \\textbf{Periodo: %s - %s}\n
                La figura \\ref{fuerdaDeHorario_horarios} muestra el uso de
                internet a lo largo de las distintas horas del dia
                \\begin{figure}[H]
                \\centering
                \includegraphics[width=10cm]{%s/FueraDeHorario_horarios.png}
                \\caption{Distribucion de los accesos segun el horario (sobre un total de %s pedidos)}
                \label{fuerdaDeHorario_horarios}
                \\end{figure}
                      
                """%(desde,hasta,os.getcwdu(),largo)
    
    def ejecutar(self,desde,hasta):
        infractores = self.obtenerInfractores(desde,hasta)
        if infractores == []:
            return \
            """
            \\chapter{Uso de internet fuera del horario laboral}\n
            \\textbf{Periodo: %s - %s}\n\n
            \\textbf{No hay infracciones}\n
            """%(desde,hasta)
        else:
            res = "\\chapter{Uso de internet fuera del horario laboral}\n"
            res +="\\textbf{Periodo: %s - %s}\n\n"%(desde,hasta)
            res += "\\begin{itemize}\n"
            for each in infractores:
                res +="\\item IP de origen: %s \n\n fecha: %s \n\n direccion: %s \n\n \
                      url: %s\n\n"%(each.ipOrigen, each.datetime,
                      "host desconocido" if not 'host' in each.headers \
                      else "\\verb<"+each.headers['host']+"<", "\\verb<"+each.uri+"<")
                      
            res += "\\end{itemize}\n"
            
            if self.plotHorarios:
                res += self.graficarHorarios(desde,hasta)
                
            if self.plotUsuarios:
                res += self.graficarUsuarios(desde,hasta,infractores)            
            res += "\\newpage"    
                            
            return res
        
#variables necesarias para poder importar el modulo 
reporte = FueraDeHorario()
nombre = "Fuera de horario"
descripcion = "Informa el uso de internet fuera de los horarios establecidos"
