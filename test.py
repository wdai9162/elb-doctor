import os
import json
import boto3
import botocore
from botocore.config import Config
import time

print (int(time.time()*1000))


config = Config(
    region_name = 'ap-southeast-2',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

log_client = boto3.client('logs', config=config)

try: 
    put_log_events_response = log_client.put_log_events(
        logGroupName='elb-hc-logs-onos-pub-vpc0-syd-alb-0',
        logStreamName='elb-hc-tg-##ecs-dev-te-wiki-tool-fe##onos-alb-0-instance-tg-0',
        logEvents=[
            {
                'timestamp': 1671942785001, #response['ResponseMetadata'].HTTPHeaders.date,
                'message': 'testtesttest'
            }
        ],
        # sequenceToken='49636121214446068567953005218702894214095039209494545074'
    )
    print(put_log_events_response)
except botocore.exceptions.ClientError as error: 
    print("an error happened")
    print(error)

# print(put_log_events_response)


# if(put_log_events_response['ResponseMetadata']['HTTPStatusCode'] == 200): 
#     put_token = ssm.put_parameter(
#         Name=os.environ['SequenceTokenParameter'],
#         Value=put_log_events_response['nextSequenceToken'],
#         Overwrite=True
# )


    

#     print(response)
    
# def log_constructor(): 
    
#     time 
#     target 
#     port
#     health status 
#     failure reason 
#     json 
    

# def log_publisher(): 
    
    