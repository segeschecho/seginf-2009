from reporte import Reporte
from latex import LatexFactory
from enthought.traits.api import *
from enthought.traits.ui.api import *

class ReporteTrucho(Reporte):

    flagTrucho = Bool(True)
    rangoTrucho = Range(1,10,5)
    
    def ejecutar(self,desde,hasta):
        l = LatexFactory()
        l.chapter("Reporte Trucho")
        l.texto("%s"%self.flagTrucho)
        return l.generarOutput()
