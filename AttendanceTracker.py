#Useful pages
#https://www.pygame.org/docs/ref/image.html
#PNGs
#https://www.pngegg.com/
#
#Ensure 
# pip install pygame
# pip install pyserial
# pip install google-api-python-client --break-system-packages
# pip install google-auth-httplib2 --break-system-packages
# pip install google-auth-oauthlib --break-system-packages
# pip install gspread --break-system-packages

#ToDo : 
# Case where name is a sub-name of another e.g. Jim & Jimmy
# If using Google and the connection is lost then revert to local gracefully

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
import time

ShowKeyboard = True
KBFontSize = 48
KeyCapImg = ''
KeyCapFont = ''
KBBorder = ''
KBSpacing = ''
KeyCapScaledImg = ''
KeyCapScaledImg3x = ''
VirtualKeyPressed = -1
VirtualKeyPressedTimer = 0
KeyboardRect = 0

ConfigShowIP    = True
ConfigShowPorts = True
ConfigDefaultPadLocation = "Workshop"
CurrentPadLocation = "Workshop"
ConfigUseGoogle = True
ConfigGoogleSheetID   = ""
ConfigGoogleAutoCreateLog = True
ConfigGoogleMemberUpdateTime = 20
ConfigListTextColor = pygame.Color('darkred')
ConfigNameTextBackgroundColor = pygame.Color('lightskyblue3')
ConfigNameTextColor = pygame.Color('red')
ConfigKeyboardAlpha = 180

CurrentLoggingSheetName = "Logging"

GOOGLE_ID_COL     = 1
GOOGLE_NAME_COL   = 2
GOOGLE_TYPE_COL   = 3
GOOGLE_INOUT_COL  = 4
GOOGLE_STATUS_COL = 5

DATABASE_LOCAL  = 0
DATABASE_GOOGLE = 1

DatabaseLocation = DATABASE_LOCAL

CurrentEvent = "Workshop"

WindowWidth  = 1024
WindowHeight = 600

MemberActivityFilename = "Activity.log"
CWD = os.getcwd()

#BackgroundColor = (100,255,255)
BackgroundColor = (255,255,255)

CheckInButton = []
CheckOutButton = []
ButtonBorder = 10
ButtonHeight = 90
ButtonCurve = 25
ButtonThickness = 0

UserToSearch = ""
UserToSearchChanged = True

InputFromCardValid = False
InputFromCardActive = False
InputFromCard = ""
InputFromKeyboardActive = False
InputFromKeyboard = ""

NameTextBox = []
NameTextBoxHeight = 50
NameTextBoxText = ""

LoadedPhoto = 0
Photo2Display = 0
PhotoState = -100
PhotoEffectSpeed = 6
SplashFiles = []
KeyCapImg = ""
CursorBlinkState = False
TextInputActive = True

UnknownCardTimeout = 0
KeyboardEntryTimeout = 0

CheckInOutTimeoutClick = 0 #ToDo:
CheckInOutTimeoutCard = 0 #ToDo:
TimeoutCardActive = False #ToDo:
TimeoutClickActive = False #ToDo:
TimeoutClickClear = False #ToDo:
TimeoutCardClear = False #ToDo:

MouseDownPos = (0, 0)
MouseClicked = False

DisplayNeedUpdated = True
SerialPortName = ""
SerialPort = ""
SerialPortOpened = False
SerialPortExists = False

MemberDictionary = {}
MemberDictionaryLocal = {}
MemberDictionaryGoogle = {}
NameToID={}
NameToIDLocal={}
NameToIDGoogle={}

CurrentIP = "0.0.0.0"
GoogleConnectionGood = False
GoogleMemberCount = 0
GoogleMemberLastUpdatesAt = datetime.now() - timedelta(days=1000)

class UserStatus(Enum):
    ERROR, CREATED, CHECKIN, CHECKOUT, DISABLED = range(5)

UserStatusText = {
    UserStatus.ERROR    : "ERROR",
    UserStatus.CREATED  : "CREATED",
    UserStatus.CHECKIN  : "CHECKIN",
    UserStatus.CHECKOUT : "CHECKOUT",
    UserStatus.DISABLED : "DISABLED"
}

GoogleStatusText = {
    UserStatus.ERROR    : "ERROR",
    UserStatus.CREATED  : "Out",
    UserStatus.CHECKIN  : "In",
    UserStatus.CHECKOUT : "Out",
    UserStatus.DISABLED : "DISABLED"
}

