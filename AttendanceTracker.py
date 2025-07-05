#Useful pages
#https://www.pygame.org/docs/ref/image.html
#PNGs
#https://www.pngegg.com/
#
#Ensure 
# pip install pygame
# pip install pyserial
# pip install google-api-python-client
# pip install google-auth-httplib2
# pip install google-auth-oauthlib
# pip install gspread

#ToDo : 
# Case where name is a sub-name of another e.g. Jim & Jimmy

import pygame 
import random
import serial
import serial.tools.list_ports as port_list
import os
from enum import Enum
import re
import math
from datetime import datetime, timedelta
import sys
import socket
import gspread
from google.oauth2.service_account import Credentials

ConfigShowIP    = True
ConfigShowPorts = True
ConfigUseGoogle = True
ConfigGoogleSheetID   = ""
ConfigGoogleMemberUpdateTime = 20

GoogleSheet=""
GOOGLE_INOUT_COL = 4

CurrentEvent = "Workshop"

WindowWidth  = 1024
WindowHeight = 600

UserPhotoFilename    = "Photo.jpg"
UserActivityFilename = "Activity.log"
CurrentUserPhotoFilename = ""
CurrentUserActivityFilename = ""

#BackgroundColor = (100,255,255)
BackgroundColor = (255,255,255)

CheckInButton = []
CheckOutButton = []
ButtonBorder = 10
ButtonHeight = 90
ButtonCurve = 25
ButtonThickness = 0

NameTextBox = []
NameTextBoxHeight = 50
NameTextBackgroundColor = pygame.Color('lightskyblue3')
NameTextColor = pygame.Color('red')
NameTextBoxText = ""
NameTextChanged = True
ListTextColor = pygame.Color('darkred')

LoadedPhoto = 0
Photo2Display = 0
PhotoState = -100
PhotoEffectSpeed = 6
SplashFiles = []

CursorBlinkState = False
TextInputActive = True
CHECKINOUTCLICK_TIMEOUT = 5 * 2 
CHECKINOUTCARD_TIMEOUT  = 5 * 2
CheckInOutTimeoutClick = 0
CheckInOutTimeoutCard = 0
TimeoutCardActive = False
TimeoutClickActive = False

SomethingHappened = True
ComPort = ""
SerialPort = ""
SerialPortOpened = ""

MemberDictionary = {}
MemberDictionaryGoogle = {}
NameToID={}
NameToIDGoogle={}

CurrentIP = "0.0.0.0"
GoogleConnectionGood = False
GoogleMemberLastUpdatesAt = datetime.now() - timedelta(days=1000)

class UserStatus(Enum):
    ERROR, CREATED, CHECKEDIN, CHECKEDOUT, DISABLED = range(5)

UserStatusText = {
    UserStatus.ERROR : "ERROR",
    UserStatus.CREATED : "CREATED",
    UserStatus.CHECKEDIN : "CHECKEDIN",
    UserStatus.CHECKEDOUT : "CHECKEDOUT",
    UserStatus.DISABLED : "DISABLED"
}

GoogleStatusText = {
    UserStatus.ERROR : "ERROR",
    UserStatus.CREATED : "Out",
    UserStatus.CHECKEDIN : "In",
    UserStatus.CHECKEDOUT : "Out",
    UserStatus.DISABLED : "DISABLED"
}

CurrentUserStatus = UserStatus.CHECKEDOUT
CurrentUserID = ""
CurrentUserName = ""

CURSOR_BLINK_TIMER_EVENT = pygame.USEREVENT + 1
INTERVAL_TIMER_EVENT = pygame.USEREVENT + 2

class MenuState(Enum):
    ERROR, SEARCH, ADMIN, CHECKINOUT = range(4)

CurrentMenu = MenuState.SEARCH

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def BuildFileList(Path):
    """Build a list of all files in the specified OS path.
    Parameters:
        Path (String): OS path to directory to scan. Can be relative or absolute.
    Returns:
        List: List of file names."""
    Files = []
    if (os.path.exists(Path)):
        for entry in os.scandir(Path):
            if entry.is_file():
                Files.append(entry.name)
    return Files

def ResizeWindow():
    """Calculate all the button, list, window sizes and
    locations based on the current display window size.
    Additionally update the dislay photo parameters."""
    global WindowWidth
    global WindowHeight
    global CheckInButton
    global CheckOutButton
    global NameTextBox
    global PhotoCenter
    global NameTextBoxRect
    global NameListRect
    global CheckInRect
    global CheckOutRect

    WindowWidth  = screen.get_width()
    WindowHeight = screen.get_height()
    ButtonWidth = (WindowWidth / 4) - (2 * ButtonBorder)
    PhotoCenter = (WindowWidth / 4, WindowHeight / 2)

    CheckInButton  = [((WindowWidth / 8) * 4) + ButtonBorder, WindowHeight - ButtonHeight - ButtonBorder, ButtonWidth, ButtonHeight]
    CheckOutButton = [((WindowWidth / 8) * 6) + ButtonBorder, WindowHeight - ButtonHeight - ButtonBorder, ButtonWidth, ButtonHeight]
    NameTextBox = [((WindowWidth / 8) * 4) + ButtonBorder, ButtonBorder, (WindowWidth / 2)  - (ButtonBorder * 2), NameTextBoxHeight]
    NameTextBoxRect = pygame.Rect(NameTextBox)
    ListBoxHeight = WindowHeight - (4 * ButtonBorder) - NameTextBoxHeight - ButtonHeight
    NameListBox = [((WindowWidth / 8) * 4) + ButtonBorder, (2 * ButtonBorder) + NameTextBoxHeight, (WindowWidth / 2)  - (ButtonBorder * 2), ListBoxHeight]
    NameListRect = pygame.Rect(NameListBox)
    CheckInRect = pygame.Rect(CheckInButton)
    CheckOutRect = pygame.Rect(CheckOutButton)

    UpdatePhoto2Display()

def DrawButton(Button, Text, TextColor, ButtonColor):
    """Render a button with additional text.
    Parameters:
        Button (int[4]): Button location quad array.
        Text (String): Button text.
        TextColor (pygame.Color): Text color.
        ButtonColor (pygame.Color): Button color."""
    ButtonRect = pygame.Rect(Button)
    pygame.draw.rect(screen,ButtonColor,ButtonRect, ButtonThickness, ButtonCurve)
    txt_surface = font.render(Text, True, TextColor)
#    x = math.floor(Button[0] - ((Button[2] + txt_surface.get_width()) / 2))
#    y = math.floor(Button[1] - ((Button[3] + txt_surface.get_height()) / 2))
    x = ButtonRect.centerx - (txt_surface.get_width() / 2)
    y = ButtonRect.centery - (txt_surface.get_height() / 2)
    screen.blit(txt_surface, (x, y))

    
def ShowPhoto():
    """Render the current 'Photo2Display' in the photo window.
    Performs rotations and translations to animate the image.
    Once reached full zoom in/out animation stops."""
    global PhotoState
    PhotoPhase = PhotoState / 100

    if (PhotoState < 0):
        PhotoState = PhotoState + PhotoEffectSpeed
        if (PhotoState > 0):#Reached full size
            PhotoState = 0
            PhotoPhase = 0
        img = pygame.transform.rotozoom(Photo2Display, PhotoPhase * 360, 1.0+PhotoPhase)
        rect = img.get_rect() 
        rect.center = PhotoCenter 
        screen.blit(img, rect)
    elif (PhotoState > 0):
        PhotoState = PhotoState + PhotoEffectSpeed
        if (PhotoState >= 100):#If reached full zoom then stop
            PhotoState = 0
        else:
            img = pygame.transform.rotozoom(Photo2Display, -PhotoPhase * 360, PhotoPhase * 2)
            rect = img.get_rect() 
            rect.center = PhotoCenter 
            screen.blit(img, rect)
    else:
        rect = Photo2Display.get_rect() 
        rect.center = PhotoCenter 
        screen.blit(Photo2Display, rect)

def LoadPhoto(Filename):
    """Load the image and convert it ready to be used for rendering.
    Parameters:
        Filename (String): Path and name of image to load. Can be relative or absolute"""
    global LoadedPhoto
    LoadedPhoto = pygame.image.load(Filename)
    LoadedPhoto.convert()
    UpdatePhoto2Display()

def UpdatePhoto2Display():
    """Update the display parameters for the currently loaded photo/image"""
    global Photo2Display
    global PhotoCenter

    TargetWidth = (WindowWidth / 2) - (ButtonBorder * 2)
    WidthRatio  = (TargetWidth / LoadedPhoto.get_width())
    TargetHeight = (WindowHeight - (ButtonBorder * 2))
    HeightRatio = ( TargetHeight / LoadedPhoto.get_height())
    if (WidthRatio > HeightRatio):
        Photo2Display =  pygame.transform.smoothscale(LoadedPhoto, (LoadedPhoto.get_width() * HeightRatio,LoadedPhoto.get_height() * HeightRatio))
    else:
        Photo2Display =  pygame.transform.smoothscale(LoadedPhoto, (LoadedPhoto.get_width() * WidthRatio,LoadedPhoto.get_height() * WidthRatio))

def ShowIP():
    IPfont = pygame.font.Font(None, 12)
    txt_surface = IPfont.render(CurrentIP, True, pygame.Color('black'))
    screen.blit(txt_surface, (3, 3))
    CurrentIP

def DrawBox(Box, BoxColor, BorderThickness, BorderColor):
    """Render a box.
    Parameters:
        Box (pygame.Rect): Window location/size.
        BoxColor (pygame.Color): Text color.
        BorderThickness (int): Text box border thickness
        BorderColor(pygame.Color): Border color."""
    x = Box[0]
    y = Box[1]
    w = Box[2]
    h = Box[3]
    BorderBox = (x - BorderThickness, y - BorderThickness, w + (2 * BorderThickness), h + (2 * BorderThickness))
    
    pygame.draw.rect(screen, BorderColor, BorderBox) 
    pygame.draw.rect(screen, BoxColor, Box) 

def DrawListBox(Bounds, List, TextColor):
    """Render a list box, displaying upto the first MaxDisplayable entries.
    Parameters:
        Bounds (): (pygame.Rect): List box location/size.
        List (List): List entries to display.
        TextColor(pygame.Color): List entries text color
        """
    global FilteredEntryCount
    DrawBox(Bounds, NameTextBackgroundColor, 2, 'Black')
    FilteredEntryCount = len(List)
    MaxDisplayable = math.floor(Bounds[3] / NameTextHeight)
    if (FilteredEntryCount > MaxDisplayable):
        FilteredEntryCount = MaxDisplayable
    for Index in range(0, FilteredEntryCount):
        txt_surface = font.render(List[Index], True, TextColor)
        screen.blit(txt_surface, (Bounds[0] + 5, Bounds[1] + 5 + (Index * NameTextHeight)))
        
def DrawTextInputBox(Bounds, Text, TextColor, BackgroundColor, BorderColor, BorderThickness):
    """Render a text input box.
    Parameters:
        Bounds (pygame.Rect): Text box location/size.
        Text (String): Text to populate in the box.
        TextColor (pygame.Color): Text color.
        BackgroundColor(pygame.Color): Background color.
        BorderColor(pygame.Color): Border color.
        BorderThickness (int): Text box border thickness"""
    global font
    DrawBox(Bounds, BackgroundColor, BorderThickness, BorderColor)
    if (CursorBlinkState):
        Cursor = "|"
    else:
        Cursor = ""
    txt_surface = font.render(Text + Cursor, True, TextColor)
    screen.blit(txt_surface, (Bounds[0] + 5, Bounds[1] + 5))

