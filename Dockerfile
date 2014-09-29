FROM centos/base
RUN yum install -y httpd
EXPOSE 80
USER root
CMD httpd -DFOREGROUND