CurrentUserStatus = UserStatus.ERROR
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
    DrawBox(Bounds, ConfigNameTextBackgroundColor, 2, 'Black')
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

    
def DisplaySearchScreen(Names):
    """Render the search window, populating the member name list box"""
#    screen.fill(BackgroundColor) 
    DrawTextInputBox(NameTextBoxRect, NameTextBoxText, ConfigNameTextColor, ConfigNameTextBackgroundColor, 'black', 2)
    DrawListBox(NameListRect, Names, ConfigListTextColor)

def UpdateDisplay():
    """
    Update the display window based on the current menu state.
    Only do this though is something happened requiring a display update
    """
    if (DisplayNeedUpdated):
        #Depending on what the current dislpay state is...
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
        #Always show a picture
        ShowPhoto()
        if (ConfigShowIP):
            ShowIP()
        if (ShowKeyboard):
            RenderKeyboard()
        #pygame.display.update()    
        pygame.display.flip()
        #Clear the buffer ready for the next renderings
        screen.fill(BackgroundColor) 

def ConsolidateMemberLists():
    """
    Merge the 2 lists if possible.
    Needs to consider whether the Google connection is good etc...
    ToDo : Lots needs to be done here !!!
    """

def CheckMemberLists():
    """
    Scan the Google and Local lists and make sure they match. 
    If not, consolidate them.
    NOTE: FOR THE MOMENT NO CONSOLIDATION IS APPLIED. GOOGLE IS CONSIDERED AUTHORITIVE
    Then make sure all member directories exists and consolidate with Google Sheets if active
    If a member directory does not exist then create it and associated database file and ensure Google matches.
    ToDo : Actually consolidate. At the end make sure the Google list and local lists match if possible. Depends on connection status etc...
    """
    global MemberDictionary
    global NameToID
    global DatabaseLocation

    if (MemberDictionaryGoogle == MemberDictionaryLocal):
        print("Lists are the same")
    else:
        print("Lists are NOT the same")
        #ToDo : At this point we need to check the local cache and update Google with any updates that need to be applied
        #We also need to make the local files match Google
        ConsolidateMemberLists()

    if (GoogleConnectionGood):
        MemberDictionary = MemberDictionaryGoogle
        NameToID = NameToIDGoogle
        DatabaseLocation = DATABASE_GOOGLE
    else:
        print("Google connection not active. Using local lists")
        MemberDictionary = MemberDictionaryLocal
        NameToID = NameToIDLocal
        DatabaseLocation = DATABASE_LOCAL

    #Scan the active list and make sure all member directories exist
    #Make sure the Members local directory exists
    CheckAndMakePath("./Members")
    for Member in MemberDictionary:
        MemberPath = "./Members/" + Member
        CurrentMemberActivityFilename = MemberPath + "/" + MemberActivityFilename
        if (not os.path.exists(MemberPath)):
            #Directory does not exists so create both directory and new log file
            os.mkdir(MemberPath)	
        if (not os.path.exists(CurrentMemberActivityFilename)):
            StatusText = UserStatusText[UserStatus.CREATED]
            CurrentDataTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            m = open(CurrentMemberActivityFilename, "a")
            m.write(CurrentDataTime + "," + CurrentEvent + "," + StatusText + "\n")
            m.close()



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
    
def AddMemberToDictionary(MemberList, IDList, ID, Name, Type, InOut, Status):
    Member =	{
        "Name": Name,
        "Type": Type,
        "InOut": InOut,
        "Status": Status
    }
    #Add the member dictionary entry to the global member dictionary
    MemberList[ID] = Member
    IDList[Name] = ID

def GoogleReadMembers():
    """"
    Load the list of members from Google Sheets
    Only do this though if a good Google connection exists and it is longer than the refresh period since last updated
    This should be safe unless a user goes from one entry pad to another quicker than this period
    """
    global MemberDictionaryGoogle
    global NameToIDGoogle
    global GoogleMemberLastUpdatesAt
    global GoogleMemberCount

    if (GoogleConnectionGood) and ((datetime.now() - GoogleMemberLastUpdatesAt) > timedelta(seconds=ConfigGoogleMemberUpdateTime)):
        GoogleMemberCount = int(GoogleMembersSheet.acell('B1').value)
        MemberData = GoogleMembersSheet.get_all_values()[2:GoogleMemberCount + 3]
        GoogleMemberLastUpdatesAt = datetime.now()
        MemberDictionaryGoogle.clear()
        NameToIDGoogle.clear()
        for Info in MemberData:
            #Build a dictionary for the member details
            #Arrays are indexed from 0. sheet columns indexed from 1
            ID = Info[GOOGLE_ID_COL - 1]
            Name = Info[GOOGLE_NAME_COL - 1]
            Type = Info[GOOGLE_TYPE_COL - 1]
            InOut = Info[GOOGLE_INOUT_COL - 1]
            Status = Info[GOOGLE_STATUS_COL - 1]
            AddMemberToDictionary(MemberDictionaryGoogle, NameToIDGoogle, ID, Name, Type, InOut, Status)

