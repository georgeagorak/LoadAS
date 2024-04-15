import logging
logger = logging.getLogger(__name__)
import subprocess
import re
import os
import sys
import csv

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
            #load_app_session("session.sup")
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
    # TODO needs some further dev
    # saved_filename = os.path.basename(os.path.abspath(filename))
    # if saved_filename == filename:
    #     filename = append_file_name(filename)
    if not os.path.isdir("user_sessions/"):
        os.mkdir("user_sessions/")
    with open(f"user_sessions/{filename}.sup", "w") as file: # .sup - (short for save user programs) plain text format containing commands of apps to load by LoadAS. This file/s with .sup format is/are produced by the user.
        writer = csv.DictWriter(file,fieldnames=["command","x_offset","y_offset","width","height"])
        for app in list:
            try:
                run_command = subprocess.check_output(f"ps -p {app.PID} -o cmd=",shell=True,text=True)
                logger.info(f"The PID:{app.PID}, is {run_command} command")
                isValidCmd,run_command = processed_run_command(run_command)
                if isValidCmd:
                    writer.writerow({"command": f"{run_command.rstrip()}",
                                    "x_offset": app.x_offset,
                                    "y_offset": app.y_offset,
                                    "width": app.width,
                                    "height": app.height})
            except subprocess.CalledProcessError:
                print(f"Flatpak applications are not supported: '{app.title}' application won't be added to a session file (won't be ran/loaded)")

def processed_run_command(cmd_path):
    if "gjs" not in cmd_path: #avoids gnome-shell 
        cmd_path = os.path.basename(cmd_path)
        if "gnome-terminal" in cmd_path:
            cmd_path = cmd_path.removesuffix('-server\n') + '\n' # if gnome terminal is open!
        return [True,cmd_path]
    return [False,''] #give empty string to write()

def load_app_session(filename):
    session_files_storage = "user_sessions/"
    #initial checks
    if not os.path.isdir("user_sessions/"):
        raise NameError("There are no session files to load: user_sessions/ does not exits - fix: create a session file.")
    if not isSessionFile(session_files_storage):
        raise NameError("There are no session files to load: user_sessions/ does exits but no single .sep session file could be found (deleted manually?) - fix: create a session file.")
    
    #TODO subprocess.check_output first for confirming that the commands work

    with open(f"{session_files_storage}{filename}","r") as file:
        for line in file:
            try:
                subprocess.Popen(f"{line}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                print(f"Following app: '{line}', is not longer installed, please ")

def isSessionFile(path):
    for file in os.listdir(path):
        if file.endswith(".sup"):
            return True
    return False
    

# TODO needs some further dev
# def append_file_name(name):
#     counter = 0
#     name_suffix = ''
#     filename = name + "{}.sup"
#     while os.path.isfile(filename.format(name_suffix)):
#         counter += 1
#         name_suffix += str(counter)
#     filename = filename.format(counter)

if __name__ == "__main__":
    main()