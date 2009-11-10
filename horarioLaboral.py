from persistencia import get_session, RequestHTTP
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from reporte import Reporte

class FueraDeHorario(Reporte):
    
    minimo = 0
    maximo = 23
    semana = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
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
                 CheckListEditor(values=[(x,semana[x]) for x in range(7)]))
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
            res += "\\begin{itemize}\n"
            for each in infractores:
                res +="\\item %s %s\n"%(each.ipOrigen, each.datetime)
            res += "\\end{itemize}\n"
            return res
        
#variables necesarias para poder importar el modulo 
reporte = FueraDeHorario()
nombre = "Fuera de horario"
descripcion = "Informa el uso de internet fuera de los horarios establecidos"