from typing import Dict
import boto3

def getElbs() -> Dict:
    """Retrieves all elastic load balancers in the account"""

    client = boto3.client('elbv2')
    response = client.describe_load_balancers()

    return response