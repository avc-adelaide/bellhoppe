% #################################################################################
%
% LaTeX Template LaTeX for INTER-NOISE 2026
%
% 2026 changes by Will Robertson:
%  - Create class file so main document is cleaner
%  - Improve markup for title and abstract
%  - Remove indentfirst and \noindent commands
%  - Simplify definitions for section/subsection numbering
%  - Remove UTF8 input encoding (redundant since 2018, might cause subtle bugs)
%  - Remove breakurl (seems fragile on different systems)
%  - Use caption package for proper "top caption" spacing
%  - Added Appendix example to template (manual formatting...)
%
% #################################################################################

\ProvidesClass{internoise2026-wr}

%===============================================================================
% You should only need to change this section to create a template for a new conference
\newcommand{\YearConf}{2026}
\newcommand{\CityConfCountry}{Adelaide, Australia}
\newcommand{\CityConf}{Adelaide, Australia}
\newcommand{\StateConf}{}
\newcommand{\DateConf}{9-12 August \YearConf}
\newcommand{\CountryConf}{Australia}
\newcommand{\LogoConf}{logo.png}
\newcommand{\CopyrightConf}{\\ Permission is granted for the reproduction of a fractional part of this paper published in the Proceedings of INTER-NOISE \YearConf ~ \underline{provided permission is obtained} from the author(s) \underline{and credit is given} to the author(s) and these proceedings.}
%===============================================================================


\LoadClass[a4paper,12pt]{article}

\usepackage[T1]{fontenc}

\usepackage{graphicx} % used to insert the figure
\usepackage{multirow} % used for the table
\usepackage{amsmath, amssymb, amsfonts, bm, stmaryrd}
\usepackage{txfonts}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{varwidth}
\usepackage{multicol}
\usepackage[tableposition=top]{caption}

\usepackage{geometry}
\geometry{margin=2.0cm}

\usepackage{hyperref}
\hypersetup{colorlinks=true,linkcolor=black,citecolor=black,urlcolor=black}
%\usepackage{breakurl}

\pagestyle{empty}

\usepackage{titlesec}
\titleformat{\section}{\bfseries\uppercase}{\thesection.}{1em}{}
\titleformat{\subsection}{\bfseries}{\thesubsection.}{1em}{}
\titleformat{\subsubsection}{\bfseries\itshape}{\thesubsubsection.}{1em}{}

\titlespacing*{\section}{0pt}{12pt}{8pt}
\titlespacing*{\subsection}{0pt}{6pt}{3pt}
\titlespacing*{\subsubsection}{0pt}{6pt}{0pt}

\hyphenpenalty=10000
\setlength{\emergencystretch}{3em}

\setlength{\columnsep}{1cm}
\setlength{\parindent}{0.5cm}
\setlength{\parskip}{0.0cm}

\renewcommand{\labelitemi}{\textendash}
\renewcommand{\labelitemii}{\textendash}

\renewcommand\eqref[1]{Equation~\ref{#1}}

\renewcommand{\arraystretch}{1.25}

%==============================================================================
%  REFERENCES FORMATTING
\renewcommand\@biblabel[1]{#1.}
\renewcommand{\refname}{REFERENCES} 
\setlength{\footnotesep}{12pt} 

% Sort out linespacing with references _______________________
\newlength{\bibitemsep}
\newlength{\bibparskip}
\setlength{\bibitemsep}{.2\baselineskip plus .05\baselineskip minus .05\baselineskip}
\setlength{\bibparskip}{0pt}
\let\oldthebibliography\thebibliography

\renewcommand\thebibliography[1]{%
  \oldthebibliography{#1}%
  \setlength{\parskip}{\bibitemsep}%
  \setlength{\itemsep}{\bibparskip}%
}
%==============================================================================
%  ABSTRACT FORMATTING
\usepackage{abstract}
\renewcommand{\abstractnamefont}{\centering\normalfont\bfseries\MakeUppercase}  % Title font
\renewcommand{\abstracttextfont}{\normalfont\itshape\noindent\ignorespaces}   % Body font
\setlength{\abstitleskip}{-12pt}% don't know why this needs to be -ve
\setlength{\absleftindent}{0pt}
\setlength{\absrightindent}{0pt}
%==============================================================================
%  Page headers and footers  formatting
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhead{}\fancyfoot{}
\renewcommand\headrulewidth{0.5pt}
\chead{\fontsize{10}{10}\selectfont Proceedings of INTER-NOISE \YearConf}
\fancypagestyle{firststyle}
{
   \fancyhf{}
   \fancyfoot[C]{\scriptsize\em Permission is granted for the reproduction of a fractional part of this paper published in the Proceedings of INTER-NOISE \YearConf{} provided permission is obtained from the author(s) and credit is given to the author(s) and these proceedings.}
   \renewcommand{\headrulewidth}{0pt} % removes horizontal header line
}
%==============================================================================
% TITLE FORMATTING
\renewcommand\maketitle{%
  \thispagestyle{firststyle}
  \begin{center}
  	\includegraphics[width=2in]{\LogoConf}
  \end{center}
  \vskip.5cm
  \begingroup
  \fontsize{16}{20}\selectfont\bfseries
  \@title\par
  \endgroup
}
%==============================================================================
% AUTHOR and INSTITUTION formatting
\newcounter{instit}
\def\internoise@marker{@}
\newcommand\institution[2][\internoise@marker]{%
  \medskip
  \begin{varwidth}{\textwidth}
    \ifx#1\internoise@marker\relax    
      \stepcounter{instit}%
      \textsuperscript{\theinstit}%
    \else\if\relax#1\relax\else
      \textsuperscript{#1}%
    \fi\fi
    \small#2\par%
  \end{varwidth}
  \par
}
\newcommand\markinstitution[1]{\textsuperscript{#1}}
\newcommand\markcorresponding[1]{%
  \textsuperscript{#1\if\relax#1\relax\else,\fi*}%
}
\newcommand\markpresenting[1]{%
  \textsuperscript{#1\if\relax#1\relax\else,\fi\#}%
}
\newcommand\markcorrespondingpresenting[1]{%
  \textsuperscript{#1\if\relax#1\relax\else,\fi\#}%
}
\newcommand\correspondingpresentingemail[1]{%
  \renewcommand{\thefootnote}{\#}
  \footnotetext{Presenting and corresponding author: \href{mailto:#1}{#1}}
}
\newcommand\correspondingemail[1]{%
  \renewcommand{\thefootnote}{*}
  \footnotetext{Corresponding author: \href{mailto:#1}{#1}}
}
\newcommand\presentingemail[1]{%
  \renewcommand{\thefootnote}{\#}
  \footnotetext{Presenting author: \href{mailto:#1}{#1}}
}
%==============================================================================


