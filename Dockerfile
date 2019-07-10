FROM python:3.6 AS BASE

# RUN pip3 install -U setuptools cookiecutter
# RUN pip3 install -U pylint
# RUN pip3 install coverage
# RUN pip3 install codecov
# RUN pip3 install -U pytest
# RUN pip3 install pytest-cov
# RUN pip3 install oyaml
# RUN export PIPENV_VENV_IN_PROJECT=1
# RUN export PATH="/home/ccextender/.local/share/virtualenvs/ccextender-eHKON4Y-"

# RUN export PIPENV_PIPFILE="/go/src/ccextender/Pipfile"

# RUN apt-get install bash

RUN pip install pipenv

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
    && chown -R ccextender:ccextender /home/ccextender \
    && chown -R ccextender:ccextender /usr/local/lib/python3.6/site-packages \
    && chown -R ccextender:ccextender /usr/local/bin

#########################################

# RUN pipenv shell

RUN pipenv install --system --deploy

USER ccextender

# RUN source /home/ccextender/.local/share/virtualenvs/ccextender-eHKON4Y-/bin/activate

# ENTRYPOINT [ "pipenv", "--three", "run", "python", "-m", "CCExtender.CCExtender"]

ENTRYPOINT [ "python", "-m", "pkg.ccextender.ccextender"]