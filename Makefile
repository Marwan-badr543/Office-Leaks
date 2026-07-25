PYTHON      := python3
VENV        := venv
VENV_BIN    := $(VENV)/bin
PY          := $(VENV_BIN)/python
PIP         := $(VENV_BIN)/pip
BACKEND_DIR := office_leaks
FRONTEND_DIR := office_leaks_frontend
ENV_FILE    := $(BACKEND_DIR)/office_leaks/.env

EXTRA_DEPS  := djangorestframework-simplejwt redis huey google-genai standard-imghdr

.PHONY: help venv install-backend install-frontend install logs env \
	migrate makemigrations superuser redis backend frontend run shell \
	dbshell test clean freeze

help:
	@echo "targets:"
	@echo "  install         venv + backend deps + frontend deps"
	@echo "  install-backend venv + pip install (requirements + missing extras)"
	@echo "  install-frontend npm install"
	@echo "  logs            create office_leaks/logs (required by LOGGING config)"
	@echo "  env             create .env stub if missing"
	@echo "  migrate         apply migrations"
	@echo "  makemigrations  regenerate migrations from models"
	@echo "  superuser       create Django superuser"
	@echo "  redis           start local redis-server (background)"
	@echo "  backend         run Django dev server (:8000)"
	@echo "  frontend        run Vite dev server (:5173)"
	@echo "  run             run backend + huey + frontend together (run.py)"
	@echo "  shell           Django shell"
	@echo "  dbshell         Django dbshell"
	@echo "  test            run backend tests"
	@echo "  freeze          write current venv deps back to requirements.txt"
	@echo "  clean           remove venv, node_modules, db.sqlite3, logs"

$(VENV_BIN)/python:
	$(PYTHON) -m venv $(VENV)

venv: $(VENV_BIN)/python

install-backend: venv
	$(PIP) install -q --upgrade pip
	$(PIP) install -q -r requirements.txt
	$(PIP) install -q $(EXTRA_DEPS)

install-frontend:
	cd $(FRONTEND_DIR) && npm install

install: install-backend install-frontend logs env

logs:
	mkdir -p $(BACKEND_DIR)/logs

env:
	@test -f $(ENV_FILE) || printf 'SECRET_KEY=change-me\nREDIS_URL=redis://127.0.0.1:6379/0\n' > $(ENV_FILE)

migrate: logs env
	cd $(BACKEND_DIR) && ../$(PY) manage.py migrate

makemigrations: logs env
	cd $(BACKEND_DIR) && ../$(PY) manage.py makemigrations

superuser: logs env
	cd $(BACKEND_DIR) && ../$(PY) manage.py createsuperuser

redis:
	redis-cli ping >/dev/null 2>&1 || redis-server --daemonize yes

backend: logs env redis
	cd $(BACKEND_DIR) && ../$(PY) manage.py runserver 0.0.0.0:8000

frontend:
	cd $(FRONTEND_DIR) && npm run dev

run: logs env redis
	$(PY) run.py

shell: logs env
	cd $(BACKEND_DIR) && ../$(PY) manage.py shell

dbshell: logs env
	cd $(BACKEND_DIR) && ../$(PY) manage.py dbshell

test: logs env
	cd $(BACKEND_DIR) && ../$(PY) manage.py test

freeze:
	$(PIP) freeze > requirements.txt

clean:
	rm -rf $(VENV) $(FRONTEND_DIR)/node_modules $(BACKEND_DIR)/db.sqlite3 $(BACKEND_DIR)/logs
