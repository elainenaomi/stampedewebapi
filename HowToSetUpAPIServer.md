Set up netlogger web API server

# On Linux server #

### Install Python 2.6 ( required by Mongo db) ###
```
./configure --enable-shared
make
make install
```

### Install Apache HTTP Server ###
```
sudo yum -y install httpd
```
test:
```
sudo /etc/init.d/httpd start
```

### Install mod\_wsgi (WSGI interface for python web applications in Apache) ###
```
wget http://code.google.com/p/modwsgi/downloads/detail?name=mod_wsgi-3.2.tar.gz&can=2&q=
tar -zxvf mod_wsgi-3.2.tar.gz

## make sure that we have python 2.6 configuration in /etc/ld.so.conf.d/ and run
	sudo /sbin/ldconfig

./configure
make
sudo make install
```

> Config follow [How to setup Apache Mod Wsgi](http://code.google.com/p/stampedewebapi/wiki/HowToSetUpApacheModWsgi)  on Linux server use **httpd** instead of **apache2**
### Install Mongo DB ###
```
	sudo yum install mongo-server mongo          
```
test/basic command:
```
## start mongo server in background
	sudo mongod &                 
## open mongo command line tool  
	mongo
```
### Install mySQL DB ###
```
sudo yum install mysql mysql-server     

## required python mysql driver and sqlAlchemy
	sudo yum install mysql-devel.x86_64

## install mysql driver for python
	wget http://sourceforge.net/projects/mysql-python/files/mysql-python-test/1.2.3c1/MySQL-python-1.2.3c1.tar.gz/download
	tar -xvf MySQL-python-1.2.3c1
	cd MySQL-python-1.2.3c1
	python setup.py build
	sudo python setup.py install

## install SQL Alchemy
	wget http://prdownloads.sourceforge.net/sqlalchemy/SQLAlchemy-0.6.0.tar.gz?download
	tar -xvf SQLAlchemy-0.6.0.tar.gz 
	cd SQLAlchemy-0.6.0
	python setup.py build
	sudo python setup.py install

```
test/basic command:
```
## start mysql server
/sbin/service mysqld start 
## stop                 
/sbin/service mysqld stop                  
## default username 'root' password ''            
mysql -u root -p
```



### Install svn, netlogger,stampedeWebAPI ###
```
yum -y install subversion
sudo svn co https://www.cs.usfca.edu/svn/netlogger /var/local/netloggerAPI
sudo svn co https://bosshog.lbl.gov/repos/netlogger/trunk /var/local/netlogger
sudo ln -s /var/local/netloggerAPI/ /var/www/netloggerAPI
sudo mkdir /var/www/egg/
sudo chown apache:apache /var/www/egg/

```
### Install easy\_install ( python setup tools) ###
```
sudo yum install python-setuptools
sudo easy_install pymongo
```