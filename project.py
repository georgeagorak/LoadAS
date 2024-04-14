import logging
logger = logging.getLogger(__name__)
import subprocess
import re
import os
import sys

class User_App:
    def __init__(self, PID, x_offset, y_offset, width, height,title):
        self.PID = int(PID)
        self.x_offset = int(x_offset)
        self.y_offset = int(y_offset)
        self.width = int(width)
        self.height = int(height)
        self.title = title

    def __str__(self):
        return f"PID: {self.PID}, x_offset: {self.x_offset},y_offset: {self.y_offset},width: {self.width},height: {self.height}"
    
    @property
    def PID(self):
        return self._PID
    @PID.setter
    def PID(self,PID):
        try:
            int(PID)
        except TypeError:
            raise TypeError("PID must be integer string or integer")
        self._PID = PID

    @property
    def x_offset(self):
        return self._x_offset
    @x_offset.setter
    def x_offset(self,x_offset):
        try:
            int(x_offset)
        except TypeError:
            raise TypeError("PID must be integer string or integer")
        self._x_offset = x_offset

    @property
    def y_offset(self):
        return self._y_offset
    @y_offset.setter
    def y_offset(self,y_offset):
        try:
            int(y_offset)
        except TypeError:
            raise TypeError("PID must be integer string or integer")
        self._y_offset = y_offset

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self,width):
        try:
            int(width)
        except TypeError:
            raise TypeError("PID must be integer string or integer")
        self._width = width

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self,height):
        try:
            int(height)
        except TypeError:
            raise TypeError("PID must be integer string or integer")
        self._height = height
        
    @property
    def title(self):
        return self._title
    @title.setter
    def title(self,title):
        self._title = title



def main():
    logging.basicConfig(filename="myapp.log", level=logging.INFO)
    logger.info("START")

    #Check for os platform...
    if sys.platform.startswith("linux"):
            print("Beware, open flatpack software going to be ignored and it won't included session file. (it won't loaded or open!)")
            app_list = get_active_apps_info()
            save_apps_2_setup_file(app_list)
    elif sys.platform.startswith("win32"):
        print("Windows is not yet supported!")
    elif sys.platform.startswith("darwin"):
        print("macOS is not yet supported!")

    logger.info("END")

def get_active_apps_info():
    #run the capture command:  wmctrl -l -G
    #os.system("wmctrl -l -p -G > apps_info_temp.txt")
    subprocess.run("wmctrl -l -p -G > apps_info_temp.txt",shell=True) #? what if the wmctrl not install??
    logger.info("ran wmctrl cmd and created apps_info_temp.txt")

    # read line by line the output of the capture command
    app_list = []
    with open("apps_info_temp.txt", 'r') as file:
        logger.info("opened apps_info_temp.txt")
        for line in file:
            app = generate_app_info(line)
            logger.info(app)
            app_list.append(app)

    #return the relevent captured data (dic or list)
    logger.info(app_list)
    return app_list

def generate_app_info(s):
    if info := re.match(r"^(0x[0-9A-Fa-f]{8})\s{1,2}(-\d|\d)\s(\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{3,4})\s{1,4}(\d{3,4})\s{1,4}([A-Za-z0-9-]{1,})\s(.{1,})$",s):
    # created with help of: https://regex101.com/r/Op2GDF/1
        # capture relevent information (dic or list) - re
        logger.info("pattern matched in apps_info_temp.txt")
        temp_user_App = User_App(info.group(3),info.group(4),info.group(5),info.group(6),info.group(7),info.group(9))
    else:
        raise LookupError("str does not match rexp:\n\n" + str + "should match regular expression:\n\n ^(0x[0-9A-Fa-f]{8})\s{1,2}(-\d|\d)\s(\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{3,4})\s{1,4}(\d{3,4})\s{1,4}([A-Za-z0-9-]{1,})\s(.{1,})$")
    return temp_user_App

def save_apps_2_setup_file(list,filename="session"):
        with open(f"{filename}.sup", "w") as file: # .sup - (short for save user programs) plain text format containing commands of apps to load by LoadAS. This file/s with .sup format is/are produced by the user.
            for app in list:
                run_command = subprocess.check_output(f"ps -p {app['PID']} -o cmd=",shell=True,text=True)
                logger.info(f"The PID:{app['PID']}, is {run_command} command")
                file.write(f"{processed_run_command(run_command)}")
    with open(f"{filename}.sup", "w") as file: # .sup - (short for save user programs) plain text format containing commands of apps to load by LoadAS. This file/s with .sup format is/are produced by the user.
        for app in list:
            try:
                run_command = subprocess.check_output(f"ps -p {app.PID} -o cmd=",shell=True,text=True)
                logger.info(f"The PID:{app.PID}, is {run_command} command")
                file.write(f"{processed_run_command(run_command)}")
            except subprocess.CalledProcessError:
                print(f"Flatpak applications are not supported, {app.title} won't be added to a session file (won't be ran/loaded)")

def processed_run_command(cmd_path):
    if "gjs" not in cmd_path: #avoids gnome-shell 
        cmd_path = os.path.basename(cmd_path)
        if "gnome-terminal" in cmd_path:
            cmd_path = cmd_path.removesuffix('-server\n') + '\n' # if gnome terminal is open!
        return cmd_path
    return '' #give empty string to write()

if __name__ == "__main__":
    main()