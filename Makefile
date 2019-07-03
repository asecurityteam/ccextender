.PHONY : dep lint test integration coverage run

IMAGE_NAME := ccextender
DIR := $(shell pwd -L)
VERSION := $(shell date -u +%s)
GOPATH := ${GOPATH}
ifeq ($(GOPATH),)
	GOPATH := ${HOME}/go
endif
PROJECT_PATH := $(subst $(GOPATH)/src/,,$(DIR))



dep: install-dep
	# Currently there is no good way to in pull private dependencies into
	# the sdcli container at runtime that works on Linux, Mac, and in
	# Pipelines.
	dep ensure -v

lint: pylint

test:
	docker run -ti \
        --mount src="$(DIR)",target="/go/src/$(PROJECT_PATH)",type="bind" \
        -w "/go/src/$(PROJECT_PATH)" \
        registry.hub.docker.com/asecurityteam/sdcli:v1 python test

integration: ;

coverage: pytest --cov=CCExtender tests/

doc: ;

docker-login: ;

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run -v $(DIR):/go/src/$(DIR) -ti $(IMAGE_NAME)

deploy: ;
clean: ;
