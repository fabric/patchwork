import time

from fabric.api import sudo
from fabric.contrib.files import upload_template


def supervise(conf, destination='/etc/supervisor/conf.d', **kwargs):
    """
    Installs a service into supervisor. ``kwargs`` are passed onto the upload_template call.
    """
    if 'use_sudo' not in kwargs:
        kwargs['use_sudo'] = True
    
    upload_template(conf, destination, **kwargs)

    sudo("service supervisor stop")
    time.sleep(2)
    sudo("service supervisor start")
    sudo("supervisorctl status")
