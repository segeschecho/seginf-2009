#!/usr/bin/env python

from persistencia import get_session, MensajeHTTP, RequestHTTP, ResponseHTTP, RequestNoHTTP
from datetime import datetime,date
from enthought.traits.api import HasTraits

responses = {}
requests = {}
requestNoHTTP = {}
class Reporte(HasTraits):
    directorio = None
    def ejecutar(self,desde,hasta):
        raise NotImplementedError
        
    def obtenerRequests(self,desde,hasta):
        global requests
        if not (desde,hasta) in requests:
            s = get_session()
            d = datetime(desde.year,desde.month,desde.day)
            h = datetime(hasta.year,hasta.month,hasta.day)
            query = s.query(RequestHTTP)
            query.filter(RequestHTTP.datetime >= str(d) )
            query.filter(RequestHTTP.datetime <= str(h) )
        
            requests[(desde,hasta)] = query.all()
        return requests[(desde,hasta)]
        
    def obtenerResponses(self,desde,hasta):
        global responses
        if not (desde,hasta) in responses:
            s = get_session()
            d = datetime(desde.year,desde.month,desde.day)
            h = datetime(hasta.year,hasta.month,hasta.day)
            query = s.query(ResponseHTTP)
            query.filter(ResponseHTTP.datetime >= str(d) )
            query.filter(ResponseHTTP.datetime <= str(h) )
        
            responses[(desde,hasta)] = query.all()
        return responses[(desde,hasta)]
        
    def _obtenerTodoEnRango(self,d,h):
        req = self.obtenerRequests(d,h)
        resp = self.obtenerResponses(d,h)
        return (req,resp)

    def obtenerRequestsNoHTTP(self,desde,hasta):
        global requestNoHTTP
        if not (desde,hasta) in requestNoHTTP:
            s = get_session()
            d = datetime(desde.year,desde.month,desde.day)
            h = datetime(hasta.year,hasta.month,hasta.day)
            query = s.query(RequestNoHTTP)
            query.filter(RequestNoHTTP.datetime >= str(d) )
            query.filter(RequestNoHTTP.datetime <= str(h) )
        
            requestNoHTTP[(desde,hasta)] = query.all()
        return requestNoHTTP[(desde,hasta)]

