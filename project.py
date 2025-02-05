import logging
logger = logging.getLogger(__name__)
import subprocess
import re
import os
import sys
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
    logging.basicConfig(filename="LoadAS-CLI.log",filemode= 'w',level=logging.INFO)
    logger.info(str(datetime.datetime.now()))
    logger.info("START")
    
    parser = argparse.ArgumentParser(
                    description='LoadAS-CLI\n Active software saving and loading companion application PC OS systems. (.sup) files are only supported',
                    epilog='Author: George Gorak: https://github.com/JurGOn01')
    parser.add_argument("-s","--save",action='store_true',help='Save current active applications')
    parser.add_argument("-l","--load",action='store_true',help='Load saved applications from specified file')
    parser.add_argument("-f","--file",help=f'Full path of the file or just file name to load/save (include .sup extension at the end of file name). If onlt filename.sup is provided a default storage location: ./{DEFAULT_FILE_STORAGE} is used')
    parser.add_argument("-c","--close",action='store_true',help='Close all current active applications')
    parser.add_argument("-i","--ignore",nargs='+',help='Ignore list of active applications to close, this list must have the exact names specifed by -lss. Run -lss to get exact command for each supported application')
    parser.add_argument("-ls","--list",action='store_true',help='Displays all current active applications commands')
    parser.add_argument("-lss","--list_supported",action='store_true',help='Displays all supported active applications commands by LoadAS')
    
    #Check for os platform...T
    if sys.platform == "linux":
            #load_app_session(f"{DEFAULT_FILE_STORAGE}{DEFAULT_FILE_NAME}")
            args = parser.parse_args()
            if len(sys.argv)==1:
                parser.print_help()
            if args.save: 
                app_list = get_active_apps_info()
                if args.file:
                    filename_with_default_dir(args.file)
                if args.file and args.ignore:# saves in custom location
                    save_app_session(app_list, filepath=args.file, ignore_apps=args.ignore)
                elif args.file and not args.ignore:
                    save_app_session(app_list, filepath=args.file)
                elif not args.file and  args.ignore:
                    save_app_session(app_list, ignore_apps=args.ignore)
                else:# saves in default location
                    save_app_session(app_list)
            elif args.load and args.file:
                load_app_session(args.file)
            elif args.close:
                app_list = get_active_apps_info()
                if args.ignore:# closes applications not specified in arg.ignore
                    close_active_apps(app_list,ignore_apps=args.ignore)
                else:# closes ALL 
                    close_active_apps(app_list)
            elif args.list:
                app_list = get_active_apps_info()
                print(list_active_apps(app_list))
            elif args.list_supported:
                print('\nAll supported applications:\n')
                for key in linux_cmds.getAllDatabaseKeys():
                    print(f'{key}')
    logger.info("END")


def save_app_session(ls: List[User_App],filepath=f"{DEFAULT_FILE_STORAGE}{DEFAULT_FILE_NAME}", ignore_apps=[]) -> None:
    """
    Saves active window applications. 

    :param ls: list containing all active applications information.
    :param filepath: storage location of the .sup file to write.
    :param ignore_apps: a list of apps to ignore when saving.
    :return: a csv file in .sup format at the filepath directory.
    :rtype: void
    """
    filepath = filename_with_default_dir(filepath)
    file_path,_= adjust_file_name_and_path(filepath)

    with open(f"{file_path}", "w") as file: # .sup - (short for saved user programs) plain text format containing commands of apps to load by LoadAS. This file/s with .sup format is/are produced by the user.
        writer = csv.DictWriter(file,fieldnames=["command","x_offset","y_offset","width","height"])
        ignore_apps.append('gjs')
        ls = remove_app_from_list(ls,ignore_apps)
        for app in ls:
            try:
                run_command = subprocess.check_output(f"ps -p {app.PID} -o cmd=",shell=True,text=True)
                logger.info(f"The PID:{app.PID}, is {run_command} command")
                run_command = os.path.basename(run_command).removesuffix('\n').removesuffix(' --gapplication-service')
                writer.writerow({"command": f"{run_command.rstrip()}",
                                "x_offset": app.x_offset,
                                "y_offset": app.y_offset,
                                "width": app.width,
                                "height": app.height})
            except subprocess.CalledProcessError:
                print(f"Flatpak applications are not supported: '{app.title}' application won't be added to a session file (won't be ran/loaded)")
                logger.info(f"Flatpak app: {app.title}")
                continue

