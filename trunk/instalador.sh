#!/bin/bash

#instalamos svn
apt-get install subversion

#instalamos latex
apt-get install texlive-latex-base
#falta el textlive-latex3
#y biblatex (conviene desde synaptic, ya que instala paquetes relacionados)

#instalamos scapy
apt-get install python-scapy

#instalamos ipython (para que nos diga bien donde estan los errores)
apt-get install ipython

#sqlite
apt-get install sqlite

#setup tools para python(para tener el easy install)
apt-get install  python-setuptools

#sqlalchemy (para la persistencia)
easy_install sqlalchemy

#numpy usado por traits
apt-get install python-numpy

#traits(para la parte visual, ventanitas etc) 
apt-get install python-traitsbackendwx
apt-get install python-traits
apt-get install python-traitsgui




