$pdf_mode = 1;
$bibtex_use = 2;
$out_dir = 'build/latex';

$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
$biber = 'biber %O %B';

$clean_ext = 'aux bbl bcf blg fdb_latexmk fls lof log lot out run.xml synctex.gz toc xdv nav snm vrb';
$cleanup_includes_cusdep_generated = 1;