def LocalReadMembers():
    global MemberDictionaryLocal
    global NameToIDLocal
	#See if there is a list of members
    if (os.path.exists("Members.txt")):
        f = open('Members.txt', "r")
        MemberDictionaryLocal.clear()
        NameToIDLocal.clear()
        lines = f.readlines()
        for line in lines:
            line = line.rstrip()
            Info = line.split("\t")
            #Arrays are indexed from 0. sheet columns indexed from 1
            ID = Info[GOOGLE_ID_COL - 1]
            Name = Info[GOOGLE_NAME_COL - 1]
            Type = Info[GOOGLE_TYPE_COL - 1]
            InOut = Info[GOOGLE_INOUT_COL - 1]
            Status = Info[GOOGLE_STATUS_COL - 1]
            AddMemberToDictionary(MemberDictionaryLocal, NameToIDLocal, ID, Name, Type, InOut, Status)


def InitialSetup():
    """
    Perform initial launch setup, including checking all local databases exist
    If a Google connection is good then the member list and status is read from Google
    This is then compared with the local list but for the moment nothing is done if different
    """
    #If Google connection is good then read the Google member list
    GoogleReadMembers()
    #If a local list exists then read the local member list
    LocalReadMembers()
    #Now check both lists and update as necessary
    CheckMemberLists()

    #Initialize the 500ms timer event for things like cursor blink, timeout timers etc...
    pygame.time.set_timer(INTERVAL_TIMER_EVENT, 500)

    #Reset the filtered member list
    FilterDictionary("")
    
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
 
def UpdateCurrentUserLog(Action):
    """Update the current user Action in the tracking databases.
    Additionally update the Google sheet if the Google connection is active.
    ToDo : If Google is NOT active then we need to log the necessary updates.
    Parameters:
        Status (UserStatus.): ERROR, CREATED, CHECKEDIN, CHECKEDOUT, DISABLED.
    """
    #ToDo : Everything. This is completely wrong at the moment
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
        GoogleMembersSheet.update_cell(Row,GOOGLE_INOUT_COL, StatusText)
        #Then update the individual member tracking
        #ToDo : 

def SetWaitingPhoto():
    PhotoFilename = "Splash/" + random.choice(SplashFiles)
    LoadPhoto(PhotoFilename)
    PhotoState = -100
    
def KeystrokeIsValidNumber(Keystroke):    
    """
    Check if 0-9
    """
    if ((Keystroke >= ord('0')) and (Keystroke <= ord('9'))):
        return True
    else:
        return False

def KeystrokeIsValidHexDigit(Keystroke):    
    """
    Check if A-F or 0-9
    """
    if ((Keystroke >= ord('A')) and (Keystroke <= ord('F')) or ((Keystroke >= ord('0')) and (Keystroke <= ord('9')))):
        return True
    else:
        return False

def KeystrokeIsValidChar(Keystroke):
    """
    Check if A-Z or SPC
    """
    if ((Keystroke >= ord('A')) and (Keystroke <= ord('Z'))) or (Keystroke == ord(' ')):
        return True
    else:
        return False

def ToUpper(Keystroke):
    """
    Convert the keystroke to upper case
    """
    if (Keystroke < 256):
        KeyChar = chr(Keystroke)
    else:
        print("Huhh!!!")
        KeyChar = 'X'

    return ord(KeyChar.upper())

