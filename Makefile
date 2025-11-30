# Makefile

# Variables
VENV := env
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Targets / install/activate dependencies

all: install test

install: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python -m venv $(VENV)
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) -m unittest discover tests
  

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete