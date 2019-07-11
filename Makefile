.PHONY : dep lint test integration coverage run

IMAGE_NAME := ccextender
DIR := $(shell pwd -L)
VERSION := $(shell cat version)
GOPATH := ${GOPATH}
ifeq ($(GOPATH),)
	GOPATH := ${HOME}/go
endif
PROJECT_PATH := $(subst $(GOPATH)/src/,,$(DIR))
REGISTRY := registry.hub.docker.com
REGISTRY_USER := $(shell whoami)
REGISTRY_PWD := ""
IMAGE_PATH := /asecurityteam
ARTIFACT := $(REGISTRY)$(IMAGE_PATH)/$(IMAGE_NAME)



dep:
	docker run -ti \
        --mount src="$(DIR)",target="/go/src/$(PROJECT_PATH)",type="bind" \
        -w "/go/src/$(PROJECT_PATH)" \
        registry.hub.docker.com/asecurityteam/sdcli:v2 python dep
lint:
	docker run -ti \
        --mount src="$(DIR)",target="/go/src/$(PROJECT_PATH)",type="bind" \
        -w "/go/src/$(PROJECT_PATH)" \
        registry.hub.docker.com/asecurityteam/sdcli:v2 python lint

test:
	docker run -ti \
        --mount src="$(DIR)",target="/go/src/$(PROJECT_PATH)",type="bind" \
        -w "/go/src/$(PROJECT_PATH)" \
        registry.hub.docker.com/asecurityteam/sdcli:v2 python test

integration: ;

coverage:
	docker run -ti \
        --mount src="$(DIR)",target="/go/src/$(PROJECT_PATH)",type="bind" \
        -w "/go/src/$(PROJECT_PATH)" \
        registry.hub.docker.com/asecurityteam/sdcli:v2 python coverage

doc: ;

docker-login: ;

build:
	docker build -t $(ARTIFACT):$(VERSION) .

run:
	docker run -v $(DIR):/go/src/$(DIR) -ti $(ARTIFACT):$(VERSION)

deploy: build
	docker login -u=$(REGISTRY_USER) $(REGISTRY)
	docker push $(ARTIFACT):$(VERSION)
	docker tag $(ARTIFACT):$(VERSION) $(ARTIFACT):latest
	docker push $(ARTIFACT):latest

clean:
	rm -rf my-new-oss-service
	rm -f CCExtender/*.pyc
	rm -f tests/*.pyc
	rm -Rf .pycoverage/


