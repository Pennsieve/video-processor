import boto3

ssm_values = [
    ('test-etl-storage-bucket', 'storage-bucket'),
    ('test-etl-upload-bucket',  'upload-bucket'),
]

def init_ssm(values=ssm_values):
    ''' initialize SSM with test values! '''
    for (key,value) in values:
        set_ssm_value(key, value)

def set_ssm_value(key, value, type='String'):
    '''
    Initalize SSM values for testing
    '''
    client = boto3.client('ssm', region_name='us-east-1')
    client.put_parameter(Name=key, Value=value, Type=type)
