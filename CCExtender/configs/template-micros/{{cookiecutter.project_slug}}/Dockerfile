ARG REGISTRY=docker.atl-paas.net
FROM $REGISTRY/sox/asecurityteam/golang:v1 as BUILDER
WORKDIR $GOPATH/src/bitbucket.org/{{cookiecutter.project_namespace}}/{{cookiecutter.project_name}}
COPY . .
EXPOSE 8081
