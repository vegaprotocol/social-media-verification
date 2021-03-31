
.PHONY: black
black:
	@black -l 79 --check .

.PHONY: flake8
flake8:
	@flake8