def GetCurrentUserStatus():
    """Get the current user's information and status from the latest Google member update or their local database file if offline"""
    last_line = ""
    global CurrentUserPhotoFilename
    global CurrentUserActivityFilename
    global CurrentUserStatus
    global CurrentUserID
    global CurrentUserName
    
    CurrentUserName = NameTextBoxText
    CurrentUserID = NameToID[CurrentUserName]
    #Open the current user log file and get their status, photo etc
    UserPhotos = BuildFileList("./Members/" + CurrentUserID + "/Photos")
    if (len(UserPhotos) > 0):
        CurrentUserPhotoFilename = "./Members/" + CurrentUserID + "/Photos/" + random.choice(UserPhotos)
    else:
        CurrentUserPhotoFilename = "Splash/" + random.choice(SplashFiles)
    CurrentUserActivityFilename = "./Members/" + CurrentUserID + "/" + UserActivityFilename

    if (GoogleConnectionGood):
        GoogleReadMembers()
        CurrentMember = MemberDictionaryGoogle[CurrentUserID]
        TimeStamp = ""
        Location = ""
        if (CurrentMember["InOut"] == "In"):
            Action = "CHECKEDIN"
            Error = False
        elif (CurrentMember["InOut"] == "Out"):
            Action = "CHECKEDOUT"
            Error = False
        else:
            Action = "ERROR"
            Error = True
    elif (os.path.exists(CurrentUserActivityFilename)):
        with open(CurrentUserActivityFilename, 'r') as f:
            last_line = f.readlines()[-1]
        #Now extract the date/time, location and last action
        Info = re.search('(.*),(.*),(.*)', last_line)
        if(Info):
            TimeStamp = Info.group(1)
            Location = Info.group(2)
            Action = Info.group(3)
            Error = False
        else:
            TimeStamp = ""
            Action = ""
            Location = ""
            Error = True
    else:
        TimeStamp = ""
        Action = ""
        Location = ""
        Error = True
    
    if ((not Error)):
        if ((Action == "CHECKEDOUT") or (Action == "CREATED")):
            CurrentUserStatus = UserStatus.CHECKEDOUT
        elif (Action == "CHECKEDIN"):
            CurrentUserStatus = UserStatus.CHECKEDIN
        else:
            CurrentUserStatus = UserStatus.ERROR
    else:
        CurrentUserStatus = UserStatus.ERROR

    
def DisplaySearchScreen(Names):
    """Render the search window, populating the member name list box"""
#    screen.fill(BackgroundColor) 
    DrawTextInputBox(NameTextBoxRect, NameTextBoxText, NameTextColor, NameTextBackgroundColor, 'black', 2)
    DrawListBox(NameListRect, Names, ListTextColor)

def UpdateDisplay():
    """Update the display window based on the current menu state.
    If on the check in/out menu then check if a timeout has occured.
    If yes then clear the name text. If typed/clicked timeout then
    cancel the checkin/out. If the member was checked from their 
    card/tag then default to checking in/out as appropriate."""
    global NameTextChanged
    global CurrentMenu
    global NameTextBoxText
    global SomethingHappened
    global CheckInOutTimeoutCard
    global CheckInOutTimeoutClick
    global TimeoutClickActive
    global TimeoutCardActive
    global CurrentUserStatus

    Index = 0
    
    if (CurrentMenu == MenuState.CHECKINOUT):
        if ((CheckInOutTimeoutClick == 0) and (TimeoutClickActive == True)): #Current user was clicked and has timed out so clear the text and revert
            CurrentMenu = MenuState.SEARCH
            NameTextBoxText = ""
            NameTextChanged = True
            SomethingHappened = True
            TimeoutClickActive = False
            SetWaitingPhoto()

        if ((CheckInOutTimeoutCard == 0) and (TimeoutCardActive == True)): #Current user used card and has timed out so check them in/out and clear the text and revert
            if (CurrentUserStatus == UserStatus.CHECKEDOUT):
                UpdateCurrentUserStatus(UserStatus.CHECKEDIN)
            elif (CurrentUserStatus == UserStatus.CHECKEDIN):
                UpdateCurrentUserStatus(UserStatus.CHECKEDOUT)
            CurrentMenu = MenuState.SEARCH
            NameTextBoxText = ""
            NameTextChanged = True
            SomethingHappened = True
            TimeoutCardActive == False
            SetWaitingPhoto()
        
    if ((SomethingHappened == True) or (PhotoState != 0)):
        if (NameTextChanged):
            FilterDictionary(NameTextBoxText)
            NameTextChanged = False
            if (len(FilteredMembersNames) > 1):
                CurrentMenu = MenuState.SEARCH
        if (CurrentMenu == MenuState.SEARCH):
            DisplaySearchScreen(FilteredMembersNames)
        elif (CurrentMenu == MenuState.CHECKINOUT):
            DisplaySearchScreen(FilteredMembersNames)
            if (CurrentUserStatus == UserStatus.CHECKEDOUT):
                DrawButton(CheckInButton, "Check In", 'black', 'gray')
                DrawButton(CheckOutButton, "Check Out", 'lightgray', 'gray')
            elif (CurrentUserStatus == UserStatus.CHECKEDIN):
                DrawButton(CheckInButton, "Check In", 'lightgray', 'gray')
                DrawButton(CheckOutButton, "Check Out", 'black', 'gray')
        ShowPhoto()
        if (ConfigShowIP):
            ShowIP()
        #pygame.display.update()    
        pygame.display.flip()
        #Clear the buffer ready for the next renderings
        screen.fill(BackgroundColor) 

