import project
from tkinter import * 
import customtkinter


global ignorelist
ignorelist = []
checkboxes = []

def saveAsFile():
        filepath = customtkinter.filedialog.asksaveasfilename(title = "LoadAS - Select file",filetypes = (("Saved User Programs files","*.sup"),("all files","*.*")))
        
        app_session_list = project.get_active_apps_info()

        #! need include ignore window to get all to ignore apps

        project.save_app_session(app_session_list, filepath=filepath, ignore_apps= ignorelist)

def openAsFile():
        filepath = customtkinter.filedialog.askopenfilename(title = "LoadAs - Select file",filetypes = (("Saved User Programs files","*.sup"),("all files","*.*")))

        project.load_app_session(filepath,ignore_apps=ignorelist)

def closeActiveApps():
        app_session_list = project.get_active_apps_info()

        project.close_active_apps(app_session_list, ignore_apps=ignorelist)

def checkBoxListUpdate():
        for checkbox in checkboxes:
                if not checkbox.get().endswith('_off'):
                        if checkbox.get() not in ignorelist:
                                ignorelist.append(checkbox.get())
                else:
                        if checkbox.get().removesuffix('_off') in ignorelist:
                                ignorelist.remove(checkbox.get().removesuffix('_off'))
        print(ignorelist)

# Settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# Frame
app = customtkinter.CTk()
app.title("LoadAS")

app.geometry('300x400+810+300') #rough center for 1080p monitor

saveAs_button = customtkinter.CTkButton(app,width=400,height=40,text='Save session', command=saveAsFile)
saveAs_button.pack(padx=10,pady=10)
openAs_button = customtkinter.CTkButton(app,width=400,height=40,text='Open session', command=openAsFile)
openAs_button.pack(padx=10,pady=10)
close_button = customtkinter.CTkButton(app,width=400,height=40,text='Close session', command=closeActiveApps)
close_button.pack(padx=10,pady=10)

scrollable_frame = customtkinter.CTkScrollableFrame(app, width=350, height=50, label_text='Ignore CheckList')

for i, key in enumerate(project.linux_cmds.getAllDatabaseKeys()):
        check_var = customtkinter.StringVar(value="off")
        checkboxes.append(customtkinter.CTkCheckBox(scrollable_frame,text=key, command=checkBoxListUpdate,variable=check_var,onvalue=key, offvalue=f'{key}_off'))
        checkboxes[i].pack(anchor='w',pady=2,padx=25)
scrollable_frame.pack(padx=10,pady=25)

# Loop
app.mainloop()