FROM tensorflow/tensorflow:latest-gpu-py3
USER root
SHELL [ "/bin/bash", "-c" ]

RUN apt-get update
RUN apt-get install -y git

#RUN pip install --upgrade pip
RUN pip3 install sklearn keras sqlalchemy numpy kubernetes psycopg2-binary benedict flask-login 
RUN pip3 install gaugi saphyra


ENTRYPOINT ["entrypoint.sh"]






