FI-ADMIN
=========

Administration interface and API for Information Sources

Los pasos abajo para la instalaci�n del FI-ADMIN fueron probados bajo servidor Linux con Debian GNU/Linux 8 pero si supone seren compatibles con la ultima versi�n 18.04 LTS de Ubuntu o otro sistema Linux actual

1 - Instalaci�n de los paquetes necesarios como root del servidor (python2.7 y apache2)
---------------------------------------------------------------------------------------

$ sudo apt-get install build-essential
$ sudo apt-get install python-dev libxml2-dev libxslt1-dev
$ sudo apt-get install python-virtualenv
$ sudo apt-get install python-mysqldb
$ sudo apt-get install python-pip
$ sudo apt-get install apache2 libapache2-mod-wsgi

2 - Creaci�n del ambiente de ejecuci�n del sistema (usuario normal del sistema)
-------------------------------------------------------------------------------

a. Crear estructura de directorio para el sistema (ej. **?/home/fi-admin/**)

**user@server:/home$** mkdir fi-admin

b. Hacer clone del repositorio de codigos FI-ADMIN del servicio GitHub:

**user@server:/home/fi-admin$** git clone ?https://github.com/bireme/fi-admin.git ? git

c. Hacer clone del reposit�rio de login BIREME Accounts

**user@server:/home/fi-admin$**? git clone ?https://github.com/bireme/biremelogin.git ? biremelogin

d. Instalaci�n de los paquetes necesarios del FI-ADMIN bajo virtualenv

**user@server:/home/fi-admin$** ?virtualenv env
**user@server:/home/fi-admin$** ?source env/bin/activate
**user@server:/home/fi-admin$** ?pip install -r git/requirements.txt
**user@server:/home/fi-admin$** ?pip install mimeparse
**user@server:/home/fi-admin$** ?pip install dateparser

e. Creaci�n de enlaces simb�licos

**user@server:/home/fi-admin$** ?ln -s git/bireme bireme
**user@server:/home/fi-admin$** ?cd git/bireme
**user@server:/home/fi-admin/git/bireme$** ?ln -s ../../biremelogin/biremelogin biremelogin
**user@server:/home/fi-admin/git/bireme$** ?cd static
**user@server:/home/fi-admin/git/bireme/static$** ?ln -s /home/fi-admin/env/lib/python2.7/site-packages/tinymce/static/django_tinymce/ django_tinymce
**user@server:/home/fi-admin/git/bireme/static$** ?ln -s /home/fi-admin/env/lib/python2.7/site-packages/django/contrib/admin/static/admin/ admin

3 - Archivo de configuraci�n WSGI
---------------------------------

a. Crear arquivo ?application.wsgi ?bajo el directorio inicial (ej. /home/fi-admin/) con la configuraci�n abajo:

import os, sys

PROJECT_NAME = 'fi-admin'
INSTALL_BASE = '/home/fi-admin/'

PROJECT_BASE = os.path.join(INSTALL_BASE, 'bireme')

sys.path.append(INSTALL_BASE)
sys.path.append(PROJECT_BASE)
sys.path.append(os.path.join(PROJECT_BASE, 'fi-admin'))

os.environ['DJANGO_SETTINGS_MODULE'] = PROJECT_NAME+'.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

4 - Configuraci�n del VirtualHost APACHE2
-----------------------------------------

[VirtualHost APACHE2](docs/fi-admin.sld.cu.conf)

5 - Configuraci�n del FI-ADMIN
------------------------------

La configuraci�n del FI-ADMIN (base de datos, etc) est�n ubicados en el archivo **?settings_local.py**:

a. Crear archivo de configuraci�n del sistema

**user@server:/home/fi-admin$** ?cd git/bireme/fi-admin/
**user@server:/home/fi-admin/git/bireme/fi-admin$** ?cp settings_local.py-SAMPLE settings_local.py

b. Configurar datos de acceso para la base de datos y otros ajustes necesarios.
