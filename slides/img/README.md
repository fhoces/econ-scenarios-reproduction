# Static figures for the deck

`seq29.tex` is the TikZ source for the sequence diagram on the "Reading Prices Off
Quantities" slide (rendered 29). Rebuild after editing:

    cd slides/img
    pdflatex seq29.tex
    gs -dNOPAUSE -dBATCH -sDEVICE=pngalpha -r220 -sOutputFile=seq29.png seq29.pdf

The slide embeds `img/seq29.png` relative to `slides.html`, so the PNG is tracked and the
`.aux`/`.log` are not. Colours match the deck: blue #2A78D6 for the frictionless block,
orange #EB6834 for the flows, green #1BAF7A for system (39).