def ProcessKeyDown(Keystroke):
    """
    Process the keyboard events and update the text accordingly
    Keystrokes can also come from the virtual keyboard
    """
    global InputFromCardActive
    global InputFromCard
    global InputFromKeyboardActive
    global InputFromKeyboard
    global UserToSearchChanged
    global UserToSearch
    global InputFromCardValid
    global KeyboardEntryTimeout

    #We detect where the user information is coming from here
    #If neither keyboard or card then user to search should also be blank
    #If '0' and was perviously from keyboard then clear any existing text and use the card number
    #Not case sensitive, so convert to uper case
    Keystroke = ToUpper(Keystroke)

    if (KeystrokeIsValidNumber(Keystroke)):
        #All keycard inputs start with '0'        
        InputFromCardActive = True
        #Numbers can ONLY come from the card reader so clear any keyboard data
        if (InputFromKeyboardActive):
            InputFromKeyboardActive = False
            UserToSearch = ""
            UserToSearchChanged = True
    elif (KeystrokeIsValidChar(Keystroke)):
        #Wasn't a number (nor CR) so must be from regular keyboard
        InputFromKeyboardActive = True
        KeyboardEntryTimeout = KEYBOARD_ENTRY_TIMEOUT

    #Depending on whether keystroke came from the keyboard
    if (InputFromCardActive):
        #Keycard so check if end of string yet. Reader sends CR at end of string
        if (Keystroke == pygame.K_RETURN):
            #CR so flag current data is from the card and is valid
            InputFromCardValid = True
        else:
            #UserToSearch is only updated once the final CR is received from the card, and handled in "update"
            InputFromCard = InputFromCard + chr(Keystroke)
    elif (InputFromKeyboardActive):
        #Keyboard so process backspace and characters
        #Backspace 
        if (Keystroke == pygame.K_BACKSPACE):
            # get text input from 0 to -1 i.e. end. 
            UserToSearch = UserToSearch[:-1]
            UserToSearchChanged = True
        elif (KeystrokeIsValidChar(Keystroke)): 
            #Keyboard inputs need to update the search name as you type
            InputFromKeyboard = InputFromKeyboard + chr(Keystroke)
            UserToSearch = UserToSearch + chr(Keystroke)
            UserToSearchChanged = True

def ProcessIntervalTimerEvent():
    """Process the interval timers for the touch screen and card/tag timeout timers"""
    global UnknownCardTimeout
    global KeyboardEntryTimeout
    global UserToSearch
    global UserToSearchChanged
    global InputFromKeyboard
    global InputFromKeyboardActive
    global InputFromCard
    global InputFromCardActive

    if (UnknownCardTimeout > 0):
        print("Unknown card : ", UnknownCardTimeout)
        UnknownCardTimeout = UnknownCardTimeout - 1
        if (UnknownCardTimeout == 0):
            #Ticked down to 0, so clear the text etc...
            InputFromCard = ""
            InputFromCardActive = False
            UserToSearch = ""
            UserToSearchChanged = True
    
    if ((KeyboardEntryTimeout > 0) and (InputFromKeyboardActive)):
        print("Keyboard entry : ", KeyboardEntryTimeout)
        KeyboardEntryTimeout = KeyboardEntryTimeout - 1
        if (KeyboardEntryTimeout == 0):
            #Ticked down so reset the keyboard entry info
            InputFromKeyboard = ""
            InputFromKeyboardActive = False
            UserToSearch = ""
            UserToSearchChanged = True
            UnknownCardTimeout = 0


#    global CheckInOutTimeoutClick
#    global CheckInOutTimeoutCard
#
#    if (CheckInOutTimeoutClick > 0):
#        CheckInOutTimeoutClick = CheckInOutTimeoutClick - 1
#        print("CheckInOutTimeoutClick", CheckInOutTimeoutClick)
#
#    if (CheckInOutTimeoutCard > 0):
#        CheckInOutTimeoutCard = CheckInOutTimeoutCard - 1
#        print("CheckInOutTimeoutCard", CheckInOutTimeoutCard)


def ProcessCursorBlinkTimerEvent():
    """Toggle blinking cursor if the text box is currently active"""
    global CursorBlinkState

    if (TextInputActive):
        CursorBlinkState = not CursorBlinkState
    else:
        CursorBlinkState = False
                
def ProcessLoginSearchWindowEvents(event):
    """
    Process events specific to the search menu
    """
    if ((event.type == pygame.KEYDOWN) and (event.unicode != '')): 
        ProcessKeyDown(ord(event.unicode))
    elif (event.type == CURSOR_BLINK_TIMER_EVENT): 
        ProcessCursorBlinkTimerEvent()
    
def ProcessMouseDown(event):
    global MouseDownPos
    global MouseClicked

    MouseDownPos = event.pos
    MouseClicked = True