def CheckMembers():
    """Check that a members list exists and that all the associated member
    directories also exist. 
    If a member directory does not exist then create it and associated database file."""
    global NameToID
    global MemberDictionary
    global CurrentUserActivityFilename

    f = open('Members.txt', "r")
    lines = f.readlines()
    for line in lines:
        line = line.rstrip()
        fields = line.split("\t")
        ID = fields[0]
        Name = fields[1]
        Type = fields[2]
        InOut = fields[3]
        Status = fields[4]
        #Build a dictionary for the member details
        Member =	{
            "Name": Name,
            "Type": Type,
            "InOut": InOut,
            "Status": Status
        }
        #Add the member dictionary entry to the global member dictionary
        MemberDictionary[ID] = Member
        NameToID[Name] = ID
        #Make sure that the member ID database path exists
        MemberPath = "./Members/" + ID
        CurrentUserActivityFilename = MemberPath + "/" + UserActivityFilename
        CurrentDataTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if (not os.path.exists(MemberPath)):
            #Directory does not exists so create both directory and new log file
            os.mkdir(MemberPath)	
        if (not os.path.exists(CurrentUserActivityFilename)):
            UpdateCurrentUserStatusFiles(UserStatus.CREATED)
    if (GoogleConnectionGood):
        if (MemberDictionaryGoogle == MemberDictionary):
            print("Lists are the same")
        else:
            print("Lists are NOT the same")


def CheckAndMakePath(Path):
    """Check if a file system path exists and if not create it.
    Parameters:
        Path (String): Path OS path to check/create"""
    if (not os.path.exists(Path)):
        os.mkdir(Path)	

def FilterDictionary(SearhFor):
    """Filter the member list beased on the 'SearchFor' text.
    The search for text is used as a regular expression partial.
    Parameters:
        SearchFor (String): Text segment to locate in member dictionary"""
    global FilteredMembers
    global FilteredMembersNames
    FilteredMembersNames = []
    FilteredDictionary = {}
    pattern = ".*" + re.escape(SearhFor)
    for ID in MemberDictionary:
        Data = MemberDictionary[ID]
        Name = Data["Name"]
        if re.match(pattern, Name, re.IGNORECASE):
            #Add the member dictionary entry to the global member dictionary
            FilteredDictionary[ID] = Data
            FilteredMembersNames.append(Name)
    FilteredMembers =  FilteredDictionary
    FilteredMembersNames.sort(key=str.lower)
    
def GoogleReadMembers():
    """"
    Load the list of members from Google Sheets
    Only do this though if a good Google connection exists and it is longer than the refresh period since last updated
    This should be safe unless a user goes from one entry pad to another quicker than this period
    """
    global GoogleSheet
    global MemberDictionaryGoogle
    global NameToIDGoogle
    global GoogleMemberLastUpdatesAt

    if (GoogleConnectionGood) and ((datetime.now() - GoogleMemberLastUpdatesAt) > timedelta(seconds=ConfigGoogleMemberUpdateTime)):
        MemberCount = int(GoogleSheet.sheet1.acell('B1').value)
        MemberData = GoogleSheet.sheet1.get_all_values()[2:MemberCount + 3]
        GoogleMemberLastUpdatesAt = datetime.now()
        MemberDictionaryGoogle.clear()
        NameToIDGoogle.clear()
        for Info in MemberData:
            #Build a dictionary for the member details
            ID = Info[0]
            Name = Info[1]
            Type = Info[2]
            InOut = Info[3]
            Status = Info[4]
            Member =	{
                "Name": Name,
                "Type": Type,
                "InOut": InOut,
                "Status": Status
            }
            #Add the member dictionary entry to the global member dictionary
            MemberDictionaryGoogle[ID] = Member
            NameToIDGoogle[Name] = ID


def InitialSetup():
    """
    Perform initial launch setup, including checking all local databases exist
    If a Google connection is good then the member list and status is read from Google
    This is then compared with the local list but for the moment nothing is done if different
    """
    GoogleReadMembers()
	#See if there is a list of members
    if (os.path.exists("Members.txt")):
		#Yes, so make sure all necessary folders also exist
        CheckAndMakePath("./Members")
		#Now cycle through all members and make sure they have a directory
        #This also builds a list of all members
        CheckMembers()
    else:
        print("ERROR : No 'Members.txt' file exists.")
        print("        A Members file must exists with at least one ADMIN member.")
        exit(-1)

    pygame.time.set_timer(INTERVAL_TIMER_EVENT, 500)                

    
