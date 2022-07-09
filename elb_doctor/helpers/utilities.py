import sys
import time 

class output_renderer:

    # HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    # def __init__(self,answers,outputs,HealthyHostCount,UnHealthyHostCount):
        
    #     self.answers=answers
    #     self.outputs=outputs 
    #     self.HealthyHostCount=HealthyHostCount
    #     self.UnHealthyHostCount=UnHealthyHostCount

    def color_ok_blue(self,string):
        return self.OKBLUE+string+self.ENDC

    def color_ok_green(self,string):
        return self.OKGREEN+string+self.ENDC

    def color_fail_red(self,string):
        return self.FAIL+string+self.ENDC

    def color_warn_yellow(self,string):
        return self.WARNING+string+self.ENDC

    def font_header_bold(self,string):
        return self.BOLD+string+self.ENDC

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


    def healthbar(self, it, stopper, prefix="",size=60, out=sys.stdout): # Python3.3+
        count = len(it)

        if count==0: 
            print(self.color_fail_red("There is no target registered!"))
            return 
            
        def show(j):
            x = int(size*j/count)    #needs to catch target=0 => division by Zero error
            print("{}[{}{}] {}/{}".format(prefix, u"█"*x, "."*(size-x), j, count), 
                    end='\r', file=out, flush=True)
        show(0)
        for i, item in enumerate(it):
            yield item
            if i<stopper:
                show(i+1)
            else: break
        # print("\n", flush=True, file=out)
        print(flush=True, file=out)


    # def link(uri, label=None):
    #     if label is None: 
    #         label = uri
    #     parameters = ''

    #     # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST 
    #     escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    #     return escape_mask.format(parameters, uri, label)

    def output_v1(self,outputs,HealthyHostCount,UnHealthyHostCount):

        for i in self.healthbar(range(len(outputs["InstanceStates"])),HealthyHostCount, "  Healthy Targets: ", 100):
            time.sleep(0.03)

        print(self.FAIL)
        for i in self.healthbar(range(len(outputs["InstanceStates"])),UnHealthyHostCount, "Unhealthy Targets: ", 100):
            time.sleep(0.03)
        print(self.ENDC)

        row_format ="{:<30}{:<35}{:<20}{:<40}"
        print(row_format.format('Target:Port','HealthState','Reason','Description'))
        print(row_format.format("------------------------------","---------------------------------------------","--------------------","--------------------"))
        for i in outputs["InstanceStates"]:
            if i["State"] == "OutOfService":
                print(row_format.format(i["InstanceId"],self.color_fail_red(i["State"]),i["ReasonCode"],i["Description"]))
            else: 
                print(row_format.format(i["InstanceId"],self.color_ok_green(i["State"]),i["ReasonCode"],i["Description"]))  

    def output_v2(self,answers,outputs,HealthyHostCount,UnHealthyHostCount):

        #calculate column width 
        #build bar 
        #build table header 
        #build table rows
        #build matcher

        for i in self.healthbar(range(len(outputs["TargetHealthDescriptions"])),HealthyHostCount, "  Healthy Targets: ", 100):
            time.sleep(0.03) # any code you need

        print(self.FAIL)
        for i in self.healthbar(range(len(outputs["TargetHealthDescriptions"])),UnHealthyHostCount, "Unhealthy Targets: ", 100):
            time.sleep(0.03) # any code you need
        print(self.ENDC)

        # print(outputs)
        row_format ="{:<40}{:<40}{:<100}"
        print(row_format.format('\033[1mTarget:Port\033[0m','\033[01mHealth Status\033[0m','\033[01mFailure Reason\033[0m'))
        print(row_format.format("----------------------------------------","--------------------------------------------------","----------","----------"))
        for i in outputs["TargetHealthDescriptions"]:

            target_port = "\033[0m"+i["Target"]["Id"]+":"+str(i["Target"]["Port"])+"\033[0m"

            if i["TargetHealth"]["State"] == "healthy":

                print(row_format.format(target_port, self.color_ok_green((i["TargetHealth"]["State"])), ""))

            elif i["TargetHealth"]["Reason"] == "Target.FailedHealthChecks":

                print(row_format.format(target_port, self.color_fail_red(i["TargetHealth"]["State"]), "Failed to establish TCP connection with the target, or the target response was malformed."))

            elif i["TargetHealth"]["Reason"] == "Target.ResponseCodeMismatch":

                print(row_format.format(target_port, self.color_fail_red(i["TargetHealth"]["State"]), "This target responded with HTTP code {0} while the configured Success Codes is {1}".format(self.color_fail_red(i["TargetHealth"]["Description"][-5:]),self.color_ok_green("["+answers["tg"]["success_codes"]+"]"))))

            elif i["TargetHealth"]["Reason"] == "Target.Timeout":

                print(row_format.format(target_port, self.color_fail_red(i["TargetHealth"]["State"]), "This target did not respond within the configured Health Check timeout of "+self.color_ok_green("["+str(answers["tg"]["hc_timeout"])+"]")+" seconds"))

            elif i["TargetHealth"]["Reason"] == "Elb.InternalError":

                print(row_format.format(target_port, self.color_fail_red(i["TargetHealth"]["State"]), i["TargetHealth"]["Reason"]+i["TargetHealth"]["Description"]+"FAILED to respond to Health Check within the allowed timeout"))
                
            else: 
                print(row_format.format(i["Target"]["Id"]+":"+str(i["Target"]["Port"]), self.color_fail_red(i["TargetHealth"]["State"]),i["TargetHealth"]["Reason"],i["TargetHealth"]["Description"]))