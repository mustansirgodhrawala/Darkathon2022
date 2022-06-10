FROM ubuntu:latest
ARG keyword
ADD main.py .
RUN apt install python3 python3-pip -y
CMD ["python3","main.py","-k",keyword]
