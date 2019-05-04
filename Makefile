# 'make' by itself runs the 'all' target
.DEFAULT_GOAL := all
.PHONY: all
all:	fmt lint test

.PHONY: fmt
fmt:
	@echo "Starting  format"
	find . -name "*.py" | xargs black -l 80
	@echo "Completed format"

.PHONY: lint
lint:
	@echo "Starting  lint"
	find . -name "*.py" | xargs pylint
	find . -name "*.yml" | xargs yamllint -s
	@echo "Completed lint"

.PHONE: test
test:
	@echo "Starting  unit tests"
	find . -name "*.pyc" -delete
	find . -name "test_*.py" | xargs pytest
	@echo "Completed unit tests"
