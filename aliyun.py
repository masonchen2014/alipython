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
        response = helper._get_all_responses(domain,version,'DescribeInstances',**params)
        insName = []
        innerIp = []
        pubIp = []
        regionId = []
        secGroupId = []
        for r in response:
 #           instances = json.loads(r)
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

    
    def get_security_groups(self,domain,version,action



helper = AliHelper('LTAI9XTbkEzHWkxY','DgnunLljMOPylukmteF2KXLATBG4rn')
shClient = helper.create_client('cn-shanghai')
hzClient = helper.create_client('cn-hangzhou')
#helper.get_instances_info('ecs.aliyuncs.com','2014-05-26','DescribeInstances',PageNumber = '1',PageSize = '10')
helper.get_instances_info('ecs.aliyuncs.com','2014-05-26',PageNumber = '1',PageSize = '30')
#request = helper._create_request('ecs.aliyuncs.com','2014-05-26','DescribeInstances',PageNumber = '1',PageSize = '20')
#hzRes = shClient.do_action_with_exception(request)
#print(hzRes)


#

#
#shRes = shClient.do_action_with_exception(request)
#print(shRes)
#print(shClient.get_region_id())
#request2 = helper.create_request('ecs.aliyuncs.com','2014-05-26','DescribeInstances',PageNumber = '1',PageSize = '100')
#hzRes = hzClient.do_action_with_exception(request2)
#print(hzRes)
#print(hzClient.get_region_id())

 #   print (obj['InnerIpAddress'])

#request2 = helper.create_request('ecs.aliyuncs.com','2014-05-26','DescribeInstances',PageNumber = '1',PageSize = '100')
#response2 = helper.get_response(request2)
#print(response)
#print(response2)


##获取ip地址
#requestIp = helper.create_request('ecs.aliyuncs.com','2014-05-26','DescribeNetworkInterfaces',PageNumber = '1',PageSize = '30')
#responseIp = helper.get_response(requestIp)
#print(responseIp)

##获取lsb地址，对应集群和监控端口
#requestLsb = helper.create_request('slb.aliyuncs.com','2014-05-15','DescribeLoadBalancers',PageNumber = '1',PageSize = '30')
#responseLsb = helper.get_response(requestLsb)
#print(responseLsb)

##获取安全组列表和内容、安全组和ECS实例对应的关系



