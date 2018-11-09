# We could use a smaller image, but this ensures that everything CircleCI needs
# is installed already.
FROM circleci/python:3.6
MAINTAINER Jeremy Low <jeremy@iseverythingstilltheworst.com>

# These are the version of python currently supported.
ENV SUPPORTED_VERSIONS="2.7.15 3.7.1 pypy-5.7.1 pypy3.5-6.0.0"
ENV PYENV_ROOT /home/circleci/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH

# Get and install pyenv.
RUN curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

# pyenv installer doesn't set these for us.
RUN echo "export PATH=${PYENV_ROOT}/bin:$$PATH \n\
eval '\$(pyenv init -)' \n\
eval '\$(pyenv virtualenv-init -)'" >> ~/.bashrc
RUN pyenv update

# Install each supported version into the container.
RUN for i in $SUPPORTED_VERSIONS; do pyenv install "$i"; done
