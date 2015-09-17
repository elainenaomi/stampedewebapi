# On an Ubuntu machine #
  1. install apache2 and modwsgi
```
      sudo apt-get install apache2 libapache2-mod-wsgi
```

  1. create file /etc/apache2/conf.d/netlogger.conf and paste below:
```
       LoadModule wsgi_module modules/mod_wsgi.so

       WSGIScriptAlias / /var/www/netloggerAPI/dispatcher.py/
       WSGIPythonPath /var/www/netloggerAPI/
       WSGIPythonEggs /var/www/egg/
       WSGIRestrictStdout Off
       Alias /static /var/www/netloggerAPI/static/
       AddType text/html .py

      <Directory /var/www/netloggerAPI/>
          Order deny,allow
          Allow from all 
      </Directory>
```

  1. create symlink from /var/www/netloggerAPI to your code base. For example:
```
      ln -s /home/jecortez/NetloggerMongoFrontend/src/ netloggerAPI
```

  1. Make sure that the end of dispatcher.py in the code directory looks like this:
```
      #if __name__ == "__main__": app.run()
      application = web.application(urls, globals()).wsgifunc()
```

  1. restart apache
```
      sudo /etc/init.d/apache2 restart
```

  1. Done! Now do to your URL and enjoy!