def load_app_session(filepath,ignore_apps=[]) -> None:
    """
    Loads saved previously active window applications. 
    
    :param filepath: storage location of the .sup file to read.
    :param ignore_apps: a list of apps to ignore when loading.
    :return: opens applications from the .sup file.
    :rtype: void
    """
    filepath = filename_with_default_dir(filepath)

    #TODO subprocess.check_output first for confirming that the commands work

    with open(f"{filepath.removesuffix('.sup')}.sup","r") as file:
        reader = csv.reader(file)
        for row in reader:
        #! row --> row[0]= command, row[1]=x, row[2]=y, row[3]=width and row[4]=height
            if row[0] in ignore_apps:
                continue
            
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
                while t < 60:      
                    ws2 = [w.split()[0:3] for w in get("wmctrl -lp").splitlines() if not w in ws1]
                    procs = [[(p, w[0]) for p in get("ps -e ww").splitlines() \
                            if row[0] in p and w[2] in p] for w in ws2] #! row[0] used as, row[0] (app_name) !=  app_run_cmd... not always..
                    if len(procs) > 0:
                        for cmd in [f"wmctrl -ir {procs[0][0][1]} -b remove,maximized_horz", 
                                    f"wmctrl -ir {procs[0][0][1]} -b remove,maximized_vert", 
                                    f"xdotool windowsize --sync {procs[0][0][1]} {row[3]} {row[4]}", 
                                    f"xdotool windowmove {procs[0][0][1]} {row[1]} {row[2]}"]:   
                            subprocess.call(["/bin/bash", "-c", cmd])
                        break
                    time.sleep(0.5)
                    t = t+1
            except IndexError:
                logger.info(f"Bad cmd: {app_run_cmd},{row[0]}")
                continue

def close_active_apps(active_apps: List[User_App],ignore_apps = []) -> None:
    """
    Closes active window applications. 
    
    :param active_apps: list containing all active applications information.
    :param ignore_apps: a list of apps to ignore when closing.
    :return: closes chosen active apps. 
    :rtype: void
    """
    
    filtered_active_apps = remove_app_from_list(active_apps,ignore_apps)# allows for more to ignore/remove
    for app in filtered_active_apps:
        subprocess.run(f"kill -9 {app.PID}",shell=True)