def ProcessNameClick(Name):
    """Update the search text box and current user to match the clicked name.
    Get the new clicked name status ready to update the display accordingly
    Parameters:
        Name (String): New user's name"""
    global NameTextBoxText
    global NameTextChanged
    global CurrentMenu
    global PhotoState

    NameTextBoxText = Name
    NameTextChanged = True
    CurrentMenu = MenuState.CHECKINOUT
    GetCurrentUserStatus()
    if (os.path.exists(CurrentUserPhotoFilename)):
        LoadPhoto(CurrentUserPhotoFilename)
        PhotoState = -100
    else:
        SetWaitingPhoto()

def FindGoogleIDRow(ID):
    """
    Find the corresponding Google Sheet row number for the specified used ID
    The result is the ACTUAL Google sheet row, not the offset 0 indexed row
    """
    Row = 3
    for Member in MemberDictionaryGoogle:
        if (ID == Member):
            return Row
        Row = Row + 1
    #If we reach here then a fatal error has occured!!!
    print("Serious Error !!!")

def UpdateCurrentUserStatusFiles(Status):
    """Update the current user status in the tracking databases.
    Additionally update the Google sheet if the Google connection is active.
    ToDo : If Google is NOT active then we need to log the necessary updates.
    Parameters:
        Status (UserStatus.): ERROR, CREATED, CHECKEDIN, CHECKEDOUT, DISABLED.
    """
    StatusText = UserStatusText[Status]
    CurrentDataTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #Append action to file
    m = open(CurrentUserActivityFilename, "a")
    m.write(CurrentDataTime + "," + CurrentEvent + "," + StatusText + "\n")
    m.close()
    if (GoogleConnectionGood):
        #Update the Members Google sheet
        Row = FindGoogleIDRow(CurrentUserID)
        StatusText = GoogleStatusText[Status]
        GoogleSheet.sheet1.update_cell(Row,GOOGLE_INOUT_COL, StatusText)
        #Then update the individual member tracking
        #ToDo : 

def UpdateCurrentUserStatus(Status):
    """Update the current user status to the new status.
    Update the tracking database accordingly.
    Clears any timeouts and clears the text box text.
    Parameters:
        Status (UserStatus.): ERROR, CREATED, CHECKEDIN, CHECKEDOUT, DISABLED.
    """
    global CurrentUserStatus
    global NameTextBoxText
    global NameTextChanged
    global CheckInOutTimeoutClick
    global CheckInOutTimeoutCard
    global TimeoutCardActive
    global TimeoutClickActive

    CurrentUserStatus = Status
    UpdateCurrentUserStatusFiles(Status)
    MemberDictionaryGoogle[CurrentUserID]["InOut"] = GoogleStatusText[Status]
    NameTextBoxText = "" 
    NameTextChanged = True
    CheckInOutTimeoutClick = 0
    CheckInOutTimeoutCard = 0
    TimeoutCardActive = False
    TimeoutClickActive = False


def ProcessMouseDownSearchCheckinCheckout(event):
    """Process mouse click events in the search window and redirect to specific target processing.
    If clicked in text box then set the cursor blinking and capture keyboard events to update the text
    If a name in the list is clicked then process the name.
    If clicked on a check in/out button then update the member status"""
    global TextInputActive
    global CursorBlinkState
    global CurrentUserStatus
    global NameTextBoxText
    global NameTextChanged
    global CheckInOutTimeoutClick
    global TimeoutClickActive

