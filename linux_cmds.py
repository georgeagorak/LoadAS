#! At the moment database is used as its difficult to support some apps,
# e.g. chrome's command is not chrome but google-chrome... and therefore finding the cmd via PID is not conclusive.
#TODO As result this simpler solution is used for apt-get and snap applications. (flatpaks need more attention later in development)
database = {
    #name (from ps) : command
    "chrome": "google-chrome",
    "spotify": "spotify",
    "code": "code --unity-launch",
    "gnome-terminal-server":"gnome-terminal",
    "Discord":"discord",
    "gedit":"gedit",
    "nautilus":"nautilus",
    "obs":"obs"
}

def getAllDatabaseKeys():
    keysList = [key for key in database]
    return keysList

#TODO consider classmethods instead - os could be taken as input to the class and function could be configured accordingly
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