#!/usr/bin/env python
from enthought.traits.api import HasTraits

class Reporte(HasTraits):
    def ejecutar(self,desde,hasta):
        raise NotImplementedError


