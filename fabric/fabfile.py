# -*- coding: utf-8 -*-
import os
from fabric.api import env, local, settings, abort, run, cd
from fabric.operations import local, put, sudo, get
from fabric.context_managers import prefix

env.appname = 'lis-service'

env.user = ''
env.path = ''
env.rootpath = env.path + 'bireme/'
env.gitpath = env.path + 'git/'
env.virtualenv = env.path + 'env/'

def test():
    """Test server"""
    env.hosts = ['']

def stage():
    """Stage server"""
    env.hosts = ['']

def production():
    """Main server"""
    env.hosts = ['']

# including local environment from fabric
try: 
    from environment import *
except: 
    pass


def requirements():
    """
        Install the requirements
    """
    with cd(env.gitpath):
        with prefix('. %s/bin/activate' % env.virtualenv):
            run('pip install -r requirements.txt')

def migrate():
    """
        Realiza migration local
    """    
    with cd(env.rootpath):
        with prefix('. %s/bin/activate' % env.virtualenv):
            run('python manage.py migrate')

def restart_app():
    """
        Restarts remote wsgi.
    """
    with cd(os.path.join(env.gitpath ,'fabric')):
        run("./restart.sh")

def update_version_file():
    with cd(env.rootpath):
        run("git describe --tags | cut -f 1,2 -d - > templates/version.txt")
        # traz o arquivo gerado da versão para minha máquina, e implementa a versão localmente
        get("templates/version.txt", "../bireme/templates")

def full_update():
    """
        Requirements, git pull, touch 
    """
    with cd(env.gitpath):
        run("git pull")

    requirements()
    migrate()
    update_version_file()
    restart_app()

def update():
    """
        Git pull e touch 
    """
    with cd(env.gitpath):
        run("git pull")

    update_version_file()
    restart_app()