def ProcessGeneralEvents(event):
    """Process general events like timers etc..."""
    global running
    if event.type == pygame.QUIT: 
        running = False
    elif event.type == INTERVAL_TIMER_EVENT: 
        ProcessIntervalTimerEvent()
    elif event.type == pygame.MOUSEBUTTONDOWN: 
        #Mouse down needs to be globally monitored since it could be used on any 'screen'
        ProcessMouseDown(event)

def ProcessEvents():
    """
    Check if any events are scheduled. 
    """
    for event in pygame.event.get(): 
        ProcessGeneralEvents(event)
        if ((CurrentMenu == MenuState.SEARCH) or (CurrentMenu == MenuState.CHECKINOUT)):
            ProcessLoginSearchWindowEvents(event)

def OpenVCOM():
    global SerialPort
    global SerialPortOpened
    global SerialPortName

    if (SerialPortExists):
        try:
            SerialPort = serial.Serial(SerialPortName, 115200)
            if (SerialPort.is_open):
                SerialPortOpened = True
                return True
            else:
                SerialPortOpened = False
                return False
    #    except:
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            SerialPortOpened = False
            return False
    else:
        return False
    
def CloseVCOM():
    global SerialPort
    global SerialPortOpened

    if (SerialPortExists):
        try:
            SerialPort.close()
            return True
        except:
            print(f"Error closing serial port: {e}")
            SerialPortOpened = False
            return False
    else:
        return False

def InitSerialPort():
    """Get a list of available COM ports and try to open the first one ready to receive card/tag data"""
    global SerialPortName
    global SerialPortOpened
    global SerialPortExists

    ports = list(port_list.comports())
    if (ConfigShowPorts):
        print("Available ports = " )
        for port in ports:
            print(port.name)

    if (len(ports) > 0):
        #Use the first com port found
        if (sys.platform == "win32"):
            SerialPortDescription = ports[0]
            if (SerialPortName == ""):
                #No COM port found in config, so use the first available
                SerialPortName = SerialPortDescription.device
        else:
            SerialPortDescription = ports[0]
            if (ComPort == ""):
                #No COM port found in config, so use the first available
                #ComPort = ComPortDescription.device
                #If nothing in config then force to ttyAMA0
                SerialPortName = "/dev/ttyAMA0"
        SerialPortExists = True
        SerialPortOpened = OpenVCOM()
    else:
        print("No serial ports found. Cannot connect to RFID interface.")
        SerialPortExists = False
        SerialPortOpened = False

def CheckVCOMCard():
    """
    Checks if a card or tag has been presented to the VCOM card reader
    """
    global InputFromKeyboardActive
    global InputFromCardActive
    global InputFromCardValid
    global InputFromCard
    global UserToSearch
    global UserToSearchChanged
    global SerialPortExists
    global SerialPortOpened

    #If a serial port was opened then probably a serial port connected reader present (certainy in custom RaspPi, not necissarily on Windows)
    if (SerialPortOpened):
        try:
            CharctersInBuffer = SerialPort.in_waiting
            if (CharctersInBuffer > 16):
                #Strip off the loading 8x '0's
                ID = SerialPort.readline().strip().decode('utf-8')
                InputFromKeyboardActive = False
                InputFromCardActive = True
                InputFromCardValid = True
                InputFromCard = ID
                UserToSearch = ID
                UserToSearchChanged = True
        except:
            #Something happened to the port since we opened it !!
            print("Serial port has disappeared !!!")
            SerialPortExists = False
            SerialPortOpened = False


def CheckInternetActive(url="http://www.google.com", timeout=5):
    """
    Checks for internet connectivity by attempting to make an HTTP request to a URL.
    """
    try:
        requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False

def ReferenceToColumn(Ref):
    """
    Converts an Excel column name to a  1-based column number.
    From https://venkys.io/articles/details/excel-sheet-column-number
    Args:
        str: The Excel column name (e.g., 'A', 'AA').
    Returns:
        column_number (int): The 1-based column number (e.g., 1 for 'A', 27 for 'AA').
    """
    result = 0
    for char in Ref:
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result

def ColumnToReference(Col):
    """
    Converts a 1-based column number to its Excel column name.
    Generated by Google AI
    Args:
        column_number (int): The 1-based column number (e.g., 1 for 'A', 27 for 'AA').
    Returns:
        str: The Excel column name (e.g., 'A', 'AA').
    """
    Initial = Col
    if not isinstance(Col, int) or Col <= 0:
        raise ValueError("Column number must be a positive integer.")

    result = ""
    while Col > 0:
        # Adjust for 0-based indexing ('A' is 1, not 0)
        remainder = (Col - 1) % 26
        result = chr(65 + remainder) + result
        Col = (Col - 1) // 26
    return result

     
