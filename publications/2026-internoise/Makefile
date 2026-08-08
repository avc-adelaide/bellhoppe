
help:
	@echo "  py - run python code to create figures"
	@echo " tex - compile paper"

py:
	uv run in26-bh0.py
	uv run in26-bh1.py
	uv run in26-bh2.py
	uv run in26-bh3.py

tex:
	@echo "TODO :)"

bib:
	biber in26-robertson.bcf \
	    --output_format=bibtex
	    --output_file=in26-references.bib
