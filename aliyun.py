from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
import pandas as pd

class AliHelper:    
    def __init__(self,access_key,access_key_secret):
        self._access_key = access_key
        self._access_key_secret = access_key_secret
        self._clients = []

    # per region per client
    def create_client(self,region_id):
        client=AcsClient(self._access_key,self._access_key_secret,region_id)
        self._clients.append(client)
        return client
    
    # create aliyun API request
    def _create_request(self,domain,version,action_name,**params):
        request = CommonRequest()
        request.set_domain(domain)
        request.set_version(version)
        request.set_action_name(action_name)
        for k,v in params.items():
            request.add_query_param(k,v)
        return request

    # Send an aliyun API request from specified client,get the corresponding json object
    def _get_client_response(self,client,domain,version,action_name,**params):
        request = self._create_request(domain,version,action_name,**params)
        res = client.do_action_with_exception(request)
        return json.loads(res)

    # For every client,get results according to the params
    def _get_response(self,domain,version,action_name,**params):
        'get response for single page.'
        response = []
        for c in self._clients:
            print('Get response from region :',c.get_region_id())
            response.append(self._get_client_response(c,domain,version,action_name,**params))
        return response

    # For every client,get all the results
    def _get_all_responses(self,domain,version,action_name,**params):
        'get response for all pages.'
        response = []
        pageSize = 100

        if 'PageSize' in params:
            pageSize = int(params['PageSize'])

        print('Page size is ',pageSize)
        for c in self._clients:
            pageNum = 1
            print('Get all responses from region :',c.get_region_id())
            jsonObj = self._get_client_response(c,domain,version,action_name,PageNumber = repr(pageNum),PageSize = pageSize)
            response.append(jsonObj)
            total_count = jsonObj['TotalCount']
            print('total count is :',total_count)

            if total_count < pageSize:
                total_count = 0
            else:
                total_count -= pageSize
 
            while total_count > 0:
                pageNum += 1
                jsonObj = self._get_client_response(c,domain,version,action_name,PageNumber = repr(pageNum),PageSize = pageSize)
                total_count -=pageSize
                response.append(jsonObj)

            #print(res)
        print('response json obj number is ',len(response))
        return response


    # Get all the instance info that running on aliyun
    def get_instances_info(self,domain,version,**params):
        response = self._get_all_responses(domain,version,'DescribeInstances',**params)
        insName = []
        insId = []
        innerIp = []
        pubIp = []
        regionId = []
        secGroupId = []
        insDict = {}
        for r in response:
            iCount = 0
            for instance in r['Instances']['Instance']:
                iCount += 1
                insDict[instance['InstanceId']] = (instance['InnerIpAddress']['IpAddress'],instance['PublicIpAddress']['IpAddress'])
                insName.append(repr(instance['InstanceName']))
                insId.append(instance['InstanceId'])
                innerIp.append(repr(instance['InnerIpAddress']['IpAddress']))
                pubIp.append(repr(instance['PublicIpAddress']['IpAddress']))
                regionId.append(repr(instance['RegionId']))
                secGroupId.append(repr(instance['SecurityGroupIds']['SecurityGroupId']))
   #         print('the nubmer of instance in obj is ',iCount)
   #     print('instances number is :',len(insName))
  #      dataFrame = pd.DataFrame({'InstanceName':insName,'InstanceId':insId,'InnerIp':innerIp,'PublicIp':pubIp,'RegionId':regionId,'SecGroupIds':secGroupId},columns=['InstanceName','InstanceId','InnerIp', 'PublicIp','RegionId','SecGroupIds'])
   #     dataFrame.to_csv("instances_info.csv",index=False,sep=',')
  #      print('write data into file instances_info.csv')
        return insDict

    # Get an inner ip and a public ip for specified instance Id
    def get_server_ip_from_dict(self,instanceDict,instanceId):
        innerIp,pubIp= instanceDict[instanceId]
        iIp = ''
        pIp = ''
        if innerIp:
            iIp = innerIp[0]
        if pubIp:
            pIp = pubIp[0]
        return iIp,pIp

    # Get security groups info and write them into csv file
    def get_security_groups(self,domain,version,**params):
        response = self._get_all_responses(domain,version,'DescribeSecurityGroups',**params)
        groupId = []
        regionId = []
        description = []
        innerAccPolicy = []
        vpcId = []
        permission = []
        for r in response:
            for group in r['SecurityGroups']['SecurityGroup']:
                regionId.append(r['RegionId'])
                groupId.append(group['SecurityGroupId'])
                description.append(repr(group['Description']))

        groupRegion = list(zip(groupId,regionId))

        groupId2 = []
        regionId2 = []
        description2 = []
        innerAccPolicy2 = []
        vpcId2 = []

 #       print(len(groupRegion))
        for gId,rId in groupRegion:
            #print(gId,rId)
            for c in self._clients:
                if c.get_region_id() == rId :
                #    print(gId,rId)            
                    response = self._get_client_response(c,domain,version,'DescribeSecurityGroupAttribute',SecurityGroupId = gId)
               # else:
               #     print('else',rId,repr(c.get_region_id()))
               #     print(response)
                    for p in response['Permissions']['Permission']:
                        groupId2.append(response['SecurityGroupId'])
                        regionId2.append(response['RegionId'])
                        innerAccPolicy2.append(response['InnerAccessPolicy'])
                        vpcId2.append(response['VpcId'])
                        description2.append(response['Description'])
                        permission.append(p)
            
                
        dataFrame = pd.DataFrame({'SecurityGroupId':groupId2,'Description':description2,'RegionId':regionId2,'VpcId':vpcId2,'InnerAccessPolicy':innerAccPolicy2,'Permissons':permission},columns=['SecurityGroupId', 'Description','RegionId','VpcId','InnerAccessPolicy','Permissons'])
        dataFrame.to_csv("security_group_info.csv",index=False,sep=',')
        print('write data into file security_group_info.csv')

    # Get load balancers info and write them into csv file
    def get_load_balancers(self,domain,version,**params):
        response = self._get_all_responses(domain,version,'DescribeLoadBalancers',**params)
        lbId = []
        for r in response:
            for ld in r['LoadBalancers']['LoadBalancer']:
                lbId.append((ld['LoadBalancerId'],ld['RegionId']))

        loadBalancerId = []
        lbName = []
        address = []
        backends = []
        listenerPortsAndProtocol = []
        
        for l,rId in lbId:
            #print(gId,rId)
            for c in self._clients:
                if c.get_region_id() == rId :
                    response = self._get_client_response(c,domain,version,'DescribeLoadBalancerAttribute',LoadBalancerId = l)
                    loadBalancerId.append(response['LoadBalancerId'])
                    lbName.append(response['LoadBalancerName'])
                    address.append(response['Address'])
                    backends.append(repr(response['BackendServers']['BackendServer']))
                    listenerPortsAndProtocol.append(repr(response['ListenerPortsAndProtocol']['ListenerPortAndProtocol']))

        dataFrame = pd.DataFrame({'LoadBalancerId':loadBalancerId,'LoadBalancerName':lbName,'Address':address,'BackendServers':backends,'ListenerPortAndProtocol':listenerPortsAndProtocol},columns=['LoadBalancerId', 'LoadBalancerName','Address','BackendServers','ListenerPortAndProtocol'])
        dataFrame.to_csv("load_balancers_info.csv",index=False,sep=',')
        print('write data into file load_balancers_info.csv')

    # Create a dict that stores loadbalancerId、regionId and all its backend server ids
    def create_load_balancers_dict(self,domain,version,**params):
        response = self._get_all_responses(domain,version,'DescribeLoadBalancers',**params)
        lbId = []
        for r in response:
            for ld in r['LoadBalancers']['LoadBalancer']:
                lbId.append((ld['LoadBalancerId'],ld['RegionId']))

        lbBackendsDict = {}
        for l,rId in lbId:
            #print(gId,rId)
            for c in self._clients:
                if c.get_region_id() == rId :
                    response = self._get_client_response(c,domain,version,'DescribeLoadBalancerAttribute',LoadBalancerId = l)
                    backends = response['BackendServers']['BackendServer']
                    lbBackendsDict[l]=(rId,backends)

        return lbBackendsDict
        print(lbBackendsDict)

    #Get all the backend server ids of specfied loadbalancer 
    def get_backend_servers_from_dict(self,ldDict,lbId):
        if lbId in ldDict:
            regionId,backends = ldDict[lbId]
            serverId = []
            for server in backends:
                serverId.append(server['ServerId'])
         #   print(regionId,serverId)
            return regionId,serverId
        else:
            print('not in the dict')

    #Set weight of specified backend server 
    def set_backend_server(self,domain,version,regionId,lbId,serverId,weight):
        for c in self._clients:
            if c.get_region_id() == regionId :
                response = self._get_client_response(c,domain,version,'SetBackendServers',LoadBalancerId = lbId,BackendServers = [{"ServerId":serverId,"Weight":repr(weight)}])
                print(response)
                
        
        
