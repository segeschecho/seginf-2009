Como armar el entorno:
    1. Tener algun tipo de linux (lo hago para ubuntu y sus amigos)
    2. Instalar easy_install para python:
        > sudo apt-get install python-setuptools python-dev build-essential
    3. Instalar scapy:
        > sudo easy_install scapy
        (Si esto falla, bajar scapy de synaptic, minimo la version 2)
    4. Instalar sqlAlchemy:
        > sudo easy_install sqlalchemy
    5. Instalar dpkt:
        extraerlo, pararse en el directorio
        > sudo python setup.py install
    7. Ahora todo deberia andar, sin embargo parece haber un bugcito en 
        algunas versiones viejas descapy que consiste en la falta de un 
        import, lo cual hace que se rompa todo, si pasa esto avisme
    8. Crear las tablas:
        > python persistencia.py
        
    9. Correr el sniffer:
        > sudo python sniff.py
        para obtener ayuda:
        > python sniff.py -h
        para pararlo: ctrl+c
        
        
