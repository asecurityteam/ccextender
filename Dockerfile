FROM python:3.6 AS BASE

RUN pip3 install -U setuptools cookiecutter
RUN pip3 install -U pylint
RUN pip install coverage
RUN pip install codecov
RUN pip3 install -U pytest
RUN pip3 install pytest-cov
RUN pip3 install oyaml

# COPY . /go/src/Users/aslape/python/src/github.com/CCExtender/

# WORKDIR /go/src/Users/aslape/python/src/github.com/CCExtender/

COPY . /go/src/ccextender/

WORKDIR /go/src/ccextender/

# Create a non-root user to avoid permissions issues when
# modifying files on the mounted host directories.
RUN mkdir -p /home/ccextender

RUN groupadd -r ccextender -g 1000 \
    && useradd --no-log-init -r -g ccextender -u 1000 ccextender \
    && chown -R ccextender:ccextender /opt \
    && chown -R ccextender:ccextender /go \
    && chown -R ccextender:ccextender /home/ccextender

#########################################

USER ccextender

CMD [ "python", "-m", "CCExtender.CCExtender"]