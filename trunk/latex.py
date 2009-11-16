class LatexFactory(object):
    def __init__(self):
        self.text = ""
    
    def itemize(self,d,unidad = ""):
        self.text += "\\begin{itemize}\n"
        for each in d:
            self.text += "\\item %s: %s %s\n"%(each,d[each],unidad)
        self.text += "\\end{itemize}\n"
    
    def section(self,nombre):
        self.text += "\\section{%s}\n"%(nombre)
    
    def chapter(self,nombre):
        self.text += "\\chapter{%s}\n"%(nombre)
    
    def figure(self,direccion,caption = None,label = None):
        self.text += "\\begin{figure}[h]\n"
        self.text += "\\centering\n"
        self.text += "\\includegraphics[width=12cm]{%s}\n"%direccion
        if caption != None:
            self.text += "\\caption{%s}\n"%caption
        if label != None:
            self.text += "\\label{%s}"%label
        self.text += "\\end{figure}"
    
    def texto(self,texto):
        self.text += texto + "\n"
        
    def negrita(self,texto):
        self.text += "\\textbf{%s}\n"%texto
        
    def nuevaLinea(self):
        self.text += "\n"
        
    def nuevaPagina(self):
        self.text += "\\newpage\n"
    
    def generarOutput(self):
        return self.text
                                        
        
        
        