def GoogleAddLoggingMember(MemberID, Column):
    """
    Add the MemberID headings to the specified cell column in the Logging Google sheet
    ToDo : Chcek if the sheet is wide enough? Expand if not?
    ToDo : Should also set the Members sheet status to "Out" too
    """
    CurrentDataTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    DataToWrite = [
        ['ID', MemberID, '=SUM(E:E)'],
        ['Timestamp', 'Location', 'Action'],
        [CurrentDataTime, CurrentPadLocation, 'CREATED'] 
    ]
    Range = ColumnToReference(Column) + "2:" + ColumnToReference(Column + 2) + "4"

    try:    
        #Note: 'user_entered' is appended so that the formula is taken as though typed in rather than adding the text to the cell which would add a ' at the start
        GoogleLoggingSheet.batch_update([{'range':Range, 'values':DataToWrite}], value_input_option=gspread.utils.ValueInputOption.user_entered) 
    except gspread.exceptions.APIError as e:
        print("ERROR", e, type(e))
        #Most likely a quote error, so delay and try again
        #ToDo : Really need more robust error checking since might be some other error
        print("Write quota exceeded. Please wait...")
        time.sleep(65)
        #Then try aggain
        try:    
            GoogleLoggingSheet.batch_update([{'range':Range, 'values':DataToWrite}])
        except gspread.exceptions.APIError as e:
            print("ERROR", e, type(e))
            print("Critical error. Write quota exceeded again I don't know what to do now!!!")#I do eally know, but too lazy at the moment to implement!!


def GoogleCheckLoggingValid():
    """
    Check all the members in the Members sheet have valid and correct entries in the Logging sheet
    ToDo : Should really do this after consolidating the Google and Local lists.
    """
    #Read the current member list
    GoogleReadMembers()
    RequiredColmnCount = (4 * GoogleMemberCount) + 1
    ActualColumnCount = GoogleLoggingSheet.col_count
    if (RequiredColmnCount > ActualColumnCount):
        GoogleLoggingSheet.add_cols(RequiredColmnCount - ActualColumnCount)
    #Read the Logging headers
    #Current headers are Timestamp, Location, Action, 'In' time
    LoggingHeadersID = GoogleLoggingSheet.row_values(2)
    LoggingHeadersIDLength = len(LoggingHeadersID)
    #Scan the member list.
    #Check that the ID matches the order on the Members list.
    # If yes, move to next member
    # If no and not blank then this is an error!!
    # If blank then create it
    MemberIndex = 0 #Python lists are indexed from 0->
    for MemberID in MemberDictionaryGoogle:
        #Dictionary indexes are from 0-> but Google Sheet columns are consideed from 1-> so this starts at Google column "C" with spacing 4 columns
        #Starting at MemberDictionaryGoogle[0] check Google Sheet column 3 ("C")
        GoogleLoggingIndex = (MemberIndex * 4) + 3 
        #Check if desired position is beyond current Google Sheet header length. If not, then not fallen off the end, if yes then this entry must not be there
        if (GoogleLoggingIndex <= LoggingHeadersIDLength):
            LoggingEntry = LoggingHeadersID[GoogleLoggingIndex - 1]
            if (MemberID != LoggingEntry):
                if (LoggingEntry != ""):
                    print("Critical error. Logging sheet does not match Members order!!!")
                else:
                    print("Adding member ", MemberID, " to logging sheet")
                    #Member ID missing so add a new table entry
                    GoogleAddLoggingMember(MemberID, GoogleLoggingIndex - 1) #-1 since we need to 'skip back' a column for the "ID" text
        else:
            #Headers are missing members from the list so go ahead and add them all at once so we 'save' our write quote
            #ToDo : For the moment just add one at a time with a delay every so often to try to minimize write quote usage
            # Need to trap all quote errors though eventually
            GoogleAddLoggingMember(MemberID, GoogleLoggingIndex - 1) #-1 since we need to 'skip back' a column for the "ID" text
        MemberIndex = MemberIndex + 1