#Text always active now so can use keyboard mimic card reader
#    if NameTextBoxRect.collidepoint(event.pos): 
#        TextInputActive = True
#        CursorBlinkState = True
#        pygame.time.set_timer(CURSOR_BLINK_TIMER_EVENT, 500)                
#    else: 
#        TextInputActive = False
#        CursorBlinkState = False
        
    if NameListRect.collidepoint(event.pos): 
        EntryHit = math.floor((event.pos[1] - NameListRect[1]) / NameTextHeight)
        if (EntryHit < len(FilteredMembersNames)):
            #Clicked on a single entry so make it the currently selected user and prepare to check in/out
            ProcessNameClick(FilteredMembersNames[EntryHit])
            CheckInOutTimeoutClick = CHECKINOUTCLICK_TIMEOUT
            TimeoutClickActive =True
    elif ((CurrentUserStatus == UserStatus.CHECKEDOUT) and (CheckInRect.collidepoint(event.pos))):
        UpdateCurrentUserStatus(UserStatus.CHECKEDIN)
        SetWaitingPhoto()
    elif ((CurrentUserStatus == UserStatus.CHECKEDIN) and (CheckOutRect.collidepoint(event.pos))):
        UpdateCurrentUserStatus(UserStatus.CHECKEDOUT)
        SetWaitingPhoto()

def SetWaitingPhoto():
    PhotoFilename = "Splash/" + random.choice(SplashFiles)
    LoadPhoto(PhotoFilename)
    PhotoState = -100
    

def ProcessMouseDown(event):
    """Process mouse events based on the currenly active menu state"""
    global TextInputActive
    global CursorBlinkState
    global NameTextBoxText
    global NameTextChanged

    if ((CurrentMenu == MenuState.SEARCH) or (CurrentMenu == MenuState.CHECKINOUT)):
        ProcessMouseDownSearchCheckinCheckout(event)

def ProcessKeyDown(event):
    """Process the keyboard events and update the text accordingly"""
    global NameTextBoxText
    global NameTextChanged
    # Check for backspace 
    if event.key == pygame.K_BACKSPACE: 
        # get text input from 0 to -1 i.e. end. 
        NameTextBoxText = NameTextBoxText[:-1] 
    # Unicode standard is used for string 
    # formation 
    else: 
        NameTextBoxText += event.unicode
    #Note that the text has changed so we can update the filtered list
    NameTextChanged = True

def ProcessIntervalTimerEvent():
    """Process the interval timers for the touch screen and card/tag timeout timers"""
    global CheckInOutTimeoutClick
    global CheckInOutTimeoutCard

    if (CheckInOutTimeoutClick > 0):
        CheckInOutTimeoutClick = CheckInOutTimeoutClick - 1
        print("CheckInOutTimeoutClick", CheckInOutTimeoutClick)

    if (CheckInOutTimeoutCard > 0):
        CheckInOutTimeoutCard = CheckInOutTimeoutCard - 1
        print("CheckInOutTimeoutCard", CheckInOutTimeoutCard)


def ProcessCursorBlinkTimerEvent():
    """Toggle blinking cursor if the text box is currently active"""
    global CursorBlinkState

    if (TextInputActive):
        CursorBlinkState = not CursorBlinkState
    else:
        CursorBlinkState = False
                
def ProcessLoginSearchWindowEvents(event):
    """Process events specifif to the search menu"""
    if event.type == pygame.MOUSEBUTTONDOWN: 
        ProcessMouseDown(event)
    elif event.type == pygame.KEYDOWN: 
        ProcessKeyDown(event)
    elif event.type == CURSOR_BLINK_TIMER_EVENT: 
        ProcessCursorBlinkTimerEvent()

def ProcessGeneralEvents(event):
    """Process general events like timers etc..."""
    global running
    if event.type == pygame.QUIT: 
        running = False
    elif event.type == INTERVAL_TIMER_EVENT: 
        ProcessIntervalTimerEvent()

def ProcessEvents():
    """Check if any events are scheduled. 
    If yes, note that something has happened.
    Next, check and process any general events (timers etc...).
    Then check current menu status specific events (button clicks etc...)"""
    global SomethingHappened
    for event in pygame.event.get(): 
        SomethingHappened = True
        ProcessGeneralEvents(event)
        if ((CurrentMenu == MenuState.SEARCH) or (CurrentMenu == MenuState.CHECKINOUT)):
            ProcessLoginSearchWindowEvents(event)

def InitComPort():
    """Get a list of available COM ports and try to open the first one ready to receive card/tag data"""
    global ComPort
    global SerialPort
    global SerialPortOpened

    ports = list(port_list.comports())
    if (ConfigShowPorts):
        print("Available ports = " )
        for port in ports:
            print(port.name)

    if (len(ports) > 0):
        #Use the first com port found
        if (sys.platform == "win32"):
            ComPortDescription = ports[0]
            ComPort = ComPortDescription.device
        else:
            ComPort = "/dev/ttyAMA0"
        try:
            SerialPort = serial.Serial(ComPort, 115200)
            if (SerialPort.is_open):
                print("UART ", SerialPort.name, " with card reader opened correctly")
                SerialPortOpened = True
            else:
                print("UART failed to connect to card reader !!!")
                SerialPortOpened = False
    #    except:
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            SerialPortOpened = False
    else:
        print("No serial ports found. Cannot connect to RFID interface.")
        SerialPortOpened = False

