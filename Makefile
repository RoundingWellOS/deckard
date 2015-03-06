PYTHON  = `which python2.7`
PG_DUMP = `which pg_dump`
PSQL = `which psql`

DB_NAME = deckard
DB_USER = deckard

ENV_DIR = env

unexport VIRTUALENV

db:
	$(PSQL) -U $(DB_USER) $(DB_NAME)

rebuild-db:
	scripts/rebuild-db

init-db:
	scripts/init-db

drop-db:
	scripts/drop-db

run-http-server:
	$(PYTHON) deckard/http/app.py

run-queue:
	deckard_queue_manager

reqs:
	pip install -r requirements.txt

dev:
	$(PYTHON) setup.py develop

env:
	rm -rf $(ENV_DIR)
	virtualenv -p $(PYTHON) $(ENV_DIR)

.PHONY: test