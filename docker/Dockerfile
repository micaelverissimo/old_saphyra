FROM tensorflow/tensorflow:latest-gpu-py3
USER root
SHELL [ "/bin/bash", "-c" ]

RUN apt-get update
RUN apt-get install -y git

RUN pip install --upgrade pip
RUN pip3 install sklearn keras sqlalchemy numpy kubernetes psycopg2-binary benedict flask-login 


# get the saphyra repository
RUN mkdir -p /code
RUN cd /code && git clone https://github.com/jodafons/saphyra.git && cd saphyra && \
ls  && bash setup_module.sh && bash setup_module.sh --head && git pull

COPY test-gpu.py /
COPY setup_envs.sh /
