import logging
logger = logging.getLogger(__name__)
import subprocess
import re
import os;import sys;
import csv
import time;import datetime
import argparse

from typing import List

DEFAULT_FILE_NAME = "session"
DEFAULT_FILE_STORAGE = "user_sessions/"

APPS_TO_IGNORE = ['gnome-terminal','gjs']
DEV_APPS_TO_IGNORE = ['gnome-terminal','code','gjs']

if sys.platform == "linux":
    import linux_cmds
    from linux_cmds import User_App
else: #TODO more platforms support
    raise ImportError(f"Sorry: no implementation for your platform ('{sys.platform}') available")


def main():
    logging.basicConfig(filename="LoadASS.log",filemode= 'w',level=logging.INFO)
    logger.info(str(datetime.datetime.now()))
    logger.info("START")

    parser = argparse.ArgumentParser(
                    prog='LoadASS-CLI',
                    description='Active software saving and loading companion application PC OS systems. (.sup) files are only supported',
                    epilog='Author: George Gorak: https://github.com/JurGOn01')
    parser.add_argument("-l","--load",help='')

    load_group = parser.add_argument_group('Load session file', '')
    load_group.add_argument("-s","--save",help='Save current active applications')
    load_group.add_argument("-f","--file",help=f'Full path of the file or just file name to load (no extension needed). Default location: ./{DEFAULT_FILE_STORAGE}')

    load_group = parser.add_argument_group('Save session file', '')
    parser.add_argument("-ls","--list",help='Displays all current active applications commands')
    args = parser.parse_args()

    #Check for os platform...
    if sys.platform == "linux":
            #load_app_session(f"{DEFAULT_FILE_STORAGE}{DEFAULT_FILE_NAME}")
            app_list = get_active_apps_info()
            save_app_session(app_list)
            # ans = input('Closing all current running apps... are you sure?\nIf so, please save any work currently open before proceeding: ')
            # close_active_apps(ans,app_list,['gnome-terminal','code','gjs'])

            if args.s and args.p:
                pass
            elif args.s and not args.p:
                pass
    elif sys.platform == "win32":
        print("Windows is not yet supported!")
    elif sys.platform == "darwin":
        print("macOS is not yet supported!")

    logger.info("END")


def save_app_session(ls: List[User_App],filepath="user_sessions/session") -> None:
    # TODO needs some further dev
    file_path= create_file_path(filepath)
    
    with open(f"{file_path}.sup", "w") as file: # .sup - (short for saved user programs) plain text format containing commands of apps to load by LoadAS. This file/s with .sup format is/are produced by the user.
        writer = csv.DictWriter(file,fieldnames=["command","x_offset","y_offset","width","height"])
        ls = filter_out_app_from_list(ls,['gjs'])
        for app in ls:
            try:
                run_command = subprocess.check_output(f"ps -p {app.PID} -o cmd=",shell=True,text=True)
                logger.info(f"The PID:{app.PID}, is {run_command} command")
                run_command = os.path.basename(run_command).removesuffix('\n')
                writer.writerow({"command": f"{run_command.rstrip()}",
                                "x_offset": app.x_offset,
                                "y_offset": app.y_offset,
                                "width": app.width,
                                "height": app.height})
            except subprocess.CalledProcessError:
                print(f"Flatpak applications are not supported: '{app.title}' application won't be added to a session file (won't be ran/loaded)")
                logger.info(f"Flatpak app: {app.title}")
                continue

