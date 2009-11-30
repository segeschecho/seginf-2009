#!/usr/bin/env python
from sqlalchemy import text
from persistencia import MensajeHTTP, RequestHTTP, ResponseHTTP, get_session, engine
from datetime import datetime,date
from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.pyface.progress_dialog import ProgressDialog
from enthought.pyface.file_dialog import FileDialog
from enthought.pyface.message_dialog import MessageDialog

import os
import tempfile
from templates import documento
from tex import convert
from reporte import Reporte
from horarioLaboral import FueraDeHorario
from blackList import ListaNegra
from ajax import Ajax
from contentType import ContentType
from nonHTTP import NonHTTP


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

class Shell(HasTraits):
    h=PythonValue
    view = View(Item('h',editor=ShellEditor(),show_label=False),resizable=True)
    
class Ventana(HasTraits):
    desde = Date(date.today())
    hasta = Date(date.today())
    scripts = List(Configurador)
    generarReporte = Button(label='Generar')
    salida = File('fede.pdf')
    ingresarComandos = Button(label='Modo interactivo')
    
    def _ingresarComandos_fired(self):

        Shell().edit_traits()
        
    
    
    def _generarReporte_fired(self):
        desde = self.desde
        hasta = self.hasta
        
        
        if hasta < desde:
            error=MessageDialog(message='Hasta debe ser posterior a desde',severity='error',title='Error')
            error.open()
            return
        seleccionados = [x for x in self.scripts if x.seleccionado]
        progress = ProgressDialog(title="Progreso", message="Generando reportes",
                              max=len(seleccionados)+3, show_time=True, can_cancel=True)
        progress.open()
        dire = tempfile.mkdtemp(suffix='reporTool', prefix='')
        
        res =""
        i = 1


        for each in seleccionados:
                print each.nombre
   
                res += each.ejecutar(desde,hasta)

                (cont, skip) = progress.update(i)
                if not cont or skip:
                    return
                i +=1


        #DEBUG        
        fe = open('fede.tex','w')
        fe.write(unicode(documento%res))
        fe.close()
        
        if self.formato in ('ambos','pdf'):
            if self.salida[-4:] != '.pdf':
                self.salida = self.salida + '.pdf'
            f = open(self.salida,'w')
            f.write(convert(unicode(documento%res), 'latex', 'pdf'))
            f.close()

        if self.formato in ('html','ambos'):
            from plasTeX.TeX import TeX
            from plasTeX.Renderers.XHTML import Renderer
            tex =TeX()
            tex.input(documento%res)
            outdir='informe'
            dire = os.getcwdu()
            if not os.path.isdir(outdir):
               os.makedirs(outdir)
        
            os.chdir(outdir)
            r = Renderer()
            r.render(tex.parse())
            os.chdir(dire)
        progress.update(len(seleccionados)+3)
        del res
    
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
    formato = Enum(['pdf','html','ambos'])
    view = View(Item('desde',style='custom' ), Item('hasta',style='simple' ), 'formato',Item('salida', editor=FileEditor(), style='text'),
            Item('scripts',editor=ListEditor(style='custom'),resizable=True,show_label=False),
            Item('generarReporte'), 'ingresarComandos',
            resizable=True,
            title="ReporTool",
             )

 
directorio = tempfile.mkdtemp(suffix='', prefix='reporTool')
f = FueraDeHorario()
c = Configurador(script = f,nombre="Fuera de horario", descripcion = "Informa el uso de internet fuera de los horarios establecidos")
l = ListaNegra(categoria = 'sexo',lista = './bl/sexo.list',directorio=directorio)
c1 = Configurador(script = l, nombre = 'Sexo', descripccion = "Muestra informacion sobre accesos a paginas de sexo")
a = Ajax(directorio=directorio)
c2 = Configurador(script = a, nombre="Trafico Ajax", descripcion = "Muestra el uso de Ajax en la red",)
l1 = ListaNegra(categoria = 'redes sociales', lista ='./bl/redsociales.list',directorio=directorio)
c3 = Configurador(script = l1, nombre='Redes sociales', descripciones = "Informa sobre el uso de redes sociales")
l2 = ListaNegra(categoria = 'warez', lista ='./bl/warez.list',directorio=directorio)
c4 = Configurador(script = l2, nombre='warez', descripciones = "Informa sobre el uso de sitios warez")
l3 = ListaNegra(categoria = 'violencia', lista ='./bl/violencia.list',directorio=directorio)
c5 = Configurador(script = l3, nombre='violencia', descripciones = "Informa sobre el uso de sitios violentos")
l4 = ListaNegra(categoria = 'Apuestas', lista ='./bl/timba.list',directorio=directorio)
c6 = Configurador(script = l4, nombre='Apuestas', descripciones = "Informa sobre el uso de sitios de apuestas")
l5 = ListaNegra(categoria = 'spyware', lista ='./bl/spyware.list',directorio=directorio)
c7 = Configurador(script = l5, nombre='spyware', descripciones = "Informa sobre el uso de sitios conocidos por introducir spyware")
ct = ContentType()
c8 = Configurador(script = ct, nombre = "Tipo de trafico", descripcion = "Muestra el tipo de trafico en la red")
non = NonHTTP()
c9 = Configurador(script = non, nombre = "Protocolos de aplicacion", descripcion = "Muestra los distintos protocolos usados")
v = Ventana(scripts=[c,c1,c2,c3,c4,c5,c6,c7,c8,c9],desde = date(2000,1,1), hasta = date(2100,1,1))

v.configure_traits()
for filename in os.listdir(directorio):
     os.remove(os.path.join(directorio, filename))
os.rmdir(directorio)

