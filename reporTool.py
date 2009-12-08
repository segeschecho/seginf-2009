#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


####### Imports de los distintos reportes #######
from horarioLaboral import FueraDeHorario
from blackList import ListaNegra
from ajax import Ajax
from contentType import ContentType
from nonHTTP import NonHTTP
from evolucion import EvolucionMensual
from heuristica import Heuristica
from traficoEnGral import TraficoEnGral

#from reporteTrucho import ReporteTrucho

# Clase que permite configurar las distintas opciones de los reportes
# Envuelve aun reporte
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

#Consola interactiva
class Shell(HasTraits):
    h=PythonValue
    view = View(Item('h',editor=ShellEditor(),show_label=False),resizable=True)
    
#Ventana principal de la aplicacion
class Ventana(HasTraits):
    #Componentes de la ventana
    desde = Date(date.today())
    hasta = Date(date.today())
    scripts = List(Configurador)
    generarReporte = Button(label='Generar')
    salida = File('reporte.pdf')
    directorioSalidaDeHTML = Directory('./informe')
    ingresarComandos = Button(label='Modo interactivo')
    formato = Enum(['pdf','html','ambos'])
    view = View(Item('desde',style='custom' ), Item('hasta',style='simple' ), 'formato',
            Item('salida', editor=FileEditor(), style='text'),
            Item('directorioSalidaDeHTML', editor=DirectoryEditor(),style='text'),
            Item('scripts',editor=ListEditor(style='custom'),resizable=True,show_label=False),
            Item('generarReporte'), 'ingresarComandos',
            resizable=True,
            title="ReporTool",
             )
    directorio = None
    def _ingresarComandos_fired(self):

        Shell().edit_traits()
        
        
    
    def _generarReporte_fired(self):
        desde = self.desde
        hasta = self.hasta
        
        #Valido que sea un rango valido
        if hasta < desde:
            error=MessageDialog(message='Hasta debe ser posterior a desde',severity='error',title='Error')
            error.open()
            return
        
        
        seleccionados = [x for x in self.scripts if x.seleccionado]
        
        progress = ProgressDialog(title="Progreso", message="Generando reportes",
                              max=len(seleccionados)+3, show_time=True, can_cancel=True)
        
        progress.open()
        
        res =""
        i = 1
        
        #Corro los reportes y voy armando el latex
        for each in seleccionados:
                print each.nombre
   
                res += each.ejecutar(desde,hasta)

                (cont, skip) = progress.update(i)
                if not cont or skip:
                    return
                i +=1


        #DEBUG        
        fe = open('debug.tex','w')
        fe.write(unicode(documento%res))
        fe.close()
        
        #Exporto el resultado segun que formatos de salida se pidieron
        if self.formato in ('ambos','pdf'):
            if self.salida[-4:] != '.pdf':
                self.salida = self.salida + '.pdf'
            f = open(self.salida,'w')
            f.write(convert(unicode(documento%res), 'latex', 'pdf'))
            f.close()

        
        if self.formato in ('html','ambos'):
            archivo = self.directorio + "/auxiliarTOHTML.tex"
            fe = open(archivo,'w')
            texto = documento%res
            texto=texto.replace("'a", "\\'a")
            texto=texto.replace("'e", "\\'e")
            texto=texto.replace("'i", "\\'i")
            texto=texto.replace("'o", "\\'o")
            texto=texto.replace("'u", "\\'u")
            
            fe.write(texto)
            fe.close()
            print archivo
            print self.directorioSalidaDeHTML
            out = self.directorioSalidaDeHTML.replace(" ", "\\ ")
            print os.popen('./plasTeX/plastex -d %s %s'%(out,archivo)).read()
            
        progress.update(len(seleccionados)+3)
        
        del res
    

#Directorio temporal para almacenar las imagenes que generen los reportes
directorio = tempfile.mkdtemp(suffix='', prefix='reporTool')

###########################################
##        Carga de los reportes          ##
###########################################
f = FueraDeHorario(directorio = directorio)
c = Configurador(script = f,nombre="Fuera de horario",
                 descripcion = "Informa el uso de internet fuera de los horarios establecidos")

l = ListaNegra(categoria = 'sexo',lista = './bl/sexo.list',directorio=directorio)
c1 = Configurador(script = l, nombre = 'Sexo',
                  descripccion = "Muestra informacion sobre accesos a paginas de sexo")

a = Ajax(directorio=directorio)
c2 = Configurador(script = a, nombre="Trafico Ajax",
                  descripcion = "Muestra el uso de Ajax en la red",)

l1 = ListaNegra(categoria = 'redes sociales',
                lista ='./bl/redsociales.list',directorio=directorio)
c3 = Configurador(script = l1, nombre='Redes sociales',
                  descripciones = "Informa sobre el uso de redes sociales")

l2 = ListaNegra(categoria = 'Warez', lista ='./bl/warez.list',
                directorio=directorio)
c4 = Configurador(script = l2, nombre='Warez',
                  descripciones = "Informa sobre el uso de sitios warez")

l3 = ListaNegra(categoria = 'Violencia', lista ='./bl/violencia.list',
                directorio=directorio)
c5 = Configurador(script = l3, nombre='Violencia',
                  descripciones = "Informa sobre el uso de sitios violentos")

l4 = ListaNegra(categoria = 'Apuestas', lista ='./bl/timba.list',
                directorio=directorio)
c6 = Configurador(script = l4, nombre='Apuestas',
                  descripciones = "Informa sobre el uso de sitios de apuestas")

l5 = ListaNegra(categoria = 'Spyware', lista ='./bl/spyware.list',
                directorio=directorio)
c7 = Configurador(script = l5, nombre='Spyware',
                  descripciones = "Informa sobre el uso de sitios conocidos por introducir spyware")

ct = ContentType(directorio = directorio)
c8 = Configurador(script = ct, nombre = "Tipo de trafico",
                  descripcion = "Muestra el tipo de trafico en la red")

non = NonHTTP(directorio = directorio)
c9 = Configurador(script = non, nombre = "Protocolos de aplicacion",
                  descripcion = "Muestra los distintos protocolos usados")

ev = EvolucionMensual(directorio = directorio)
c10 = Configurador(script = ev, nombre = "Evolucion mensual",
                   descripcion = "Muestra como varia el trafico mensualmente para los sitios seleccionados")

he = Heuristica(directorio = directorio, categoria = 'Sexo',
                archivo = './heuristicas/sex.txt')
c11 = Configurador(script = he, nombre = "Heuristica sexo",
                   descripcion = "Realiza una busqueda heuristica para detectar visitas a paginas de sexo")

tg = TraficoEnGral(directorio=directorio)
c12 = Configurador(script = tg, nombre="Sitios con mas Trafico", descripcion = "Muestra los sitios con mas trafico en el periodo seleccionado")



#######################################################
##      Otros reportes definidos por el usuario       #
#######################################################
#rt = ReporteTrucho()
#configDePrueba = Configurador(script = rt, nombre="Reporte Trucho",descripcion = "Soy un reporte muy trucho")



######################################################
configuradores=[c,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12]


## Registrar en esta lista los configuradores definidos por el usuario
#configuradores.append(configDePrueba)



v = Ventana(scripts=configuradores,desde = date(2009,1,1), hasta = date(2010,1,1),directorio=directorio)
v.configure_traits()

for filename in os.listdir(directorio):
     os.remove(os.path.join(directorio, filename))
os.rmdir(directorio)

