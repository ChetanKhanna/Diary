# PS-Diary
This is a project for an online weekly diary for Practice School.
## Installing the project
clone this repo into your system
```bash
git clone https://github.com/kestal-lab/PS2-Diary.git
```
## virtualenv
Activate virtualenv that comes with the project and install required dependencies
```bash
source myproject/bin/activate
pip install -r requirements.txt
```
Once all dependencies are installed, exit the virtualenv
```bash
deactivate
```

The programme uses supervisor and rabbitmq to run celery tasks. Please make sure
that those are installed.

## rabbitmq-server
```bash
yum -y install epel-release
yum -y update
yum -y install erlang socat

wget https://www.rabbitmq.com/releases/rabbitmq-server/v3.6.10/rabbitmq-server-3.6.10-1.el7.noarch.rpm
rpm --import https://www.rabbitmq.com/rabbitmq-release-signing-key.asc
rpm -Uvh rabbitmq-server-3.6.10-1.el7.noarch.rpm
```

## supervisor
supervisor is included in requirements.txt and will be installed along with other
python package from the virtualenv.

## configuring supervisor and PS2-celery
Once supervisor and rabbitmq are installed, copy paste the configuration files included in the pulled github repository to the following locations
supervisord.conf --> /etc/supervisord.conf
PS2-celery.conf --> /etc/supervisord.d/PS2-celery.conf

*PS2-celery.conf is not there by default and has to be created explicitly*

## starting services
Run the following commands in the *root shell*
```bash
systemctl start httpd
systemctl start mariadb.service
systemctl enable rabbitmq-server.service
systemctl start rabbitmq-server.service
systemctl enable supervisord
systemctl start supervisord
supervisorctl reread
supervisorctl update
```

## How to run
log into 127.0.0.1/PS2/ from your web-browser