def get_active_apps_info() -> List[User_App]:
    """
    provides application list of all GUI open programs

    :return: List of all active window applications. 
    :rtype: List[User_App]
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
            if app: #avoid NoneType due to LoadAS 
                app_list.append(app)

    #return the relevent captured data (dic or list)
    logger.info(app_list)
    return app_list

def generate_app_info(s: str) -> User_App:
    """
    Filters the input string to extract PID, x_offset, 
    y_offset, width, height and title of active application for saving/loading/closing. 
    
    :param s: a string containing active application information to extract.
    :raise LookupError: If the string does not match the expected pattern generted by wmctrl command.
    :return: class strcuture containg previously mentioned parameters. 
    :rtype: User_app
    """

    if info := re.match(r"^(0x[0-9A-Fa-f]{8})\s{1,2}(-\d|\d)\s(\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{3,4})\s{1,4}(\d{3,4})\s{1,4}([A-Za-z0-9-]{1,})\s(.{1,})$",s):
    # created with help of: https://regex101.com/r/ez1cfX/1
        # capture relevent information (dic or list) - re
        logger.info("pattern matched in apps_info_temp.txt")
        temp_user_App = User_App(info.group(3),info.group(4),info.group(5),info.group(6),info.group(7),info.group(9))
        return temp_user_App
    elif 'LoadAS' in s:
        pass #do nothing, as this is GUI
    else:
        raise LookupError("str does not match rexp:\n\n" + s + "should match regular expression:\n\n ^(0x[0-9A-Fa-f]{8})\s{1,2}(-\d|\d)\s(\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{1,}|-\d{1,})\s{1,}(\d{3,4})\s{1,4}(\d{3,4})\s{1,4}([A-Za-z0-9-]{1,})\s(.{1,})$")

def isSessionFile(path: str) -> bool:
    """
    Validates the file format.

    :param path: relative/full path ending with a file name and format.
    :return: whether the value ends with *.sup file format. 
    :rtype: boolean
    """
    
    for file in os.listdir(path):
        if file.endswith(".sup"):
            return True
    return False

def get_app_cmd(app_str: str)-> str | None:
    """
    Gives back the command to run the application.  

    :param app_str: a string that is associated with a command to execute the an app.
    :return: Command line if matches the database, otherwise None. 
    :rtype: string
    """
        
    for app_name in linux_cmds.database:
        if app_name in app_str:
            return linux_cmds.database[app_name]
    return None

def remove_app_from_list(ls: List[User_App],app_names:List[str]) -> List[User_App]:
    """
    Gives back the command to run the application.  

    :param ls: list with active/to be loaded applications.
    :param app_names: application/s to be removed.
    :return: list of active/to be loaded applications. 
    :rtype: List[User_App]
    """
    
    remove_index = []
    for app_name in app_names: #! apps names have to be the name of application, not the command!
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

def adjust_file_name_and_path(filepath: str,override=False) -> str:
    """
    Creates new file name with the path incase of duplication and overwriting the session file (.sup).

    :param filepath: string contining file name.
    :param override: functionality to over write a file.
    :return: a full/relative path with (maybe) incremented file name. 
    :rtype: string
    """
        
    if not os.path.isdir(os.path.dirname(filepath)):
        os.mkdir(os.path.dirname(filepath))
    
    filepath = filepath.removesuffix('.sup')

    counter = 1
    
    #Ensures that the file will be unique (+1 at the end...)
    if not override:
        if os.path.isfile(f"{filepath}.sup") and os.path.isfile(f"{filepath}{counter}.sup"):
            while os.path.isfile(f"{filepath}{counter}.sup"): #TODO possible speed issues, with large amount of files.
                counter += 1
            filepath = f"{filepath}{counter}.sup"
            return filepath, counter
        elif os.path.isfile(f"{filepath}.sup"):
            return f"{filepath}{counter}.sup", counter
        else:
            return f"{filepath}.sup",counter
    else:
        return f"{filepath}.sup", (counter - 1)

def list_active_apps(ls: List[User_App]) -> str:
    """
    Generates a list with all active applications.
    Used primarly to display.

    :param ls: all active applications list.
    :return: long string with each application name seperated by '\\n'. 
    :rtype: string
    """

    apps_list_str = ''
    ls = remove_app_from_list(ls,['gjs'])
    for app in ls:
        run_command = subprocess.check_output(f"ps -p {app.PID} -o cmd=",shell=True,text=True)
        apps_list_str += str(os.path.basename(run_command).removesuffix('\n')) + '\n'
    
    return apps_list_str

def filename_with_default_dir(filepath):
    """
    Correcting the path if only file name only has been provided.

    :param filepath: path to the session file (.sup).
    :return: relative/full path to the session file. 
    :rtype: string
    """
    if '/' not in filepath: #User only provided a name, therefore default location used...
        if not os.path.isdir(DEFAULT_FILE_STORAGE):
            raise NameError("There are no session files to load: user_sessions/ does not exits - fix: create a session file.")
        if not isSessionFile(DEFAULT_FILE_STORAGE):
            raise NameError("There are no session files to load: user_sessions/ does exits but no single .sep session file could be found (deleted manually?) - fix: create a session file.")
        filepath = DEFAULT_FILE_STORAGE + filepath
        return filepath
    return filepath

if __name__ == "__main__":
    main()