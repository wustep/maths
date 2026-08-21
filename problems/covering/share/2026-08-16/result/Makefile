# Convenience wrapper.  The real pipeline is run_all.sh; this just names the
# common entry points.  Nothing here is required to reproduce the result.

.PHONY: all check clean paper

all: check

# Full pipeline: rebuild every generated artifact, run both verifiers over all
# four matrices, diff them, and assert every headline number.  Exit 0 or bust.
check:
	./run_all.sh

# Typeset the arXiv draft.  Needs pdflatex, which the pipeline does not.
paper: note.tex appendix_matrix.tex
	pdflatex -interaction=nonstopmode note.tex
	pdflatex -interaction=nonstopmode note.tex

clean:
	rm -f note.aux note.log note.out note.pdf note.toc
