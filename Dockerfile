FROM        centos/base
RUN         yum install -y openssh-server
RUN         echo 'root:nmg1769815' |chpasswd
RUN         ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
RUN         ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key
ADD         supervisord.conf /etc/supervisord.conf
EXPOSE      22
USER	    root 
CMD         ["/usr/bin/supervisord"]
