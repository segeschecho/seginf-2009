from pychart import *
from pychart import pie_plot as pp
import random

theme.get_options()

theme.use_color = True
theme.default_font_size=20
theme.font_family='Times'
theme.scale=0.5
theme.reinitialize()


def pie_plot(nombre, d, x, y, gradient=True,shadow=True):

    data = [(j,d[j]) for j in d]
    ar = area.T(size=(x, y), legend=legend.T(),
            x_grid_style = None, y_grid_style = None)
    colores = [fill_style.Plain(bgcolor=color.T(r=random.random(),g=random.random(),b=random.random())) for _ in data]
    plot = pp.T(data=data,
                  shadow = (2, -2,fill_style.black),
                  arc_offsets=[0],
                  label_offset = 25,
                  arrow_style = arrow.a3,radius=min(x,y)/4,
                  fill_styles=colores)
    ar.add_plot(plot)
    if nombre[-4:] != '.png':
        nombre = nombre + '.png'

    f = open(nombre,'w')
    c = canvas.init(f,format='png')
    ar.draw(c)
    c.close()
    


