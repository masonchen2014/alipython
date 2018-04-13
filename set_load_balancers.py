from aliyun import AliHelper

helper = AliHelper('','')
shClient = helper.create_client('cn-shanghai')
hzClient = helper.create_client('cn-hangzhou')
#for line in open("load_balancers.txt"):
 #   print(line)

bDict = helper.create_load_balancers_dict('slb.aliyuncs.com','2014-05-15')
#print(bDict)
rId,serverId = helper.get_backend_servers_from_dict(bDict,'lb-bp1pejpw1dkcldz9z3npb')
print(rId,serverId)
#helper.set_backend_servers('slb.aliyuncs.com','2014-05-15',bDict,'lb-bp1pejpw1dkcldz9z3npb',100)  
#helper.set_backend_server('slb.aliyuncs.com','2014-05-15','cn-hangzhou','lb-bp1pejpw1dkcldz9z3npb','i-bp1i1e1nx6x2hzqce06n',100)        


