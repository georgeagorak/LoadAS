import logging
logger = logging.getLogger(__name__)
import subprocess
import re
import os
import sys
import csv
import time
import datetime

if sys.platform == "linux":
    import linux_cmds
else: #TODO more platforms support TBD
    raise ImportError(f"Sorry: no implementation for your platform ('{sys.platform}') available")


def main():
    logging.basicConfig(filename="LoadASS.log",filemode= 'w',level=logging.INFO)
    logger.info(str(datetime.datetime.now()))
    logger.info("START")

    #Check for os platform...
    if sys.platform == "linux":
            #load_app_session("session.sup")
            app_list = get_active_apps_info()
            save_apps_2_setup_file(app_list)
            # ans = input('Closing all current running apps... are you sure?\nIf so, please save any work currently open before proceeding: ')
            # close_active_apps(ans,app_list)
    elif sys.platform == "win32":
        print("Windows is not yet supported!")
    elif sys.platform == "darwin":
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
        temp_user_App = linux_cmds.User_App(info.group(3),info.group(4),info.group(5),info.group(6),info.group(7),info.group(9))
    else:
        raise LookupError("str does not match rexp:\n\n" + str + "should match regular expression:\n\n ^(0x[0-9A-Fa-f]{8})\s{1,2}(-\d|\d)\s(\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{3,4})\s{1,4}(\d{3,4})\s{1,4}([A-Za-z0-9-]{1,})\s(.{1,})$")
    return temp_user_App

def save_apps_2_setup_file(list,filename="session",folder_path="user_sessions/"):
    # TODO needs some further dev
    file_path= create_file_path(filename,folder_path)
    
    with open(file_path, "w") as file: # .sup - (short for save user programs) plain text format containing commands of apps to load by LoadAS. This file/s with .sup format is/are produced by the user.
        writer = csv.DictWriter(file,fieldnames=["command","x_offset","y_offset","width","height"])
        list = filter_out_app_from_list(list,['gjs'])
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
                logger.info(f"Flatpak app: {app.title}")
                continue

def processed_run_command(cmd_path):
    cmd_path = os.path.basename(cmd_path)
    if "gnome-terminal" in cmd_path:
        cmd_path = cmd_path.removesuffix('-server\n') + '\n' # if gnome terminal is open!
    return [True,cmd_path.removesuffix('\n')]

def load_app_session(filename):
    session_files_storage = "user_sessions/"
    #initial checks
    if not os.path.isdir("user_sessions/"):
        raise NameError("There are no session files to load: user_sessions/ does not exits - fix: create a session file.")
    if not isSessionFile(session_files_storage):
        raise NameError("There are no session files to load: user_sessions/ does exits but no single .sep session file could be found (deleted manually?) - fix: create a session file.")
    
    #TODO subprocess.check_output first for confirming that the commands work

    with open(f"{session_files_storage}{filename}","r") as file:
        reader = csv.reader(file)
        for row in reader:
        #! row --> row[0]= command, row[1]=x, row[2]=y, row[3]=width and row[4]=height
            get = lambda x: subprocess.check_output(["/bin/bash", "-c", x]).decode("utf-8")
            ws1 = get("wmctrl -lp")

            #find command based on comparison to 'database'
            app_run_cmd = app_cmd(row[0])
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

def isSessionFile(path):
    for file in os.listdir(path):
        if file.endswith(".sup"):
            return True
    return False

def app_cmd(app_str):
    for app_name in linux_cmds.database:
        if app_name in app_str:
            return linux_cmds.database[app_name]
    return None

def close_active_apps(s,active_apps):
    if s.lower() == 'yes' or s.lower() == 'y':
        filtered_active_apps = filter_out_app_from_list(active_apps,['gnome-terminal','code','gjs'])# allows for more to ignore/remove - when closing apps, LoadAS shoudl not be closed!
        for app in filtered_active_apps:
            subprocess.run(f"kill -9 {app.PID}",shell=True)

def filter_out_app_from_list(ls,app_names):
    remove_index = []
    for app_name in app_names:
        for app in ls:
            try:
                run_command = subprocess.check_output(f"ps -p {app.PID} -o cmd=",shell=True,text=True)
                isValid, run_command_processed = processed_run_command(run_command)
            except subprocess.CalledProcessError:
                print(f"Flatpak applications are not supported: '{app.title}'")
                logger.info(f"Flatpak app: {app.title}")
                continue
            if isValid:
                if app_name in run_command_processed or app_name in run_command:
                    remove_index.append(app)
    ls = [a for a in ls if a not in remove_index]
    
    return ls

def create_file_path(name,dir,override=False):
    if name == 'session':
        if not os.path.isdir(dir):
            os.mkdir(dir)
    counter = 1
    file_full_path = f"{dir}{name}"
    if not override:
        if os.path.isfile(f"{file_full_path}.sup") and os.path.isfile(f"{file_full_path}-{counter}.sup"):
            while os.path.isfile(f"{file_full_path}-{counter}.sup"): #TODO it may slow down later due to amount of files... algorithm improvement needed later.
                counter += 1
            file_full_path = f"{file_full_path}-{counter}.sup"
            return file_full_path
        elif os.path.isfile(f"{file_full_path}.sup"):
            return f"{file_full_path}-{counter}.sup"
        else:
            return f"{file_full_path}.sup"
    else:
        return f"{file_full_path}.sup"


if __name__ == "__main__":
    main()