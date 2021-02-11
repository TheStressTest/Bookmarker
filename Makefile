PYTHON = /usr/bin/python3
VENV = venv/bin/python

build: venv requirements
	-cp devbot.service /etc/systemd/system
	@cat LICENSE

venv:
	$(PYTHON) -m venv venv

requirements:
	$(VENV) -m pip install -r requirements.txt

clean:
	rm -rf venv/ src/__pycache__ src/cogs/__pycache__ src/.env src/static-config.json
	-rm /etc/systemd/system/devbot.service
	-git pull