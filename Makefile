
.PHONY: black
black:
	@black -l 79 --check --diff .

.PHONY: flake8
flake8:
	@flake8

.PHONY: test
test:
	./scripts/test.sh

.PHONY: test-in-docker
test-in-docker:
	./scripts/test-in-docker.sh

.PHONY: test-in-docker-compose
test-in-docker-compose:
	./scripts/test-in-docker-compose.sh

.PHONY: tdd
tdd:
	./scripts/test-in-docker.sh ./scripts/test-tdd.sh
