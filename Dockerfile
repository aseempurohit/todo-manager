FROM ubuntu:14.04
MAINTAINER Manish "manish@aricent.com"
# ENV export http_proxy=$HTTP_PROXY
# ENV export https_proxy=$HTTPS_PROXY

RUN apt-get update

#RUN apt-get purge -y python-pip

RUN apt-get install -y python-pip

#RUN pip uninstall Flask
RUN pip install Flask

#RUN pip purge flask-restful
RUN pip install flask-restful

RUN apt-get install -y curl
ADD app-todomanager.py /app-todomanager.py

# ENV http_proxy "" 
# ENV https_proxy ""

CMD ["python", "app-todomanager.py","6000"]

RUN echo 'Our first Docker image for Microapp'
EXPOSE 80