def load_app_session(filepath) -> None:
    #initial checks
    if not os.path.isdir(DEFAULT_FILE_STORAGE):
        raise NameError("There are no session files to load: user_sessions/ does not exits - fix: create a session file.")
    if not isSessionFile(DEFAULT_FILE_STORAGE):
        raise NameError("There are no session files to load: user_sessions/ does exits but no single .sep session file could be found (deleted manually?) - fix: create a session file.")
    
    #TODO subprocess.check_output first for confirming that the commands work

    with open(f"{filepath}.sup","r") as file:
        reader = csv.reader(file)
        for row in reader:
        #! row --> row[0]= command, row[1]=x, row[2]=y, row[3]=width and row[4]=height
            get = lambda x: subprocess.check_output(["/bin/bash", "-c", x]).decode("utf-8")
            ws1 = get("wmctrl -lp")

            #find command based on comparison to 'database'
            app_run_cmd = get_app_cmd(row[0])
            if app_run_cmd is None:
                print(f"{row[0]} is not supported by the LoadAS software at the current time! please report this by raising the issue on github page...")
                logger.info(f"Not suported: {row[0]}")
                continue

            try:
                subprocess.Popen(f"{app_run_cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                print(f"Following app: '{app_run_cmd}', is not longer installed, the app will be omitted \n if otherwise, please recreate the session file again.")
                logger.info(f"Not installed: '{app_run_cmd}'")
            t = 0
            
            # Script taken from a StackExchange thread, made by Jacob Vlijm
            # https://askubuntu.com/questions/613973/how-can-i-start-up-an-application-with-a-pre-defined-window-size-and-position
            try:
                while t < 30:      
                    ws2 = [w.split()[0:3] for w in get("wmctrl -lp").splitlines() if not w in ws1]
                    procs = [[(p, w[0]) for p in get("ps -e ww").splitlines() \
                            if row[0] in p and w[2] in p] for w in ws2] #! row[0] used as, row[0] (app_name) !=  app_run_cmd... not always..
                    if len(procs) > 0:
                        w_id = procs[0][0][1]
                        for cmd in [f"wmctrl -ir {w_id} -b remove,maximized_horz", 
                                    f"wmctrl -ir {w_id} -b remove,maximized_vert", 
                                    f"xdotool windowsize --sync {procs[0][0][1]} {row[3]} {row[4]}", 
                                    f"xdotool windowmove {procs[0][0][1]} {row[1]} {row[2]}"]:   
                            subprocess.call(["/bin/bash", "-c", cmd])
                        break
                    time.sleep(0.5)
                    t = t+1
            except IndexError:
                print(f"{app_run_cmd} is not command for {row[0]} or\nterminal does not support this command or\nwmctrl/xdotool is not installed")
                logger.info(f"Bad cmd: {app_run_cmd},{row[0]}")
                continue

def close_active_apps(s: str,active_apps: List[User_App],ignore_apps: List[str]) -> None:
    if s.lower() == 'yes' or s.lower() == 'y':
        filtered_active_apps = filter_out_app_from_list(active_apps,ignore_apps)# allows for more to ignore/remove - when closing apps, LoadAS shoudl not be closed!
        for app in filtered_active_apps:
            subprocess.run(f"kill -9 {app.PID}",shell=True)

def get_active_apps_info() -> List[User_App]:
    """
    provides application list of all GUI open programs

    """
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

def generate_app_info(s: str) -> User_App:
    if info := re.match(r"^(0x[0-9A-Fa-f]{8})\s{1,2}(-\d|\d)\s(\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{3,4})\s{1,4}(\d{3,4})\s{1,4}([A-Za-z0-9-]{1,})\s(.{1,})$",s):
    # created with help of: https://regex101.com/r/Op2GDF/1
        # capture relevent information (dic or list) - re
        logger.info("pattern matched in apps_info_temp.txt")
        temp_user_App = User_App(info.group(3),info.group(4),info.group(5),info.group(6),info.group(7),info.group(9))
    else:
        raise LookupError("str does not match rexp:\n\n" + str + "should match regular expression:\n\n ^(0x[0-9A-Fa-f]{8})\s{1,2}(-\d|\d)\s(\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{3,4})\s{1,4}(\d{3,4})\s{1,4}([A-Za-z0-9-]{1,})\s(.{1,})$")
    return temp_user_App

def isSessionFile(path: str) -> bool:
    for file in os.listdir(path):
        if file.endswith(".sup"):
            return True
    return False

def get_app_cmd(app_str: str)-> str | None:
    for app_name in linux_cmds.database:
        if app_name in app_str:
            return linux_cmds.database[app_name]
    return None

def filter_out_app_from_list(ls: List[User_App],app_names:List[str]) -> List[User_App]:
    remove_index = []
    for app_name in app_names:
        for app in ls:
            try:
                run_command = subprocess.check_output(f"ps -p {app.PID} -o cmd=",shell=True,text=True)
                run_command_processed = os.path.basename(run_command).removesuffix('\n')
            except subprocess.CalledProcessError:
                print(f"Flatpak applications are not supported: '{app.title}'")
                logger.info(f"Flatpak app: {app.title}")
                continue
            if app_name in run_command_processed or app_name in run_command:
                remove_index.append(app)
    ls = [a for a in ls if a not in remove_index]
    
    return ls

def create_file_path(filepath: str,override=False) -> str:
    _,filename = filepath.split('/')
    if filename == DEFAULT_FILE_NAME:
        if not os.path.isdir(dir):
            os.mkdir(dir)
    counter = 1
    if not override:
        if os.path.isfile(f"{filepath}.sup") and os.path.isfile(f"{filepath}-{counter}.sup"):
            while os.path.isfile(f"{filepath}-{counter}.sup"): #TODO it may slow down later due to amount of files... algorithm improvement needed later.
                counter += 1
            filepath = f"{filepath}-{counter}.sup"
            return filepath
        elif os.path.isfile(f"{filepath}.sup"):
            return f"{filepath}-{counter}.sup"
        else:
            return f"{filepath}.sup"
    else:
        return f"{filepath}.sup"

def list_active_apps(ls: List[User_App]) -> str:
    apps_list_str = ''
    ls = filter_out_app_from_list(ls,['gjs'])
    for app in ls:
        run_command = subprocess.check_output(f"ps -p {app.PID} -o cmd=",shell=True,text=True)
        apps_list_str += str(os.path.basename(run_command).removesuffix('\n')) + '\n'
    
    return apps_list_str


if __name__ == "__main__":
    main()