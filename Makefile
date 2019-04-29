.DEFAULT_GOAL := all
.PHONY: all
all:	fmt lint

.PHONY: fmt
fmt:
	@echo "Starting  format"
	find . -name "*.py" | xargs black -l 80
	@echo "Completed format"

.PHONY: lint
lint:
	@echo "Starting  lint"
	find . -name "*.py" | xargs pylint
	@echo "Completed lint"
