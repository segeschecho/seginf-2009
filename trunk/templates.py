documento = """
\\documentclass[a4paper]{report}

\\usepackage{amsmath, amsthm}
\\usepackage[spanish,activeacute]{babel}
\\usepackage{a4wide}
\\usepackage{hyperref}
\\usepackage{fancyhdr}
\\usepackage{graphicx} 
\\usepackage{amssymb}
\\usepackage{amsmath}
\\usepackage[latin1]{inputenc}
\\usepackage[dvipsnames,usenames]{color}
\\usepackage{amsfonts}
\\usepackage{ulem}
\\usepackage{marvosym}
\\usepackage{colortbl}
\\usepackage{color}
\\usepackage{float}

\\parskip    = 11 pt
\\headheight	= 13.1pt
\\pagestyle	{fancy}
\\definecolor{orange}{rgb}{1,0.5,0}

\\addtolength{\\headwidth}{1.0in}

\\addtolength{\\oddsidemargin}{-0.5in}
\\addtolength{\\textwidth}{1.0in}
\\addtolength{\\topmargin}{-0.5in}
\\addtolength{\\textheight}{0.7in}


\\begin{document}
\\title{Informe sobre el uso de internet}
\\author{ReporTool}

\maketitle
\\renewcommand{\\chaptername}{Parte }

\\pagestyle{empty}
{
\\fancypagestyle{plain}
    {
    \\fancyhead{}
    \\fancyfoot{}
    \\renewcommand{\\headrulewidth}{0.0pt}
    } 
\\tableofcontents
}

\\pagenumbering{arabic}
\\fancypagestyle{plain} {
    \\fancyhead[RO]{P\\'agina \\thepage\\ de \\pageref{LastPage}}
    \\renewcommand{\\headrulewidth}{0.4pt}
}
\\pagestyle{plain}

%s

\\label{LastPage}
\\end{document}
"""



