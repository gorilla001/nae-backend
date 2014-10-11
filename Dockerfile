FROM        centos/base
RUN         yum install -y openssh-server
RUN         echo 'root:nmg1769815' |chpasswd
ADD         supervisord.conf /etc/supervisord.conf
EXPOSE      22
USER	    root 
CMD         ["/usr/bin/supervisord"]
