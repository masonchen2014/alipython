from fabric.api import *

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

    def get_hosts(self):
        #return ['10.0.3.235:3721','114.55.235.185']
        return ['114.55.235.185']

    def mkdir_remote(self):
        sudo('mkdir -p '+self.ttpath)

    def upload_file(self):
        put('./shutdown_tomcat.sh',self.ttpath+'shutdown_tomcat.sh',use_sudo=True)
        put(self.wpath,self.ttpath+self.wfile,use_sudo=True)

    def shutdown_tomcat(self):
        sudo('bash '+self.ttpath+'shutdown_tomcat.sh '+self.sport+' '+self.tomcatpath)

    def copy_war(self):
        sudo('cp '+self.ttpath+self.wfile+' '+self.tpath)
        sudo('rm -rf '+self.tpath+self.wfile.rstrip('.war'))

    def start_tomcat(self):
        sudo('set -m;bash '+self.tomcatpath+'bin/startup.sh &')

    def test_tomcat(self): 
        run('curl -v localhost:'+self.sport)


