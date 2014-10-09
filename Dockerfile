FROM        centos/base
RUN         yum install -y openssh-server
ADD         supervisord.conf /etc/supervisord.conf
EXPOSE      22
USER	    root 
CMD         ["/usr/bin/supervisord"]
