from fabric.api import *
from configparser import ConfigParser
from aliyun import AliHelper
import time
import requests

class DeployServce:
    def __init__(self,war_file_path,target_tmp_path,tomcat_path,service_port,service_name,slb_id,health,alihelper):
        self.wpath = war_file_path.rstrip('/')
        self.wfile = self.wpath[self.wpath.rfind('/')+1:]
        self.ttpath = target_tmp_path.rstrip('/')+'/'
        self.tomcatpath = tomcat_path.rstrip('/')+'/'
        self.tpath = tomcat_path.rstrip('/')+'/webapps/'
        self.sport = service_port
        self.sname = service_name
        self.slb_id = slb_id
        self.health = health
        self.alihelper = alihelper
        self.hostDict = {}

    def get_hosts(self,instanceDict,slbDict):
        innerHosts = []
        pubHosts = []
        regionId,serverIds = self.alihelper.get_backend_servers_from_dict(slbDict,self.slb_id)
        for serverId in serverIds:
            iHost,pHost = self.alihelper.get_server_ip_from_dict(instanceDict,serverId)
            innerHosts.append(iHost)
            pubHosts.append(pHost)
            self.hostDict[pHost] = serverId

        self.regionId = regionId
        self.serverId = serverId
        return pubHosts

    def set_host_weight(self,host,weight):
#        print(self.regionId)
#        print(self.slb_id)
#        print(self.serverId[index])
#        print(weight)
        self.alihelper.set_backend_server('slb.aliyuncs.com','2014-05-15',self.regionId,self.slb_id,self.hostDict[host],weight)

    def mkdir_remote(self):
        sudo('mkdir -p '+self.ttpath)
        sudo('mkdir -p /home/bak/'+self.sname)

    def upload_file(self):
        put('./shutdown_tomcat.sh',self.ttpath+'shutdown_tomcat.sh',use_sudo=True)
        put(self.wpath,self.ttpath+self.wfile,use_sudo=True)

    def shutdown_tomcat(self):
        sudo('bash '+self.ttpath+'shutdown_tomcat.sh '+self.sport+' '+self.tomcatpath)

    def copy_war(self):
        tswfile =self.wfile+'.'+repr(time.time())
        sudo('mv '+self.tpath+self.wfile+' /home/bak/'+self.sname+'/'+tswfile)
        sudo('cp '+self.ttpath+self.wfile+' '+self.tpath)
        sudo('rm -rf '+self.tpath+self.wfile.rstrip('.war'))

    def start_tomcat(self):
        sudo('set -m;bash '+self.tomcatpath+'bin/startup.sh &')

    def test_tomcat(self,host,trytimes): 
        health_page = 'http://'+host+':'+self.sport+self.health
        try_times = trytimes
        i = 1
        while i <= try_times:
            i = i+1
            time.sleep(5)
            print(health_page)
            res = requests.get(health_page)
 #           print('we now get the status')
            if res.status_code == 200:
                print('service started!')
                break
        else:
            print('can not access the service!!!')
#        run('curl -v localhost:'+self.sport)


class DeployServices:
    def __init__(self,config,alihelper):
        parser =ConfigParser()
        parser.read(config)
        sections = parser.sections()
        self.servicesDict = {}
        for section in sections:
            wpath = parser.get(section,'war_file_path')
            ttpath = parser.get(section,'target_tmp_path')
            tomcatpath = parser.get(section,'tomcat_path')
            sport = parser.get(section,'service_port')
            sname = parser.get(section,'service_name')
            slbid = parser.get(section,'slb_id')
            health = parser.get(section,'health')
            ds = DeployServce(wpath,ttpath,tomcatpath,sport,sname,slbid,health,alihelper)
            self.servicesDict[section] = ds
        
    def get_services(self,*service_names):
        services = []
        for sname in service_names:
            if sname in self.servicesDict:
                services.append(self.servicesDict[sname])
            else:
                print('unknown service name '+sname)
        return services

    
        
