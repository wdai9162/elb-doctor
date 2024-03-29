"""This is a parser that extracts the target group name and arn from each elb"""

from typing import Dict

def parseTgs(tg_response) -> Dict:
    """Take ELB response and filter out only NLBs"""

    all_tg = {}
    # TODO: Check if TG association exists, return Null name / no associated tg
    # for arn?
    try:
        for i in tg_response['TargetGroups']:
            all_tg[i['TargetGroupName']] = i['TargetGroupArn']
    except KeyError as error_no_tgs:
        # reraise the error
        raise error_no_tgs

    return all_tg
