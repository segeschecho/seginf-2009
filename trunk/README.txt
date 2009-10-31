Como armar el entorno:
    1. Tener algun tipo de linux (lo hago para ubuntu y sus amigos)
    2. Instalar easy_install para python:
        > sudo apt-get install python-setuptools python-dev build-essential
    3. Instalar scapy:
        > sudo easy_install scapy
        (Si esto falla, bajar scapy de synaptic, pero es una version vieja)
    4. Instalar sqlAlchemy:
        > sudo easy_install sqlalchemy
    5. Instalar dpkt:
        bajar http://dpkt.googlecode.com/files/dpkt-1.6.tar.gz
        descomprimir
        En la carpeta dpkt, buscar bgp.py
        en ese archivo comentar con #
        las lineas:
            678             #self.failUnless(c.as == 65215)
            715             #self.failUnless(b4.open.as == 237)
        fuera de la carpeta dpkt hay un archivo setup.py, abrir una consola
        > sudo python setup.py install
    6. bajar el tp
    7. Ahora todo deberia andar, sin embargo parece haber un bugcito en scapy
        que consiste en la falta de un import, lo cual hace que se rompa todo,
        si esto le pasa a alguien mas, me avisa asi vemos como se arregla

