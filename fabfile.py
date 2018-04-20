from fabric.api import *
from aliyun import AliHelper
import deploy_service
import time


helper = AliHelper('LTAI9XTbkEzHWkxY','DgnunLljMOPylukmteF2KXLATBG4rn')
shClient = helper.create_client('cn-shanghai')
hzClient = helper.create_client('cn-hangzhou')
slbDict = helper.create_load_balancers_dict('slb.aliyuncs.com','2014-05-15')
insDict = helper.get_instances_info('ecs.aliyuncs.com','2014-05-26',PageNumber = '1',PageSize = '100')


#from aliyun import AliHelper

#helper = AliHelper('LTAI9XTbkEzHWkxY','DgnunLljMOPylukmteF2KXLATBG4rn')

#from deploy_service import DepolyServce


#ds = deploy_service.DeployServce('./war/ROOT.war','/home/chenmusheng/deploy','/home/chenmusheng/apache-tomcat-8.5.6','48009','service_name','slb_id',True)

#env.hosts = []#ds.get_hosts()
#print(env.hosts)
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

index = 0
def deploy3(ds,serviceId):
    global index
    print(serviceId[index])

#    ds.set_host_weight(index,100)
#    ds.print_attrs()
    if ds.valid == True:
        ds.set_host_weight(index,0)
        print('sleep 60 seconds...')
        time.sleep(60)
#        helper.set_backend_server('slb.aliyuncs.com','2014-05-15','cn-hangzhou','lb-bp1pejpw1dkcldz9z3npb','i-bp1i1e1nx6x2hzqce06n',100)
        ds.mkdir_remote()
 #       ds.upload_file()
        ds.shutdown_tomcat()
        ds.copy_war()
        ds.start_tomcat()
        ds.test_tomcat(index,5)
        ds.set_host_weight(index,100)
        print('sleep 180 seconds...')
        time.sleep(180)
    else:
        print('not valid service!')
    index =index +1

def deploy4():
    dss = deploy_service.DeployServices('config.ini')
    for service in dss.get_services():
        service.set_alihelper(helper)
        ihost_list,phost_list,serverId = service.get_hosts(insDict,slbDict)
        print(phost_list,serverId)
        execute(deploy3,service,serverId,hosts=phost_list)


#just for test
def deploy5(ds,serviceId):
    ds.test_tomcat(0,3)


