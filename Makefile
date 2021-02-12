PYTHON = /usr/bin/python3
VENV = venv/bin/python

build: venv requirements
	export PYTHONPATH=$$PWD
	$(PYTHON) src/utils/setup.py
	-cp devbot.service /etc/systemd/system
	@cat LICENSE

venv:
	$(PYTHON) -m venv venv

requirements:
	$(VENV) -m pip install -r requirements.txt

clean:
	rm -rf venv/ src/__pycache__ src/cogs/__pycache__ src/.env src/static-config.json src/utils/__pycache__
	-rm /etc/systemd/system/devbot.service
	-git pull