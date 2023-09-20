import os
from argparse import ArgumentParser
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

PREAMBLE=R"""\documentclass[a4paper,10pt]{article}

\usepackage[top=0.75in, bottom=0.2in, left=0.35in, right=0.35in]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{url}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{array}
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=cyan,
    pdftitle={Andrey Rybakov CV},
    pdfpagemode=FullScreen,
    }

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}

\usepackage{color}
\usepackage{tabularray}
\definecolor{mygrey}{gray}{0.82}
\textheight=9.75in
\raggedbottom

\setlength{\tabcolsep}{0in}
\newcommand{\isep}{-2 pt}
\newcommand{\lsep}{-0.5cm}
\newcommand{\psep}{-0.6cm}
\renewcommand{\labelitemii}{$\circ$}

\pagestyle{empty}

%-----------------------------------------------------------
%Custom commands
\newcommand{\resitem}[1]{\item #1 \vspace{-2pt}}
\newcommand{\resheading}[1]{{\small \colorbox{mygrey}{\begin{minipage}{0.99\textwidth}{\textbf{#1 \vphantom{p\^{E}}}}\end{minipage}}}}
\newcommand{\ressubheading}[3]{
\begin{tabular*}{6.62in}{l @{\extracolsep{\fill}} r}
	\textsc{{\textbf{#1}}} & \textsc{\textit{[#2]}} \\
\end{tabular*}\vspace{-8pt}}
%-----------------------------------------------------------

\begin{document}

\begin{center}
    \LARGE
    \textcolor{black}{Curriculum vitae}
\end{center}
"""

FILENAME="Andrey-Rybakov-CV"

def write_type_map(contents):
    result = []
    for content in contents:
        name = content["name"]
        if "links" in content:
            value = content["links"][0]["name"]
        else:
            value = content["value"]
        result.append(f"{name}"+R": \textbf{"+f"{value}"+R"}\\"+"\n")
    return result

def write_type_time_table(contents):
    result = []
    result.append(R"\begin{tblr}{t{0.15\textwidth}t{0.75\textwidth}}"+"\n")
    for content in contents:
        if "year" in content:
            if "dates" in content:
                result.append(f"{content['dates']} ")
            result.append(f"{content['year']} & ")
        if "title" in content:
            result.append(R"\textbf{"+f"{content['title']}"+"}.\n")
        if "department" in content:
            result.append(f"{content['department']},\n")
        if "institution" in content:
            result.append(f"{content['institution']}.\n")
        if "description" in content:
            for item in content["description"]:
                result.append(f"{item}.\n")
        if "location" in content:
            result.append(f"{content['location']}.\n")
        result.append(R"\\"+"\n")
    result.append(R"\end{tblr}")
    return result

def generate_input(root_dir):
    latex_input = []

    cv_data = load(open(os.path.join(root_dir, "_data", "cv.yml")), Loader=Loader)

    for section in cv_data:
        latex_input.append(R"\noindent \resheading{\textbf{"+f"{section['title'].upper()}"+R"}}\nopagebreak\\[0.2cm]"+"\n")

        if section["type"] == "map":
            latex_input.extend(write_type_map(section["contents"]))
        elif section["type"] == "time_table":
            latex_input.extend(write_type_time_table(section["contents"]))

        latex_input.append(R"\hfill\\[0.2cm]"+"\n")

    return latex_input

def generate_bibliography(root_dir):
    latex_input = ["\n"+R"\noindent \resheading{\textbf{PUBLICATIONS}}\\[0.2cm]"+"\n"+R"\begin{itemize}"+"\n"]

    bib_data = []
    with open(os.path.join(root_dir, "_bibliography", "papers.bib"), "r") as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            if lines[i].startswith("@article{"):
                bib_data.append({})
                i += 1
                while not lines[i].startswith("}"):
                    name = lines[i].split("=")[0].strip()
                    value = lines[i].split("=")[1].strip(" {},\n")
                    bib_data[-1][name] = value
                    i += 1
            i += 1

    bib_data.sort(key=lambda x: int(x["year"]), reverse=True)
    
    for paper in bib_data:
        latex_input.append(R"\item ")
        if "author" in paper:
            authors = paper['author'].split(" and ")
            family_names = [x.split(',')[0].strip() for x in authors]
            first_names = [x.split(',')[1].strip() for x in authors]
            first_names = [". ".join([name[0] for name in names.split()]) for names in first_names]
            authors = [f"{family_names[i]} {first_names[i]}." for i in range(len(family_names))]
            latex_input.append(", ".join(authors)+"\n")
        if "title" in paper:
            latex_input.append(R"\textit{"+f"{paper['title']}"+"}\n")
        if "journal" in paper and "year" in paper:
            latex_input.append(R"\textbf{"+f"{paper['journal']}, {paper['year']}."+"}\n")
        elif "journal" in paper:
            latex_input.append(R"\textbf{"+f"{paper['journal']}."+"}\n")
        elif "year" in paper:
            latex_input.append(R"\textbf{"+f"{paper['year']}."+"}\n")
        next_entry = []
        if "volume" in paper:
            next_entry.append(paper['volume'])
        if "number" in paper:
            next_entry.append(paper['number'])
        if "pages" in paper:
            next_entry.append(paper['pages'])
        latex_input.append(", ".join(next_entry) + ".\n")
        if "doi" in paper:
            latex_input.append("\n"+R"\href{https://doi.org/"+paper["doi"]+R"}{"+paper["doi"]+"}\n")

    latex_input.append(R"\end{itemize}\hfill\\[0.2cm]")
    return latex_input

def main(root_dir):
    latex_input = [PREAMBLE]
    latex_input.extend(generate_input(root_dir))
    latex_input.extend(generate_bibliography(root_dir))
    latex_input.append(R"\end{document}"+"\n")

    # Write the input
    os.makedirs(os.path.join(root_dir, "latex-cv"), exist_ok=True)
    with open(os.path.join(root_dir, "latex-cv", f"{FILENAME}.tex"), "w") as f:
        f.writelines(latex_input)

    # Build the pdf
    os.system(f"cd {os.path.join(root_dir, 'latex-cv')} && pdflatex {FILENAME}.tex -synctex=1 -interaction=nonstopmode")
    os.system(f"cp {os.path.join(root_dir, 'latex-cv', f'{FILENAME}.pdf')} {os.path.join(root_dir, 'assets', 'pdf', f'{FILENAME}.pdf')}")
    os.system(f"rm -r {os.path.join(root_dir, 'latex-cv')}")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-rd","--root-dir", required=True, help="Root directory of the project")
    args = parser.parse_args()
    main(**vars(args))
