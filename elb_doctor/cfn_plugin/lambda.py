import os
import json
import boto3
from botocore.config import Config

def lambda_handler(event, context):
    
    config = Config(
        region_name = 'ap-southeast-2',
        signature_version = 'v4',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )
    
    elbv2 = boto3.client('elbv2',config=config)
    
    answers = {}
    tg_target_count = [] 
    
    answers['tg'] = json.loads(os.environ['Answers'])
    
    for i in answers['tg']['logging_tgs']:
        if 'response' not in locals(): 
            response = elbv2.describe_target_health(TargetGroupArn=i[0]['tg_arn'])
            tg_target_count.append(len(response['TargetHealthDescriptions']))
        #if there are multiple TGs or all TGs selected, keep appending the target health response
        else:
            temp = elbv2.describe_target_health(TargetGroupArn=i[0]['tg_arn'])
            tg_target_count.append(len(temp['TargetHealthDescriptions']))
            response['TargetHealthDescriptions'] = response['TargetHealthDescriptions']+temp['TargetHealthDescriptions']
    
    log_client = boto3.client('logs', config=config)
    
    # #probably not needed as log group/stream created by CFN 
    # response = log_client.describe_log_streams(
    #     logGroupName='elb-healthcheck-logging',
    #     logStreamNamePrefix='app/onos-pub-vpc0-syd-alb-0/bcf7ee7beb876c4f',
    #     limit=10
    # )
    
    ssm = boto3.client('ssm', config=config)
    sequenceToken = ssm.get_parameters(
        Names=[os.environ['SequenceTokenParameter']]
    )
    

    #probably not needed as this parameter is created by CFN 
    # if(sequenceToken):
    #     print(sequenceToken['Parameters'][0]['Value'])
    # else:
    #     print("sequenceToken doesn't exist")


    #probably no need this IF as the parameter is created by CFN
    if (response): 
        
        #construct log 
        put_log_events_response = log_client.put_log_events(
            logGroupName=os.environ['LogGroupName'],
            logStreamName=os.environ['LogStreamName'],
            logEvents=[
                {
                    'timestamp': 1672183694000, #response['ResponseMetadata'].HTTPHeaders.date,
                    'message': json.dumps(response)
                }
            ],
            # sequenceToken=sequenceToken['Parameters'][0]['Value']
            sequenceToken="123"
        )
        
        #except CloudWatchLogs.Client.exceptions.InvalidSequenceTokenException
        #except CloudWatchLogs.Client.exceptions.DataAlreadyAcceptedException
    
        if(put_log_events_response['ResponseMetadata']['HTTPStatusCode'] == 200): 
            put_token = ssm.put_parameter(
                Name=os.environ['SequenceTokenParameter'],
                Value=put_log_events_response['nextSequenceToken'],
                Overwrite=True
        )
        
        #except 
    
    
        print(put_log_events_response)
    else: 
        print("log group or log stream is not created")

#     print(response)
    
# def log_constructor(): 
    
#     time 
#     target 
#     port
#     health status 
#     failure reason 
#     json 
    

# def log_publisher(): 
    
    