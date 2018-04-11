from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
import pandas as pd

class AliHelper:    
    def __init__(self,access_key,access_key_secret):
        self._access_key = access_key
        self._access_key_secret = access_key_secret
        self._clients = []

    def create_client(self,region_id):
        client=AcsClient(self._access_key,self._access_key_secret,region_id)
        self._clients.append(client)
       # print(client.get_region_id())
        return client
        

    def _create_request(self,domain,version,action_name,**params):
        request = CommonRequest()
        request.set_domain(domain)
        request.set_version(version)
        request.set_action_name(action_name)
        for k,v in params.items():
            request.add_query_param(k,v)
        return request

    def _get_client_response(self,client,domain,version,action_name,**params):
     #   print(params)
        print('_get_client_response invocked !')
        request = self._create_request(domain,version,action_name,**params)
        res = client.do_action_with_exception(request)
      #  print(res)
        return json.loads(res)

    def _get_response(self,domain,version,action_name,**params):
        'get response for single page.'
        response = []
        for c in self._clients:
            print('Get response from region :',c.get_region_id())
            response.append(self._get_client_response(c,domain,version,action_name,**params))
        return response

    def _get_all_responses(self,domain,version,action_name,**params):
        'get response for all pages.'
        response = []
        pageSize = 100
       # if 'PageNumber' in params:
        #    pageNum = params['PageNumber']
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


    def get_instances_info(self,domain,version,**params):
        response = self._get_all_responses(domain,version,'DescribeInstances',**params)
        insName = []
        innerIp = []
        pubIp = []
        regionId = []
        secGroupId = []
        for r in response:
            iCount = 0
            for instance in r['Instances']['Instance']:
                iCount += 1
                insName.append(repr(instance['InstanceName']))
                innerIp.append(repr(instance['InnerIpAddress']['IpAddress']))
                pubIp.append(repr(instance['PublicIpAddress']['IpAddress']))
                regionId.append(repr(instance['RegionId']))
                secGroupId.append(repr(instance['SecurityGroupIds']['SecurityGroupId']))
            print('the nubmer of instance in obj is ',iCount)
        print('instances number is :',len(insName))
        dataFrame = pd.DataFrame({'InstanceName':insName,'InnerIp':innerIp,'PublicIp':pubIp,'RegionId':regionId,'SecGroupIds':secGroupId},columns=['InstanceName', 'InnerIp', 'PublicIp','RegionId','SecGroupIds'])
        dataFrame.to_csv("instances_info.csv",index=False,sep=',')
        print('write data into file instances_info.csv')

    
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






