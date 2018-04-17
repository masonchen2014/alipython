from fabric.api import *

import deploy_service
#from aliyun import AliHelper

#helper = AliHelper('LTAI9XTbkEzHWkxY','DgnunLljMOPylukmteF2KXLATBG4rn')

#from deploy_service import DepolyServce


ds = deploy_service.DeployServce('./war/ROOT.war','/home/chenmusheng/deploy','/home/chenmusheng/apache-tomcat-8.5.6','48009','service_name','slb_id',True)

env.hosts = ds.get_hosts()
print(env.hosts)
#env.hosts = ['10.0.3.235:3721']
#env.hosts = ['114.55.235.185'] #,'121.199.4.107:2222']
env.user = 'chenmusheng'
env.sudo_password = '1qaz2wsx'
env.key_filename = '/home/mason/.ssh/id_rsa'


def mkdir_task():
    run('mkdir -p mason')

def upload_file():
#    put('./shutdown_tomcat.sh','/home/chenmusheng/mason/shutdown_tomcat.sh')
    put('./shutdown_tomcat.sh','/home/chenmusheng/deploy/shutdown_tomcat.sh',use_sudo=True)


def shutdown_tomcat():
    sudo('bash /home/chenmusheng/mason/shutdown_tomcat.sh')

def move_war_to_tomcat():
    run('')
   
def start_tomcat():
    sudo('set -m;bash /home/chenmusheng/apache-tomcat-8.5.6/bin/startup.sh &')

def test_tomcat(): 
    run('curl -v localhost:8020')

def deploy():
    mkdir_task()
    upload_file()
    shutdown_tomcat()
    start_tomcat()
    test_tomcat()

def deploy2():
    ds.mkdir_remote()
    ds.upload_file()
    ds.shutdown_tomcat()
    ds.copy_war()
    ds.start_tomcat()
    ds.test_tomcat()