def InitGoogle():
    global GoogleConnectionGood
    global GoogleMembersSheet
    global GoogleLoggingSheet
    """Try to open a connection with the Google workbook"""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("Credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    try:
        GoogleMembersSheet = client.open_by_key(ConfigGoogleSheetID).worksheet("Members")
        try:
            GoogleLoggingSheet = client.open_by_key(ConfigGoogleSheetID).worksheet(CurrentLoggingSheetName)
        except:
            #Logging sheet doesn't exist so create it
            #ToDo : 
            print("Ooops... Need to do this still !!!")
            exit(-1)
    except:
        GoogleConnectionGood = False
        print("Google connection failed")
    else:
        GoogleConnectionGood = True
        print("Google connected")
    if ((GoogleConnectionGood) and (ConfigGoogleAutoCreateLog)):
        GoogleCheckLoggingValid()

def LoadConfig():
    """Load settings from the config.txt file"""
    global ConfigShowIP
    global ConfigShowPorts
    global ConfigUseGoogle
    global ConfigGoogleSheetID
    global ConfigGoogleMemberUpdateTime
    global ConfigGoogleAutoCreateLog
    global ConfigDefaultPadLocation
    global CurrentPadLocation
    global CurrentLoggingSheetName
    global ConfigListTextColor
    global ConfigNameTextBackgroundColor
    global ConfigNameTextColor
    global ConfigKeyboardAlpha
    global SerialPortName
    global UNKNOWN_CARD_TIMEOUT
    global CHECKINOUTCLICK_TIMEOUT
    global CHECKINOUTCARD_TIMEOUT
    global KEYBOARD_ENTRY_TIMEOUT

    ConfigShowIP                  = True # Show network IP address in top left
    ConfigShowPorts               = True # List com ports available to terminal
    ConfigDefaultPadLocation      = "Workshop" #Default location for the pad
    ConfigUseGoogle               = True #Talk to Google Sheets if possible
    ConfigGoogleMemberUpdateTime  = 60*60*24   #Minimum time between member list updates (daily since only one pad at the moment)
    ConfigGoogleSheetID           = "11ORvP8H8YU0XcTJ798n_mOx_Up1-i4hQyVXFD0EeOws"
    ConfigGoogleAutoCreateLog     = True #Automatically update the Logging sheet if a new member is added
    ConfigListTextColor           = pygame.Color('darkred')
    ConfigNameTextBackgroundColor = pygame.Color('lightskyblue3')
    ConfigNameTextColor           = pygame.Color('red')
    ConfigKeyboardAlpha           = 200

    CurrentLoggingSheetName = "Logging"
    CurrentPadLocation = ConfigDefaultPadLocation
    SerialPortName = "COM3"
    #Timeouts in 500ms ticks
    #Unknown card = 2 seconds
    UNKNOWN_CARD_TIMEOUT    = 2 * 2
    #Keybord checkin/out timeout = 5 seconds
    CHECKINOUTCLICK_TIMEOUT = 5 * 2
    #Card checkin/out timeout = 5 seconds
    CHECKINOUTCARD_TIMEOUT  = 5 * 2
    #Keyboard inactivity timeout = 5 seconds
    KEYBOARD_ENTRY_TIMEOUT = 5 * 2
    
def ProcessVirtualKeyboardClick():
    global MouseClicked
    global VirtualKeyPressed
    global VirtualKeyPressedTimer

    Column = (int)((MouseDownPos[0] - KBBorder) / KBSpacing)
    Row = (int)((MouseDownPos[1] - KBBorder) / KBSpacing)
    Index = (Row * 5) + Column
    if (Index < 26):
        Character = Index + 65
        VirtualKeyPressed = Index
    elif (Index == 29):
        Character = pygame.K_BACKSPACE
        VirtualKeyPressed = 28
    else:
        Character = 32
        VirtualKeyPressed = 27
    VirtualKeyPressedTimer = 10
    MouseClicked = False
    ProcessKeyDown(Character)

def ProcessUpdates():
    """
    Process anything that needs updating
    e.g. If card read then convert to name and fill out the search text with the corresponding name etc...
    """
    global NameTextBox
    global NameTextChanged
    global NameTextBoxText
    global UserToSearchChanged
    global UserToSearch
    global InputFromCardValid
    global InputFromCard
    global InputFromCardActive
    global UnknownCardTimeout
    global VirtualKeyPressedTimer
    global VirtualKeyPressed

    if (VirtualKeyPressedTimer > 0):
        VirtualKeyPressedTimer = VirtualKeyPressedTimer - 1
        if (VirtualKeyPressedTimer == 0):
            VirtualKeyPressed = -1

    if (ShowKeyboard and MouseClicked and KeyboardRect.collidepoint(MouseDownPos)):
        #If the keyboard is visible and Mouse clicked in the keyboard region then process accordingly
        ProcessVirtualKeyboardClick()

    if (InputFromCardValid):
        #Card input has changed and is now valid
        #Get the corresponding user name
        if (len(InputFromCard) == 16):
            #IDs from the 13MHz reader are 16 character hex numberswith 8 leading '0's so remove them
            ID = InputFromCard[-8:]
        elif (len(InputFromCard) == 10):
            #IDs from 125KHz keyboard reader are 10 digit decimal numbers
            ID = InputFromCard
        #Get the member name
        if (ID in MemberDictionary):
            #ID is in the list so get the name
            Member = MemberDictionary[ID]
            MemberName = Member["Name"]
            UserToSearch = MemberName
        else:
            #Member not found so let the user know
            MemberName = "Unknown ID " + ID
            UserToSearch = MemberName
            UserToSearchChanged = True
            UnknownCardTimeout = UNKNOWN_CARD_TIMEOUT
        #Clear the card string and flags
        InputFromCard = ""
        InputFromCardValid = False
        InputFromCardActive = False


    if (UserToSearchChanged == True):
        MemberName = UserToSearch
        NameTextBoxText = MemberName
        NameTextChanged = True
        FilterDictionary(MemberName)
        UserToSearchChanged = False

def blit_alpha(target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)        
        target.blit(temp, location)

def RenderKeyboard():
    Index = 0
    for y in range(6):
        BYC = KBBorder + (y * KBSpacing) + (KBSpacing / 2) # Button center Y
        for x in range(5):
            BXC = KBBorder + (x * KBSpacing) + (KBSpacing / 2) # Button center X
            #Set the character to display and nudge the position if SPC or DEL
            if (Index < 26):
                Character = chr(65 + Index)
            elif (Index == 26):#"SPC" is 3x wide button
                Character = ""            
                BXC = BXC + KBSpacing
            elif (Index == 27):
                Character = "<"
                BXC = BXC + KBSpacing + KBSpacing #Delete needs to be moved past the "SPC"
            #If key clicked then highlight it
            if (Index == VirtualKeyPressed):
                Alpha = 255
                KeyColor = pygame.Color('blue')
            else:
                Alpha = ConfigKeyboardAlpha
                KeyColor = pygame.Color('black')
            #Actually render the keycap
            if (Index == 26):#SPC
                #"SPC" is 3x wide but BXC is the center of the 3x, so correct start location accordingly
                blit_alpha(screen, KeyCapScaledImg3x, (BXC - (KeyCapScaledImg.get_width() / 2) - KBSpacing, BYC - (KeyCapScaledImg.get_height() / 2)), Alpha)
            elif (Index < 28):
                blit_alpha(screen, KeyCapScaledImg, (BXC - (KeyCapScaledImg.get_width() / 2), BYC - (KeyCapScaledImg.get_height() / 2)), Alpha)
            #Now add the character
            if (Index < 28):
                TextImg = KeyCapFont.render(Character, True, KeyColor)
                blit_alpha(screen, TextImg, (BXC - (TextImg.get_width() / 2), BYC - (TextImg.get_height() / 2)), Alpha)
            Index = Index + 1

def InitVirtualKeyboard():
    global KeyCapImg
    global KeyCapFont
    global KBBorder
    global KBSpacing
    global KeyCapScaledImg
    global KeyCapScaledImg3x
    global KeyboardRect

    KeyCapImg = pygame.image.load(CWD + "/Assets/KeyCap1.png")
    KeyCapFont = pygame.font.SysFont('Comic Sans MS', KBFontSize)
    KBBorder = 30
    KBSpacing = (int)(((WindowWidth / 2) - (2 * KBBorder)) / 5)
    KeyCapScaledImg = pygame.transform.smoothscale(KeyCapImg, (KBSpacing, KBSpacing))
    KeyCapScaledImg3x = pygame.transform.smoothscale(KeyCapImg, (KBSpacing * 3, KBSpacing))
    #Set bounding box for keyboard
    KeyboardRect = pygame.Rect([KBBorder, KBBorder, (5 * KBSpacing), (6 * KBSpacing)])

###################################################################################################

pygame.init() 
clock = pygame.time.Clock()
LoadConfig()
InitSerialPort()

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
InitVirtualKeyboard()

running = True
  
while running: 
    ProcessEvents()
    CheckVCOMCard()
    ProcessUpdates()
    UpdateDisplay()
    clock.tick(30)
