#!/usr/bin/env python
#!/usr/bin/python
# -*- coding: utf8 -*-



from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, PickleType,Binary, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import json

engine = create_engine('sqlite:///http.sqlite')
text = text

Base = declarative_base()
class MensajeHTTP(Base):
    __tablename__ = 'mensajes'
    
    id = Column(Integer, primary_key=True)
    ipOrigen = Column(String)
    ipDestino = Column(String)
    portOrigen = Column(Integer)
    portDestino = Column(Integer)
    version = Column(String)
    headers = Column(PickleType(pickler=json))
    body = Column(PickleType)
    datetime = Column(DateTime)


    def __init__(self, ipOrigen, ipDestino, portOrigen, portDestino,version,headers,body,datetime):
        self.ipOrigen = ipOrigen
        self.ipDestino = ipDestino
        self.portOrigen = portOrigen
        self.portDestino = portDestino
        self.version = version
        self.headers = headers
        self.body = body
        self.datetime = datetime
        


    def __repr__(self):
        return "<id:%s headers:%s from:%s %s to:%s %s>" % (self.id,
                                                     self.headers, 
                                                     self.ipOrigen, self.portOrigen,
                                                     self.ipDestino, self.portDestino)


class RequestNoHTTP(Base):
    __tablename__ = 'requestsNo'
    id = Column(Integer, primary_key=True)
    ipOrigen = Column(String)
    ipDestino = Column(String)
    portOrigen = Column(Integer)
    portDestino = Column(Integer)
    body = Column(PickleType)
    datetime = Column(DateTime)
    
    def __init__(self,ipOrigen,ipDestino,portOrigen,portDestino,body,datetime):
        self.ipOrigen = ipOrigen
        self.ipDestino = ipDestino
        self.portDestino = portDestino
        self.portOrigen = portOrigen
        self.body = body
        self.datetime = datetime
        
class ResponseNoHTTP(Base):
    __tablename__ = 'responsesNo'
    id = Column(Integer, primary_key=True)
    ipOrigen = Column(String)
    ipDestino = Column(String)
    portOrigen = Column(Integer)
    portDestino = Column(Integer)
    body = Column(PickleType)
    datetime = Column(DateTime)
    
    def __init__(self,ipOrigen,ipDestino,portOrigen,portDestino,body,datetime):
        self.ipOrigen = ipOrigen
        self.ipDestino = ipDestino
        self.portDestino = portDestino
        self.portOrigen = portOrigen
        self.body = body
        self.datetime = datetime
    
class RequestHTTP(MensajeHTTP):
    __tablename__ = 'requests'
    __mapper_args__ = {'polymorphic_identity': 'requests'}
    id = Column(Integer, ForeignKey('mensajes.id'), primary_key=True)
    method = Column(String)
    uri = Column(String)
    response = Column(Integer, ForeignKey('responses.id'))
    def __init__(self,ipOrigen, ipDestino, portOrigen, portDestino, version,
                 headers,body, datetime,method, uri, response = None):
        super(RequestHTTP,self).__init__(ipOrigen, ipDestino, portOrigen,
                                         portDestino,version, headers,body,datetime)
        self.uri = uri
        self.method = method
        self.response = response
        
class ResponseHTTP(MensajeHTTP):
    __tablename__ = 'responses'
    __mapper_args__ = {'polymorphic_identity': 'responses'}
    id = Column(Integer, ForeignKey('mensajes.id'), primary_key=True)
    status = Column(String)
    razon = Column(String)
    
    def __init__(self,ipOrigen, ipDestino, portOrigen, portDestino, version,
                 headers,body, datetime,status, razon):
        super(ResponseHTTP,self).__init__(ipOrigen, ipDestino, portOrigen,
                                          portDestino,version ,headers,body,datetime)
        self.status = status
        self.razon = razon
        

def crear_tablas():
    Base.metadata.create_all(engine)

def borrar_tablas():
    Base.metadata.reflect(bind=engine)
    for table in reversed(Base.metadata.sorted_tables):
        engine.execute(table.delete())

def get_session():
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == '__main__':
    try:
        borrar_tablas()
    except:
        crear_tablas()

