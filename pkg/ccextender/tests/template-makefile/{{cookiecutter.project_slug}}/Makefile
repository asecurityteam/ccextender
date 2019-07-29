.PHONY : install-dep install-microscli dep lint test integration coverage doc docker-login build run deploy

DIR := $(shell pwd -L)
VERSION := $(shell date -u +%s)
GOPATH := ${GOPATH}
ifeq ($(GOPATH),)
	GOPATH := ${HOME}/go
endif
PROJECT_PATH := $(subst $(GOPATH)/src/,,$(DIR))

# Variables required for building and deploying internal Atlassian
# Docker images and Micros services
ENVIRON := dev
APP_IMAGE_NAME := sec-$(shell basename $(DIR))
{{cookiecutter.image_name}}
IMAGE_PATH := /atlassian/asecurityteam
ifeq ($(ENVIRON),prod)
IMAGE_PATH := /sox/asecurityteam
endif
REGISTRY := docker.atl-paas.net
REGISTRY_USER := $(shell whoami)
REGISTRY_PWD := ""
MICROS_PWD := ""
ARTIFACT := $(REGISTRY)$(IMAGE_PATH)/$(APP_IMAGE_NAME)
# Micros can't pull images from the Docker proxy registry, so image names
# must reference the internal registry name.
MICROS_HACK_ARTIFACT := docker.atl-paas.net$(IMAGE_PATH)/$(APP_IMAGE_NAME)
{{cookiecutter.hack_name}}

install-dep:
ifeq ($(shell command -v dep 2> /dev/null),)
	curl https://raw.githubusercontent.com/golang/dep/master/install.sh | sh
endif

install-micros-cli:
ifeq ($(shell command -v micros 2> /dev/null),)
	curl -O -H "Authorization:$(MICROS_PWD)" https://micros-proxy.services.atlassian.com/micros-stable/micros.tar.gz
	tar -xvf micros.tar.gz -C /usr/local/bin
	chmod +x /usr/local/bin/micros
endif

dep: install-dep
	# Currently there is no good way to in pull private dependencies into
	# the sdcli container at runtime that works on Linux, Mac, and in
	# Pipelines.
	dep ensure -v

lint: docker-login
	docker run --rm -v "$(DIR):/go/src/$(PROJECT_PATH)" \
        -w "/go/src/$(PROJECT_PATH)" \
        $(REGISTRY)/sox/asecurityteam/sec-sdcli:v1 go lint

test: docker-login
	docker run --rm -v "$(DIR):/go/src/$(PROJECT_PATH)" \
        -w "/go/src/$(PROJECT_PATH)" \
        $(REGISTRY)/sox/asecurityteam/sec-sdcli:v1 go test

integration: docker-login
	docker run --rm -v "$(DIR):/go/src/$(PROJECT_PATH)" \
        -w "/go/src/$(PROJECT_PATH)" \
        $(REGISTRY)/sox/asecurityteam/sec-sdcli:v1 go integration

coverage: docker-login
	# This fixes a permissions issue with the .coverage artifacts
	# in Pipelines where the directory and files are unwriteable.
	mkdir -p .coverage && chmod -R 777 .coverage
	docker run --rm -v "$(DIR):/go/src/$(PROJECT_PATH)" \
        -w "/go/src/$(PROJECT_PATH)" \
        $(REGISTRY)/sox/asecurityteam/sec-sdcli:v1 go coverage

doc: ;

docker-login:
ifeq ($(REGISTRY),docker-proxy.services.atlassian.com)
	docker login -u=$(REGISTRY_USER) -p=$(REGISTRY_PWD) $(REGISTRY)
endif

build: docker-login
	IMAGE=$(ARTIFACT) TAG=$(VERSION) REGISTRY=$(REGISTRY) docker-compose build

run:
	IMAGE=$(ARTIFACT) TAG=$(VERSION) REGISTRY=$(REGISTRY) docker-compose up --build --abort-on-container-exit

deploy: build install-micros-cli
	IMAGE=$(ARTIFACT) TAG=$(VERSION) REGISTRY=$(REGISTRY) docker-compose push

clean:
	rm -rf .builds/
ifeq ($(ENVIRON),prod)
	ARTIFACT_NAME=$(MICROS_HACK_ARTIFACT) \
	ARTIFACT_VERSION=$(VERSION) \
	{{cookiecutter.artifact_name}}
	micros service:deploy $(APP_IMAGE_NAME) -f $(APP_IMAGE_NAME).sd.yml --env=prod-west2 -v
else
	ARTIFACT_NAME=$(MICROS_HACK_ARTIFACT) \
	ARTIFACT_VERSION=$(VERSION) \
	{{cookiecutter.artifact_name}}
	micros service:deploy $(APP_IMAGE_NAME) -f $(APP_IMAGE_NAME).sd.yml --env=adev-west2 -v
endif
