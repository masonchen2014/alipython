from aliyun import AliHelper

helper = AliHelper('LTAI9XTbkEzHWkxY','DgnunLljMOPylukmteF2KXLATBG4rn')
shClient = helper.create_client('cn-shanghai')
hzClient = helper.create_client('cn-hangzhou')

helper.get_instances_info('ecs.aliyuncs.com','2014-05-26',PageNumber = '1',PageSize = '100')
helper.get_security_groups('ecs.aliyuncs.com','2014-05-26',PageNumber = '1',PageSize = '30')
helper.get_load_balancers('slb.aliyuncs.com','2014-05-15')
