from __future__ import print_function, unicode_literals
from elb_doctor.lib.elb.get_elbs import GetElbs
from elb_doctor.lib.elb.parse_elbs import ParseElbs
from elb_doctor.lib.tgs.getTargetHealth import getTargetHealth
from elb_doctor.lib.tgs.parseTgHealth import parseTgHealth
from elb_doctor.lib.helpers.utilities import output_renderer
from elb_doctor.lib.helpers.utilities import cloud_formation
from PyInquirer import prompt
from elb_doctor.lib.helpers.regions import standard_regions,other_regions
from elb_doctor.lib.helpers.elbtypes import elb_types
from elb_doctor.api.elb_doctor_api import ElbDoctorApi



def main():

    # get_elb = GetElbs()
    api = ElbDoctorApi()
    # parse_elbs = ParseElbs()

    questions = [
        {
        'type': 'list',
        'name': 'standard_regions',
        'message': 'What is the AWS region of your ELB?',
        'choices': standard_regions,
        'default': 'us-east-1'
        },
        {
        'type': 'list',
        'name': 'other_regions',
        'message': 'Is your ELB in any of the following Opt-in/GovCloud/China region?',
        'choices': other_regions,
        'when': lambda answers: answers['standard_regions'] == False
        },
        {
            'type': 'list',
            'name': 'elb_type',
            'message': 'What is the type of your ELB?',
            'choices': elb_types
        },
        {
            'type': 'list',
            'name': 'elb',
            'message': 'Which CLB are you having issue with?',
            'choices': api.retrieve_clbs,
            'when': lambda answers: answers['elb_type'] == 'classic'
        },
        {
            'type': 'list',
            'name': 'elb',
            'message': 'Which ALB are you having issue with?',
            'choices': api.retrieve_elbv2,                   #currently there is no better way to call parse_elbs.parse_albs, parse_elbs.parse_nlbs or parse_elbs.parse_gwlbs other than duplicating this question 3 times and use 'when' to control which one to display. get_elbv2 call will also be duplicated as well.
            'when': lambda answers: answers['elb_type'] == 'application'
        },
        {
            'type': 'list',
            'name': 'elb',
            'message': 'Which NLB are you having issue with?',
            'choices': api.retrieve_elbv2,                   #currently there is no better way to call parse_elbs.parse_albs, parse_elbs.parse_nlbs or parse_elbs.parse_gwlbs other than duplicating this question 3 times and use 'when' to control which one to display. get_elbv2 call will also be duplicated as well.
            'when': lambda answers: answers['elb_type'] == 'network'
        },
        {
            'type': 'list',
            'name': 'elb',
            'message': 'Which GWLB are you having issue with?',
            'choices': api.retrieve_elbv2,                   #currently there is no better way to call parse_elbs.parse_albs, parse_elbs.parse_nlbs or parse_elbs.parse_gwlbs other than duplicating this question 3 times and use 'when' to control which one to display. get_elbv2 call will also be duplicated as well.
            'when': lambda answers: answers['elb_type'] == 'gateway'
        },
        {
            'type': 'list',
            'name': 'tg',
            'message': 'Which TG/backend are you having issue with?',
            'choices': api.retrieve_target_groups,                                   #this is always invoked despite if the question is asked, causing problem when CLB is selected
            'when': lambda answers: answers['elb_type'] != 'classic'
        }
    ]
    
    answers = prompt(questions)
    print(answers)
    targets_health,tg_target_count = getTargetHealth(answers)
    healthy_host_count,unhealthy_host_count = parseTgHealth(answers,targets_health)  #consider to fetch from CW metrics, easier for AZ specific data
    
    print("\n")

    renderer = output_renderer()
    if answers['elb_type'] == 'classic':
        renderer.output_v1(targets_health,healthy_host_count,unhealthy_host_count)
    elif answers['elb_type'] != 'classic':
        renderer.output_v2(answers,targets_health,healthy_host_count,unhealthy_host_count,tg_target_count)

    questions2 = [
        {
        'type': 'list',
        'name': 'doctor_workflow',
        'message': 'Would you like to proceed with the below automated operations?',
        'choices': ['check_security_group', 'health_check_logging', 'create_dashboard', 'refresh_health_status'],
        'default': 'refresh_health_status'
        },
        {
        'type': 'checkbox',
        'name': 'logging_tgs',
        'message': 'Which target group would you like to log?',
        'choices':  api.retrieve_target_groups(answers),
        'when': lambda answers: answers['doctor_workflow'] == 'health_check_logging'
        },

    ]
    
    
    answers2 =  prompt(questions2)
    print(answers2)

    if(answers2['doctor_workflow']) == 'health_check_logging':

        #prepare stack parameters
        cfn_stack_name = "ElbDoctor-HealthCheck-Logging-" + answers['elb'].split('/')[-2]
        #check if stack exists(list-stacks) and perform update OR delete(list and describe tags) rollback stack

        #check if the same target group has been logged
        log_group_name = "elb-hc-logs-" + answers['elb'].split('/')[-2]

        #this is temp, consider to order and then hash
        tg_names = ''
        for i in answers2['logging_tgs']: 
            tg_names = tg_names + '##' + i[0]['tg_arn'].split('/')[-2]
        log_stream_name = "elb-hc-tg-" + tg_names 

        cloud_formation.launch_hc_logging(answers2, cfn_stack_name, log_group_name, log_stream_name)

if __name__ == "__main__":
    main()