# LoadAS - Active software saving and loading companion application for Linux
#### Video Demo:  <URL HERE>
#### Description:

## Background 
This project has been made for CS50P programming course.

The idea came to live as working in an engineering based job where different projects for which different workflows are required.
the LoadAS software is trying to ad the developer by allowing to save currently active window application and load them later on.

This is especially useful idea/feature as its common for the engineers to work on multiple projects/tasks frequently. 
This solves the time waste of reopening all necessary software to get to actual productive setup.

## Features
LoadAS has a CLI and GUI option.

Main high level features:
- Saving all active windows currently open on the OS,
- Loading specified sessions files (.sup),

Session files are saved in custom plain text file format .sup (short for Saved User Programs).

### GUI
More general user-friendly option.

...

### CLI
Allows more advanced users to use it as part of their bash scripts and/or lightweight operation via the terminal.

...

### More Functions


## Limitations, Roadblocks and Solutions

One of the limitations of the LoadAS is that the software only loads the applications themselves but without open file in the app.
Admittedly, much research has not been done in that area however it is not readily available. this is extremely difficult as accessing the applciation
open file info is not easily visiable and every application will require seperate support. (In every application, it will be differently accessed).
Therefore, that function has been abundant as the user can simply open the 'recent' files themselves.

Another limitation is the Flatpaks and other package managers. In the current implementation, flatpaks are very cumbersome to deal with their process ID, can not be used to track their application name or origin command. With apt and snap, they are supported however the method could not be generlised and commands automatically captured as when following also the process IDs, the output was not every time the command used to run the applciation. Therefore, a database soltuion has been made intead for the time being - which has its merits where it has to be manully updated and is not dynamic (if the publisher changes the command, it requires manual update). Currently only few applications are support for more of 'prototype' showcase - the database will grow as the application will.

...

## How to Contribute 
I am very happy for anyone to raise GitHub issues and suggest an idea for a new feature or different implementation of already created features.

## Further Developemnt

- More platform support - Windows and MacOS,
- Share the project.py as a module for other to use (pypi),
- Flatpak support,
- Expansion of database OR application command finder function,

....