from fabric.api import *
from aliyun import AliHelper
import deploy_service
import time

#Set fabric environments for access permission
env.user = 'chenmusheng'
env.sudo_password = '1qaz2wsx'
env.key_filename = '/home/mason/.ssh/id_rsa'


#Deploy specified service
def deploySingleService(ds):
    print('set '+env.host+' weight to 0')
    ds.set_host_weight(env.host,0)
    print('sleep 60 seconds...')
#    time.sleep(60)
    ds.mkdir_remote()
 #  ds.upload_file()
    ds.shutdown_tomcat()
    ds.copy_war()
    ds.start_tomcat()
    ds.test_tomcat(env.host,5)
    ds.set_host_weight(env.host,100)
    print('sleep 180 seconds...')
#    time.sleep(180)

#Deploy specified services
#usage : fab deploy:service_name1,service_name2
def deploy(*service_names):
    #Create AliHelper instance,get loadbalancers info and all instances info 
    helper = AliHelper('','')
    shClient = helper.create_client('cn-shanghai')
    hzClient = helper.create_client('cn-hangzhou')
    slbDict = helper.create_load_balancers_dict('slb.aliyuncs.com','2014-05-15')
    insDict = helper.get_instances_info('ecs.aliyuncs.com','2014-05-26',PageNumber = '1',PageSize = '100')

    dss = deploy_service.DeployServices('config.ini',helper)
    for service in dss.get_services(*service_names):
        host_list = service.get_hosts(insDict,slbDict)
        print(host_list)
        execute(deploySingleService,service,hosts=host_list)


#just for test
def deploy_test(*list):
    print(*list)