def TriggerNameUpdate(Name):
    """Updates the search box text and list contents to filter to the supplied name
    then updates the display accordingly
    Parameters:
        Name (string): Name to search for"""
    global NameTextBoxText
    global NameTextChanged
    global SomethingHappened
    
    SomethingHappened = True
    ProcessNameClick(Name)
    UpdateDisplay()

def CheckCard():
    """Checks if a card or tag has been presented to the card reader"""
    global SerialPortOpened
    global CheckInOutTimeoutCard
    global TimeoutCardActive

    #If a serial port was opened then probably a serial port connected reader present (certainy in custom RaspPi, not necissarily on Windows)
    if (SerialPortOpened == True):
        CharctersInBuffer = SerialPort.in_waiting
        if (CharctersInBuffer > 16):
            print(CharctersInBuffer, " characters in the UART buffer")
            Card = SerialPort.readline().strip().decode('utf-8')[8:16]
            print("Card ID = ", Card)
            if (Card in MemberDictionary):
                MemberData = MemberDictionary.get(Card)
                MemberName = MemberData["Name"]
                print("Card ID", Card, "belongs to ", MemberName)
                TriggerNameUpdate(MemberName)
                CheckInOutTimeoutCard = CHECKINOUTCARD_TIMEOUT
                TimeoutCardActive =True
            else:
                print("Member for tag", Card, "not found")

def CheckInternetActive(url="http://www.google.com", timeout=5):
    """
    Checks for internet connectivity by attempting to make an HTTP request to a URL.
    """
    try:
        requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False

def InitGoogle():
    global GoogleConnectionGood
    global GoogleSheet
    """Try to open a connection with the Google workbook"""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("Credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    try:
        GoogleSheet = client.open_by_key(ConfigGoogleSheetID)
    except:
        GoogleConnectionGood = False
    else:
        GoogleConnectionGood = True

def LoadConfig():
    """Load settings from the config.txt file"""
    global ConfigShowIP
    global ConfigShowPorts
    global ConfigUseGoogle
    global ConfigGoogleSheetID
    global ConfigGoogleMemberUpdateTime

    ConfigShowIP                 = True # Show network IP address in top left
    ConfigShowPorts              = True # List com ports available to terminal
    ConfigUseGoogle              = True #Talk to Google Sheets if possible
    ConfigGoogleMemberUpdateTime = 60*60*24   #Minimum time between member list updates (daily since only one pad at the moment)
    ConfigGoogleSheetID          = "11ORvP8H8YU0XcTJ798n_mOx_Up1-i4hQyVXFD0EeOws" #Test workbook
#    ConfigGoogleSheetID = "12mWa63-2ru-o60eQbMBL9WbbAsfEqvWSVEQrGj7w20s" #Main workbook
    

###################################################################################################

pygame.init() 
clock = pygame.time.Clock()
LoadConfig()
InitComPort()

if (ConfigUseGoogle):
    InitGoogle()

#Make sure all directories exist and load the member database dictionary
InitialSetup()

if (sys.platform == "win32"):
    screen = pygame.display.set_mode((WindowWidth, WindowHeight), pygame.DOUBLEBUF | pygame.HWSURFACE) 
else:
    screen = pygame.display.set_mode((WindowWidth, WindowHeight), pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.FULLSCREEN)  

CurrentIP = get_ip()

font = pygame.font.Font(None, 48)
NameTextHeight = font.render("A", 1, (0, 0, 0)).get_height()

SplashFiles = BuildFileList("Splash")
PhotoFilename = "Splash/" + random.choice(SplashFiles)
screen.fill(BackgroundColor) 
LoadPhoto(PhotoFilename)
ResizeWindow()

running = True
  
while running: 
    CheckCard()
    ProcessEvents()   
    UpdateDisplay()
    SomethingHappened = False
    # clock.tick(60) means that for every second at most 
    # 60 frames should be passed. 
    clock.tick(30) 
