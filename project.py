import logging
logger = logging.getLogger(__name__)
import subprocess
import re
import os


def main():
    logging.basicConfig(filename="myapp.log", level=logging.INFO)
    logger.info("START")

    app_list = get_active_apps_info()
    logger.info("END")

def get_active_apps_info():
    #run the capture command:  wmctrl -l -G
    #os.system("wmctrl -l -p -G > apps_info_temp.txt")
    subprocess.run("wmctrl -l -p -G > apps_info_temp.txt",shell=True) #? what if the wmctrl not install??
    logger.info("ran wmctrl cmd and created apps_info_temp.txt")

    # read line by line the output of the capture command
    apps_list = []
    with open("apps_info_temp.txt", 'r') as file:
        logger.info("opened apps_info_temp.txt")
        for line in file:
            apps_dict = generate_apps_list(line)
            apps_list.append(apps_dict)

    #return the relevent captured data (dic or list)
    logger.info(apps_list)
    return apps_list

def generate_apps_list(s):
    if info := re.match(r"^(0x[0-9A-Fa-f]{8})\s{1,2}(-\d|\d)\s(\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{3,4})\s{1,4}(\d{3,4})\s{1,4}([A-Za-z0-9-]{1,})\s(.{1,})$",s):
    # created with help of: https://regex101.com/r/Op2GDF/1
        # capture relevent information (dic or list) - re
        logger.info("pattern matched in apps_info_temp.txt")
        app_dict = {"window_id":info.group(1),
                        "desktop number ":info.group(2),
                        "PID":info.group(3),
                        "x-offset":info.group(4),
                        "y-offset":info.group(5),
                        "width":info.group(6),
                        "height":info.group(7),
                        "client-machine-name":info.group(8),
                        "window-title":info.group(9),}
    else:
        raise LookupError("str does not match rexp:\n\n" + str + "should match regular expression:\n\n ^(0x[0-9A-Fa-f]{8})\s{1,2}(-\d|\d)\s(\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{3,4})\s{1,4}(\d{3,4})\s{1,4}([A-Za-z0-9-]{1,})\s(.{1,})$")
    return app_dict
if __name__ == "__main__":
    main()