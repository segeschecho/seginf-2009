#!/usr/bin/env python
from persistencia import get_session, RequestHTTP
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.pyface.progress_dialog import ProgressDialog
from enthought.pyface.file_dialog import FileDialog
from enthought.pyface.message_dialog import MessageDialog


from templates import documento
from tex import convert
from reporte import Reporte
from horarioLaboral import FueraDeHorario
from blackList import ListaNegra



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


class Error(HasTraits):
    mensaje=Str("Error")
    view = View(Item('mensaje',style='readonly',show_label=False), title="ERROR", buttons=['OK'])


    
class Ventana(HasTraits):
    desde = Date(date.today())
    hasta = Date(date.today())
    scripts = List(Configurador)
    generarReporte = Button(label='Generar')
    salida = File('fede.pdf')
    
    
    def _generarReporte_fired(self):
        desde = self.desde
        hasta = self.hasta
        if hasta < desde:
            Error(mensaje='Hasta debe ser posterior a desde').edit_traits()
            return
        seleccionados = [x for x in self.scripts if x.seleccionado]
        progress = ProgressDialog(title="Progreso", message="Generando reportes",
                              max=len(seleccionados)+1, show_time=True, can_cancel=True)
        progress.open()
        res =""
        i = 1
        for each in seleccionados:
                res += each.ejecutar(desde,hasta)
                progress.update(i)
                i +=1
                
        fe = open('fede.tex','w')
        fe.write(unicode(documento%res))
        fe.close()
        if self.salida[-4:] != '.pdf':
            self.salida = self.salida + '.pdf'
        f = open(self.salida,'w')
        f.write(convert(unicode(documento%res), 'latex', 'pdf'))
        f.close()
        progress.update(len(seleccionados)+1)
    
    def _scripts_changed(self,name,old,new):
        lista = self.scripts
        if len(old) >=len(new):
            return
        for each in range(len(self.scripts)):
            if self.scripts[each] is None:
                file = FileDialog()
                file.open()
                try:
                    archivo = open(file.filename,'r')
                    s = archivo.read()
                    exec s
                    c = Configurador(script=reporte,nombre=nombre, descripcion = descripcion)
                    
                    lista[each] = c
                except:
                    MessageDialog(message="Imposible cargar el reporte a partir del archivo").open()
                    del lista[each]
        return
        
    view = View(Item('desde',style='custom' ), Item('hasta',style='simple' ), Item('salida', editor=FileEditor(), style='text'),
            Item('scripts',editor=ListEditor(style='custom'),resizable=True,show_label=False),
            Item('generarReporte'),
            resizable=True,
            title="ReporTool",
             )
    

f = FueraDeHorario()
c = Configurador(script = f,nombre="Fuera de horario", descripcion = "Informa el uso de internet fuera de los horarios establecidos")
l = ListaNegra(categoria = 'sexo',lista = '/home/fede/Escritorio/seginf-2009/sexo.list')
c1 = Configurador(script = l, nombre = 'Sexo', descripccion = "Muestra informacion sobre accesos a paginas de sexo")
v = Ventana(scripts=[c,c1],desde = date(2000,1,1), hasta = date(2100,1,1))

v.configure_traits()

