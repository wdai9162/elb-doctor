#-- Import modules
import sys
import os.path
import json
import time
import boto3

 #-- Functions
def check_status( cfn_client_ss, cfn_stack_name_ss ):
    stacks_ss = cfn_client_ss.describe_stacks(StackName=cfn_stack_name_ss)["Stacks"]
    stack_ss_val = stacks_ss[0]
    status_cur_ss = stack_ss_val["StackStatus"]
    print ("Current status of stack " + stack_ss_val["StackName"] + ": " + status_cur_ss)
    for ln_loop in range(1, 9999):
        if "IN_PROGRESS" in status_cur_ss:
            print ("\rWaiting for status update(" + str(ln_loop) + ")...",)
            time.sleep(5) # pause 5 seconds

            try:
                stacks_ss = cfn_client_ss.describe_stacks(StackName=cfn_stack_name_ss)["Stacks"]
            except:
                print (" ")
                print ("Stack " + stack_ss_val["StackName"] + " no longer exists")
                status_cur_ss = "STACK_DELETED"
                break

            stack_ss_val = stacks_ss[0]

            if stack_ss_val["StackStatus"] != status_cur_ss:
                status_cur_ss = stack_ss_val["StackStatus"]
                print (" ")
                print ("Updated status of stack " + stack_ss_val["StackName"] + ": " + status_cur_ss)
        else:
            break

    return status_cur_ss
#-- End Functions

 #-- Main program
def main(access_key_ss, secret_key_ss, param_file_ss):

    #-- Confirm parameters file exists
    if os.path.isfile(param_file_ss):
        json_data_ss=open(param_file_ss).read()
    else:
        print ("Parameters file: " + param_file_ss + " is invalid!")
        print (" ")
        sys.exit(3)

    print ("Parameters file: " + param_file_ss)
    parameters_data_ss = json.loads(json_data_ss)
    region_ss = parameters_data_ss["RegionId"]

    #-- Connect to AWS region specified in parameters file
    print ("Connecting to region: " + region_ss)
    cfn_client_ss = boto3.client('cloudformation', region_ss, aws_access_key_id=access_key_ss, aws_secret_access_key=secret_key_ss)

    #-- Store parameters from file into local variables
    cfn_stack_name_ss = parameters_data_ss["StackName"]
    print ("You are deploying stack: " + cfn_stack_name_ss)
    #-- Check if this stack name already exists
    stack_list_ss = cfn_client_ss.describe_stacks()["Stacks"]
    stack_exists_ss = False
    for stack_ss_cf in stack_list_ss:
        if cfn_stack_name_ss == stack_ss_cf["StackName"]:
            print ("Stack " + cfn_stack_name_ss + " already exists.")
            stack_exists_ss = True

    #-- If the stack already exists then delete it first
    if stack_exists_ss:
        user_response = input ("Do you want to delete or update the stack")
        print ("Calling Delete Stack API for " + cfn_stack_name_ss)
        cfn_client_ss.delete_stack(StackName=cfn_stack_name_ss)

        #-- Check the status of the stack deletion
        check_status(cfn_client_ss, cfn_stack_name_ss)

    print (" ")
    print ("Loading parameters from parameters file:")
    fetch_stack_parameters_ss = []
    for key_ss in parameters_data_ss.keys():
        if key_ss == "TemplateUrl":
            template_url_ss = parameters_data_ss["TemplateUrl"]
        elif key_ss == "StackName" or key_ss == "RegionId":
            # -- Do not send as parameters
            print (key_ss + " - "+ parameters_data_ss[key_ss] + " (not sent as parameter)")
        else:
            print (key_ss + " - "+ parameters_data_ss[key_ss])
            fetch_stack_parameters_ss.append({"ParameterKey": key_ss, "ParameterValue": parameters_data_ss[key_ss]})

    #-- Call CloudFormation API to create the stack   TemplateBody='', 
    print (" ")
    print ("Calling CREATE_STACK method to create: " + cfn_stack_name_ss)

    status_cur_ss = ""

    result_ss = cfn_client_ss.create_stack(StackName=cfn_stack_name_ss, DisableRollback=True, TemplateURL=template_url_ss, Parameters=fetch_stack_parameters_ss, Capabilities=["CAPABILITY_NAMED_IAM"])
    print ("Output from API call: ")
    print (result_ss)
    print (" ")

    #-- Check the status of the stack creation
    status_cur_ss = check_status( cfn_client_ss, cfn_stack_name_ss )

    if status_cur_ss == "CREATE_COMPLETE":
        print ("Stack " + cfn_stack_name_ss + " created successfully.")
    else:
        print ("Failed to create stack " + cfn_stack_name_ss)
        sys.exit(1)

#-- Call Main program
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print ("%s:  Error: %s\n" % (sys.argv[0], "Not enough command options given"))
        print ("Argument 1 (required): AWS Access Key ")
        print ("Argument 2 (required): AWS Secret Access Key ")
        print ("Argument 3 (required): Stack Parameters JSON file ")
        print (" ")
        sys.exit(3)
    else:
        access_key_ss = sys.argv[1]
        secret_key_ss = sys.argv[2]
        param_file_ss = sys.argv[3]

main(access_key_ss, secret_key_ss, param_file_ss)