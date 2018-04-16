from fabric.api import *

env.hosts = ['114.55.235.185'] #,'121.199.4.107:2222']
env.user = 'chenmusheng'
env.sudo_password = '1qaz2wsx'
env.key_filename = '/home/mason/.ssh/id_rsa'


def mkdir_task():
    run('mkdir -p mason')

def upload_file():
    put('./shutdown_tomcat.sh','/home/chenmusheng/mason/shutdown_tomcat.sh')

def shutdown_tomcat():
    sudo('bash /home/chenmusheng/mason/shutdown_tomcat.sh')

def move_war_to_tomcat():
    run('')
   
def start_tomcat():
    sudo('set -m;bash /home/chenmusheng/apache-tomcat-8.5.6/bin/startup.sh &')

def test_tomcat(): 
    run('curl -v localhost:48009')

def deploy():
    mkdir_task()
    upload_file()
    shutdown_tomcat()
    start_tomcat()
    test_tomcat()
