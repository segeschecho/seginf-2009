#!/usr/bin/env python
from persistencia import get_session, RequestHTTP
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *

from templates import documento
from tex import convert
from reporte import Reporte
from horarioLaboral import FueraDeHorario



class Configurador(HasTraits):
    script = Instance(Reporte)
    nombre = Str("sin nombre")
    descripccion = Str("sin descripcion")
    seleccionado = Bool(True)
    configurar = Button(label='Configurar')
    
    def ejecutar(self,desde,hasta):
        return self.script.ejecutar(desde,hasta)
    
    def _configurar_fired(self):
        self.script.edit_traits()
        
    view = View(Item('nombre',style='readonly'),
                Item('configurar',editor=ButtonEditor(),show_label=False),
                Item('seleccionado'))



class IntervaloDeFechas(HasTraits):
    desde = Date
    hasta = Date
    
    view = View(Group(Item('desde',editor=DateEditor(),style='simple'),
                Item('hasta',editor=DateEditor())))
    
    
class Ventana(HasTraits):
    d = Date
    h = Date
    scripts = List(Configurador)
    generarReporte = Button(label='Generar')
    
    def _fechas_default(self):
        return IntervaloDeFechas(desde=date.today(),hasta=date.today())
        
    def _generarReporte_fired(self):
        desde = self.d
        hasta = self.h
        #FIXMEEEEE: las fechas no estan andando
        res =""
        for each in self.scripts:
            if each.seleccionado:
                res += each.ejecutar(desde,hasta)
        
        f = open('fede.pdf','w')
        f.write(convert(unicode(documento%res), 'latex', 'pdf'))
        f.close()
    
    traits_view = View(Item('d',style='custom' ), Item('h',style='simple' ),
                Item('scripts',editor=ListEditor(rows=10,use_notebook=True,deletable =False,style='custom'),resizable=True),
                Item('generarReporte',editor=ButtonEditor(),show_label=False),
                resizable=True,
                title="ReporTool",
                )

f = FueraDeHorario()
c = Configurador(script = f,nombre="Fuera de horario", descripcion = "Informa el uso de internet fuera de los horarios establecidos")

v = Ventana()

v.scripts=[c]
v.configure_traits()
print v.d

