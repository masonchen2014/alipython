from fabric.api import *
from configparser import ConfigParser
from aliyun import AliHelper
import time
import requests

class DeployServce:
    def __init__(self,war_file_path,target_tmp_path,tomcat_path,service_port,service_name,slb_id,valid):
        self.wpath = war_file_path.rstrip('/')
        self.wfile = self.wpath[self.wpath.rfind('/')+1:]
        self.ttpath = target_tmp_path.rstrip('/')+'/'
        self.tomcatpath = tomcat_path.rstrip('/')+'/'
        self.tpath = tomcat_path.rstrip('/')+'/webapps/'
        self.sport = service_port
        self.sname = service_name
        self.slb_id = slb_id
        self.valid = valid

    def print_attrs(self):
        print(self.wpath)
        print(self.wfile)
        print(self.ttpath)
        print(self.tomcatpath)
        print(self.tpath)
        print(self.sport)
        print(self.sname)
        print(self.slb_id)
        print(self.valid)

    def set_alihelper(self,alihelper):
        self.alihelper = alihelper

    def get_hosts(self,instanceDict,slbDict):
        innerHosts = []
        pubHosts = []
        regionId,serverId = self.alihelper.get_backend_servers_from_dict(slbDict,self.slb_id)
        for server in serverId:
            iHost,pHost = self.alihelper.get_server_ip_from_dict(instanceDict,server)
            innerHosts.append(iHost)
            pubHosts.append(pHost)
#        print(hosts)
        #return ['10.0.3.235:3721','114.55.235.185']
        self.regionId = regionId
        self.serverId = serverId
        self.hosts = pubHosts
        return innerHosts,pubHosts,serverId

    def set_host_weight(self,index,weight):
#        print(self.regionId)
#        print(self.slb_id)
#        print(self.serverId[index])
#        print(weight)
        self.alihelper.set_backend_server('slb.aliyuncs.com','2014-05-15',self.regionId,self.slb_id,self.serverId[index],weight)

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

    def test_tomcat(self,index,trytimes): 
#        run('curl -v http://localhost:7064/index.html')
        try_times = trytimes
        i = 1
        while i <= try_times:
            print('http://'+self.hosts[index]+':'+self.sport+'/index.html')
            time.sleep(5)
            res = requests.get('http://'+self.hosts[index]+':'+self.sport+'/index.html')
            if res.status_code == 200:
                print('service started!')
                break
        else:
            print('can not access the service!!!')
#        run('curl -v localhost:'+self.sport)


class DeployServices:
    def __init__(self,config):
        parser =ConfigParser()
        parser.read(config)
        sections = parser.sections()
        self.services = []
        for section in sections:
            wpath = parser.get(section,'war_file_path')
            ttpath = parser.get(section,'target_tmp_path')
            tomcatpath = parser.get(section,'tomcat_path')
            sport = parser.get(section,'service_port')
            sname = parser.get(section,'service_name')
            slbid = parser.get(section,'slb_id')
            valid = parser.getboolean(section,'valid')
            ds = DeployServce(wpath,ttpath,tomcatpath,sport,sname,slbid,valid)
            self.services.append(ds)
        
    def get_services(self):
        return self.services
        
