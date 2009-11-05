#!/usr/bin/env python
#Import get_session y las clases que necesito usar
from persistencia import get_session, RequestHTTP
from datetime import datetime

lunAVie = range(5)
def fueraDeHorario(horario_entrada=8,horario_salida=17, dias=lunAVie):
    #Lo primero que hago es obtener la sesion
    s = get_session()
    # s.query(Clase) me permite hacer querys sobre sus instancias
    # en esta caso uso all que me da todas, pero se puede usar otros
    # metodos como filter
    l = s.query(RequestHTTP).all()
    res = []
    for each in l:
        if each.datetime.weekday() not in dias:
            res.append(each)
        elif not (horario_entrada <= each.datetime.hour <= horario_salida):
            res.append(each)
        
    return res
        
        
        
res =fueraDeHorario()
for each in res:
    print "Pedido fuera del horario laboral: ", each

