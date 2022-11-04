SHELL := /bin/bash
PWD := $(shell pwd)

default: build

docker-image:
	docker build -f ./client/Dockerfile -t "client:latest" .
	# Execute this command from time to time to clean up intermediate stages generated 
	# during client build (your hard drive will like this :) ). Don't left uncommented if you 
	# want to avoid rebuilding client image every time the docker-compose-up command 
	# is executed, even when client code has not changed
	# docker rmi `docker images --filter label=intermediateStageToBeDeleted=true -q`
.PHONY: docker-image

up: 
	docker-compose up --build
	make docker-compose-logs
.PHONY: docker-compose-up

nup: 
	docker compose up --build
	make docker-compose-nlogs
.PHONY: docker-compose-nup

down:
	docker-compose -f docker-compose.yaml stop -t 1
	docker-compose -f docker-compose.yaml down
.PHONY: docker-compose-down

ndown:
	docker compose -f docker-compose.yaml stop -t 1
	docker compose -f docker-compose.yaml down
.PHONY: docker-compose-ndown

logs:
	docker-compose logs -f
.PHONY: docker-compose-logs

nlogs:
	docker compose logs -f
.PHONY: docker-compose-nlogs