# -*- coding: utf-8 -*-
import os
import sys
from fabric.api import env, local, settings, abort, run, cd, task
from fabric.operations import local, put, sudo, get
from fabric.context_managers import prefix

# Define common directories
GIT_DIR = '/git'
ROOT_DIR = '/bireme'
ENV_DIR = '/env'

# include stages servers information
try: 
    from environment import STAGES
except: 
    pass

# Function that load to env variable the settings from STAGES
def stage_set(stage_name='test'):
    env.stage = stage_name
    for option, value in STAGES[env.stage].items():
        setattr(env, option, value)

    if not 'git_path' in STAGES[env.stage]:
        env.git_path = env.path + GIT_DIR
    if not 'root_path' in STAGES[env.stage]:
        env.root_path = env.path + ROOT_DIR
    if not 'virtualenv' in STAGES[env.stage]:
        env.virtualenv = env.path + ENV_DIR

@task
def test():
    """
    set test server
    """
    stage_set('test')

@task
def production():
    """
    set production server
    """
    stage_set('production')


@task
def requirements():
    """
    install/update requirements
    """
    with cd(env.git_path):
        with prefix('. %s/bin/activate' % env.virtualenv):
            run('pip install -r requirements.txt')

@task
def migrate():
    """
    run manage.py migrate
    """    
    with cd(env.root_path):
        with prefix('. %s/bin/activate' % env.virtualenv):
            run('python manage.py migrate')

@task
def restart_app():
    """
    touch appliction.wsgi file (reload appliction)
    """
    with cd(os.path.join(env.git_path ,'fabric')):
        run("./restart.sh")

@task
def update_version_file():
    """
    update application version.txt based on git describe command
    """

    with cd(env.root_path):
        run("git describe --tags | cut -f 1,2 -d - > templates/version.txt")
        # traz o arquivo gerado da versão para minha máquina, e implementa a versão localmente
        get("templates/version.txt", "../bireme/templates")

@task
def full_update():
    """
    update requirements, execute git pull, touch application.wsgi
    """
    with cd(env.git_path):
        run("git pull")

    requirements()
    migrate()
    update_version_file()
    restart_app()

@task
def update():
    """
    execute git pull and restart application
    """
    with cd(env.git_path):
        run("git pull")

    update_version_file()
    restart_app()

