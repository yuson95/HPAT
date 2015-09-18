# Copyright (c) 2015 CSEC (Comprehensive Sustainable Energy Committee), Town of Concord
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# adapted from VBA code, Author: Jonah Kadoko
# Date: 04-10-15
# Description:
# This piece of code is part of a larger code that will eventually be integrated into a much larger code 
# to be used to analyse cold-climate heat pumps for the Tufts ME 145 project.
# Converted to Python 3.4 by Brad Hubbard-Nelson, 5/7/2015

# to do:
# thermal resistance - improve calculation robustness
# generalize to natural gas for comparison
# HVAC efficiency a settable parameter for comparison
# programmable thermostats for baseline system for comparison
# dual fuel system
# heat pump cooling

# matplotlib figure plotting library
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
#from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
from matplotlib import pyplot as plt

import matplotlib.dates as mdates
import matplotlib.ticker as mticker

import numpy as np

# tkinter user interface library
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from CalendarDialog import *
import AddDeliveryDlg

from datetime import datetime, date, time
from pylab import *

LARGE_FONT = ("Verdana",20)
NORM_FONT = ("Helvetica",16)
SMALL_FONT = ("Helvetica",13)
style.use("ggplot")

# globals

# Heat pump parameters

HP_MAX = 17         # max number of heat pumps to be used in the analysis 
HP_FIT = 2          # heat pump parameters that have been fit to a polynomial [1=COPmax/COPmin, 2=Qmin/Qmax]
HPiD = 13   # global for now

# part numbers of the heat pumps
part_Number = []  # Manufacturer, Model (1 To HP_MAX, 1 To 2) As String 

tDataD = []
CAPMinD = []
CAPMaxD = []
COPMinD = []
COPMaxD = []

#  COP/Q = c*T^2 + b*T + c : The constant part of the polynomial fit of the heat pump data
a_Max = [] 
a_Min = []  
b_Max = [] 
b_Min = [] # (1 To HP_MAX, 1 To HP_FIT) As Single
c_Max = [] # (1 To HP_MAX, 1 To HP_FIT) As Single
c_Min = [] # (1 To HP_MAX, 1 To HP_FIT) As Single
T_Min = [] # The min operating temperature of heat pumps

# not used?
Q_Abs_Max = [] # Absolute Maximum possible capacity
Q_Abs_Min = [] # Absolute Maximum possible capacity as given in the datasheet (not temperature dependant !)

electric_Abs_E_Max = [] # (1 To HP_MAX, 1 To HP_FIT) As Single
electric_Abs_E_Min = [] # (1 To HP_MAX, 1 To HP_FIT) As Single

BASE_HEAT_TYPE_OIL = 0
BASE_HEAT_NAME_OIL = "Fuel Oil"
STANDARD_PRICE_OIL = 3.0
EFFICIENCY_HVAC_OIL = 0.75
UNITS_OIL = "Gallons"
ENERGY_CONTENT_OIL = 139000                             # from http://www.engineeringtoolbox.com/energy-content-d_868.html
KGCO2_PER_UNIT_OIL = 72.93*1e-6*ENERGY_CONTENT_OIL

BASE_HEAT_TYPE_GAS = 1
BASE_HEAT_NAME_GAS = "Natural Gas"
STANDARD_PRICE_GAS = 999
EFFICIENCY_HVAC_GAS = 0.90
UNITS_GAS = "SCF"
ENERGY_CONTENT_GAS = 1050                               # listed as 950-1150 from http://www.engineeringtoolbox.com/energy-content-d_868.html
KGCO2_PER_UNIT_GAS = 53.06*1e-6*ENERGY_CONTENT_GAS      # http://www.epa.gov/climateleadership/documents/emission-factors.pdf

BASE_HEAT_TYPE_ELEC = 2
BASE_HEAT_NAME_ELEC = "Electric Resistance"
STANDARD_PRICE_ELEC = 0.15
EFFICIENCY_HVAC_ELEC = 0.75
UNITS_ELEC = "KWh"
ENERGY_CONTENT_ELEC = 3412     # from http://www.engineeringtoolbox.com/energy-content-d_868.html
KGCO2_PER_UNIT_ELEC = (722/2.2)*1e-3

BASE_HEAT_TYPE_LPG = 3
BASE_HEAT_NAME_LPG = "Propane"
STANDARD_PRICE_LPG = 999
EFFICIENCY_HVAC_LPG = 0.75
UNITS_LPG = "Gallons"
ENERGY_CONTENT_LPG = 91330     # from http://www.engineeringtoolbox.com/energy-content-d_868.html
KGCO2_PER_UNIT_LPG = 62.*1e-6*ENERGY_CONTENT_LPG

BASE_HEAT_TYPE_OTHER = 4
BASE_HEAT_NAME_OTHER = "????"
STANDARD_PRICE_OTHER = 999
EFFICIENCY_HVAC_OTHER = 1.0
UNITS_OTHER = "???"
ENERGY_CONTENT_OTHER = 1
KGCO2_PER_UNIT_OTHER = 0

BaseHeatType = BASE_HEAT_NAME_OIL
BaseHvacEfficiency = EFFICIENCY_HVAC_OIL
BaseEnergyContent = ENERGY_CONTENT_OIL     # from http://www.engineeringtoolbox.com/energy-content-d_868.html
BaseEnergyUnits = UNITS_OIL
BaseKgCO2PerUnit = KGCO2_PER_UNIT_OIL

SuppHeatType = BASE_HEAT_NAME_OIL
SuppHvacEfficiency = EFFICIENCY_HVAC_OIL
SuppEnergyContent = ENERGY_CONTENT_OIL     # from http://www.engineeringtoolbox.com/energy-content-d_868.html
SuppEnergyUnits = UNITS_OIL
SuppKgCO2PerUnit = KGCO2_PER_UNIT_OIL

ElecKgCO2PerUnit = KGCO2_PER_UNIT_ELEC

T_Outdoor = [] # (1 To SITE_DATA_MAX) As Single ' outdoor temperature
T_Indoor = 65  #  As Single 'indoor temperaure as provided by the user

# times at which the temperature data was taken, this includes date and time
t_Data = []    # (1 To SITE_DATA_MAX) As Date 
t_Start = 0
t_End = 0

# AVerage COP approximated for that particular temperature, should always be between COPmax and COPmin
COP_Ave = [] # (1 To SITE_DATA_MAX, 1 To HP_MAX) As Single 

# Customer Specific parameters
fuelDeliveryHeader = ""
purchase_Date = []
purchase_Vol = []
purchase_Cost = []
numDeliveries = 0
last_Purchase = -1

#turn_ON_Date  = datetime.date(2015,10,15)   # As Date # winter time on which the customer is likely to turn the HVAC
#turn_OFF_Date  = datetime.date(2015,5,15)  # As Date # turn off HVAC heating
turn_ON_Date  = datetime.date(2015,9,15)   # As Date # winter time on which the customer is likely to turn the HVAC
turn_OFF_Date  = datetime.date(2015,6,1)  # As Date # turn off HVAC heating

# average resistance is calculated per purchase period
approx_Resistance = [] # (1 To PURCHASES_MAX, 1 To 2) As Double 
average_Resistance = -1.0

# arrays indexed by time (calculated from temperature vs time data)
timeArray = []
Q_required = []         # Double # based on resistance and outdoor temperatures only
electric_Required = []  # Min consumption, Approximate requirement, Max consumption (for each heat pump)

capacity_Max = []       # maximum capacity of each heat pump in the heating period
capacity_Min = []       # minimum capacity of each heat pump in the heating period
supplemental_Heat = []  # additional heat required to meet heating requirements per hour

KWhByYear = []
SuppUnitsByYear = []
SuppUsesByYear = []
BaseUnitsByYear = []
BaseCostByYear = []

updateGraph = False
#f = Figure(figsize=(10,6), dpi=100)
#a = f.add_subplot(111)
f = plt.figure()
a = plt.subplot2grid((3,3), (0,0), rowspan=3, colspan=3)

#f1 = Figure(figsize=(3,2), dpi=100)
#a1 = f1.add_subplot(111)
f1 = plt.figure()
a1 = plt.subplot2grid((9,3), (0,0), rowspan = 4, colspan = 3)
a1.set_ylabel('COP')
a1.set_ylim(0.,5.)
a1.set_autoscalex_on(False)
a1.set_autoscaley_on(False)
a1.set_xlim(-20.,60.)
firstPlot = True

a2 = plt.subplot2grid((9,3), (5,0), rowspan = 4, colspan = 3, sharex=a1)
a2.set_ylabel('Capacity')
a2.set_xlabel('Outdoor Temp (deg F)')
a2.set_ylim(0.,50000.)
a2.set_autoscalex_on(False)
a2.set_autoscaley_on(False)
plt.grid(True)

def popupmsg(title, msg):
    
    popup = tk.Tk()
    popup.wm_title(title)
    label = ttk.Label(popup,text=msg,font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1=ttk.Button(popup, text="OK",command=popup.destroy)
    B1.pack()
    popup.mainloop()
    
def getDate(msg):
    
    popup = tk.Tk()
    popup.wm_title("Enter Date")
    label = ttk.Label(popup,text=msg,font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1=ttk.Button(popup, text="OK",command=popup.destroy)
    B1.pack()
    popup.mainloop()

def SetBLScenario(BLT) :
    global BaseHeatType,BaseHvacEfficiency,BaseEnergyContent,BaseEnergyUnits,BaseKgCO2PerUnit
    global SuppHeatType,SuppHvacEfficiency,SuppEnergyContent,SuppEnergyUnits,SuppKgCO2PerUnit
    if BLT == BASE_HEAT_TYPE_OIL :    # oil
        BaseHeatType = BASE_HEAT_NAME_OIL
        BaseHvacEfficiency = EFFICIENCY_HVAC_OIL
        BaseEnergyContent = ENERGY_CONTENT_OIL     # from http://www.engineeringtoolbox.com/energy-content-d_868.html
        BaseEnergyUnits = UNITS_OIL
        BaseKgCO2PerUnit = KGCO2_PER_UNIT_OIL
    elif BLT == BASE_HEAT_TYPE_GAS : # natural gas
        BaseHeatType = BASE_HEAT_NAME_GAS
        BaseHvacEfficiency = EFFICIENCY_HVAC_GAS
        BaseEnergyContent = ENERGY_CONTENT_GAS     # from http://www.engineeringtoolbox.com/energy-content-d_868.html
        BaseEnergyUnits = UNITS_GAS
        BaseKgCO2PerUnit = KGCO2_PER_UNIT_GAS
    elif BLT == BASE_HEAT_TYPE_ELEC : # electric
        BaseHeatType = BASE_HEAT_NAME_ELEC
        BaseHvacEfficiency = EFFICIENCY_HVAC_ELEC
        BaseEnergyContent = ENERGY_CONTENT_ELEC     # from http://www.engineeringtoolbox.com/energy-content-d_868.html
        BaseEnergyUnits = UNITS_ELEC
        BaseKgCO2PerUnit = KGCO2_PER_UNIT_ELEC
    elif BLT == BASE_HEAT_TYPE_LPG : # propane
        BaseHeatType = BASE_HEAT_NAME_LPG
        BaseHvacEfficiency = EFFICIENCY_HVAC_LPG
        BaseEnergyContent = ENERGY_CONTENT_LPG     # from http://www.engineeringtoolbox.com/energy-content-d_868.html
        BaseEnergyUnits = UNITS_LPG
        BaseKgCO2PerUnit = KGCO2_PER_UNIT_LPG
    else:
        BaseHeatType = BASE_HEAT_NAME_OIL
        BaseHvacEfficiency = EFFICIENCY_HVAC_OIL
        BaseEnergyContent = ENERGY_CONTENT_OIL     # from http://www.engineeringtoolbox.com/energy-content-d_868.html
        BaseEnergyUnits = UNITS_OIL
        BaseKgCO2PerUnit = KGCO2_PER_UNIT_OIL
        print("Other baseline heating types not supported")
    print("Baseline scenario chosen: "+BaseHeatType)

    # for now, assume supplemental system is same as the baseline system
    SuppHeatType = BaseHeatType
    SuppHvacEfficiency = BaseHvacEfficiency
    SuppEnergyContent = BaseEnergyContent     
    SuppEnergyUnits = BaseEnergyUnits
    SuppKgCO2PerUnit = BaseKgCO2PerUnit

def loadFuelDeliveries(purchasesFile):

    # this was take from previous code tested using First Parish oil purchases
    # input = open('./Residential Profiles/FP Oil Deliveries.txt')
    global numDeliveries
    global fuelDeliveryHeader
        
    numDeliveries = 0
    fuelDeliveryHeader = ""
    purchase_Vol.clear()
    purchase_Cost.clear()
    purchase_Date.clear()
    
    # read the purchases file
    
    try:
        input = open(purchasesFile,'r', encoding='latin-1')

    except:
        print("Unable to open input file")
        return
        
    test = input.read()
    lines = test.split('\n')
    input.close()
    
    LN = 0      # step through data starting at first line
    while True:
        print(lines[LN])
        fuelDeliveryHeader += lines[LN]
        LN += 1
        
        if lines[LN].find('Heat source: ')>=0 :
            HeatSource = lines[LN]
            if HeatSource.find(BASE_HEAT_NAME_OIL)>=0 :
                SetBLScenario(BASE_HEAT_TYPE_OIL)
            elif HeatSource.find(BASE_HEAT_NAME_GAS)>=0 :
                SetBLScenario(BASE_HEAT_TYPE_GAS)
            elif HeatSource.find(BASE_HEAT_NAME_ELEC)>=0 :
                SetBLScenario(BASE_HEAT_TYPE_ELEC)
            elif HeatSource.find(BASE_HEAT_NAME_LPG)>=0 :
                SetBLScenario(BASE_HEAT_TYPE_LPG)
            
        if lines[LN].find('$$')>=0 :
            LN += 1 
            break;    # locate where the data starts
    print('====================')

    if BaseHeatType == BASE_HEAT_NAME_OIL:
        lastPrice = STANDARD_PRICE_OIL
    elif BaseHeatType == BASE_HEAT_NAME_GAS:
        lastPrice = STANDARD_PRICE_GAS
    elif BaseHeatType == BASE_HEAT_NAME_ELEC:
        lastPrice = STANDARD_PRICE_ELEC
    elif BaseHeatType == BASE_HEAT_NAME_LPG:
        lastPrice = STANDARD_PRICE_LPG
    
    first = True
    while True:
        if (LN<len(lines)):
            tokens = lines[LN].split('\t')
        else:
            break
        if len(tokens)<3:
            break           # or blank lines at end of file
            
        LN += 1
    
        if not first:
            prevYear = year
        if tokens[0].isalnum():         # first delivery of a year
            year = int(tokens[0])
    
        if tokens[3].isalpha():
            continue         # skip maintenance records
        
        gallons = tokens[3].replace(',','')
        try:
            gallons = float(gallons)
        except:
            gallons = 0.0

        dollars = tokens[2][tokens[2].find('$')+1:]
        try:
            dollars = dollars.replace(',','')
            dollars = float(dollars)
        except:
            dollars = 0.0
            
        if dollars>0 and gallons>0:
            lastPrice = dollars/gallons
        elif gallons>0:
            dollars = lastPrice*gallons 
        elif dollars==0.0 and gallons==0.0:
            break
            
        if first:
            prevDeliveryDate = date(year,1,1)
            prevMonth = 12
            prevYear = year-1
        else:
            prevDeliveryDate = DeliveryDate
            prevMonth = month
        
        datestring = tokens[1]
        monthDayYear = datestring.split('/')
        month = int(monthDayYear[0])
        day = int(monthDayYear[1]) 
        monthyear = (month,year)
        prevmonthyear = (prevMonth,prevYear)

        DeliveryDate = date(year,month,day)

        purchase_Vol.append(gallons)
        purchase_Cost.append(dollars)            
        purchase_Date.append(DeliveryDate)

        numDeliveries += 1
    
    return numDeliveries
def saveFuelDeliveries(purchasesFile):

    global numDeliveries 
    global fuelDeliveryHeader   

    # open the purchases file
    if numDeliveries<=0:
        print("No delivery data to save")
        return
    
    try:
        output = open(purchasesFile,'w', encoding='latin-1')

    except:
        print("Unable to open output file")
        return
        
# write a couple line header
    now = datetime.date.today()
    now = now.isoformat()
    outputstring = "Fuel delivery data for: (enter name here)\nFile date: "+now+"\nYear	Date	$$	"+BaseEnergyUnits+"s\n"

    oldYear = 0
    for i in range(numDeliveries) :
        year = purchase_Date[i].year
        if oldYear!= year :
            oldYear = year
            outputstring += "%d\t" % year
        else :
            outputstring += "\t"
        
        day = purchase_Date[i].day
        month = purchase_Date[i].month
        year = purchase_Date[i].year % 100
        outputstring += "%d/%d/%02d\t" % (month, day, year)
        
        outputstring += "$%.2f\t" % purchase_Cost[i]
        outputstring += "%.1f\n" % purchase_Vol[i]
        
    output.write(outputstring)
    output.close()
    
    return numDeliveries

def initializeData():
    # adapted from VBA initialize, author Jonah Kadoko
    # Initialize important counters

    current_Heating_Year = 2003 # at the very least, current heating year

    workingDirectory = './Residential Profiles/'
    # filename = 'FP Oil Deliveries.txt'
    filename = 'Default Oil Deliveries.txt'
    purchasesFile = workingDirectory + filename
    numDeliveries = loadFuelDeliveries(purchasesFile)
    
def loadData():
# Adapted fromVBA project, Author: Jonah Kadoko
# Description:
# 1. Loads all the public variables
# 2. Perfoms any operations that may need to be done on the variables
# 3. TBD.....
# Application.ScreenUpdating = False

    global HP_MAX
    # read the heat pump data file
    workingDirectory = './'
    filename = 'Cold Climate Air-Source Heat Pump Listing.txt'
    HeatPumpDataFile = workingDirectory + filename
    
    
    input = open(HeatPumpDataFile,'r', encoding='latin-1')
    test = input.read()
    lines = test.split('\n')

    LN = 0      # step through data starting at first line
    tokens = lines[0].split('\t')
    if tokens[0] == 'Manufacturer':     # original Tufts file

        def tF(stringvar):
            return float((stringvar.replace(',','')).replace('"',''))
 
        oldData = False
                
        # ' Load Heat Pump Data
        first = True
        while True:
            
            if (LN<len(lines)):
                tokens = lines[LN].split('\t')
                
            else:
                break
            LN += 1
            if LN<2:
                continue;
    
            part_Number.append({'Manufacturer':tokens[0], 'Model':tokens[2], 'Outdoor Unit':tokens[3], 'Indoor Units':tokens[4],'Variable?':tokens[5],'HSPF(IV)':tokens[6],'SEER':tokens[7],'Type':tokens[10],'Zones':tokens[11]})   
            # (hp, 1) = ActiveCell.Value
    
            if len(tokens)<50 : 
                    break
 
            if oldData:
                # old buggy version of data - slope and intercept parameters calculated for COP were off
                c_Min.append([float(tokens[44]),float(tokens[38])])
                b_Min.append([float(tokens[45]),float(tokens[39])])
                a_Min.append([float(tokens[46]),float(tokens[40])]) 
                
                c_Max.append([float(tokens[47]),float(tokens[41])])
                b_Max.append([float(tokens[48]),float(tokens[42])])
                a_Max.append([float(tokens[49]),float(tokens[43])])
            else:
                # calculate linear parameters a and b from the NEEP data
                c_Min.append([0.0,0.0])

                    
                bMinCAP = (tF(tokens[11])-tF(tokens[29]))/(47-5)
                bMinCOP = (tF(tokens[17])-tF(tokens[35]))/(47-5)
                b_Min.append([bMinCOP,bMinCAP])
                
                aMinCAP = tF(tokens[29]) - 5.*bMinCAP
                aMinCOP = tF(tokens[35]) - 5.*bMinCOP
                a_Min.append([aMinCOP,aMinCAP])
                
                c_Max.append([0.0,0.0])
                
                bMaxCAP = (tF(tokens[13])-tF(tokens[31]))/(47-5)
                bMaxCOP = (tF(tokens[19])-tF(tokens[37]))/(47-5)
                b_Max.append([bMaxCOP,bMaxCAP])
                
                aMaxCAP = tF(tokens[31]) - 5.*bMaxCAP
                aMaxCOP = tF(tokens[37]) - 5.*bMaxCOP
                a_Max.append([aMaxCOP,aMaxCAP])
                
    else:   # file directly from NEEP, format different
        def tF(stringvar):
            return float((stringvar.replace(',','')).replace('"',''))
                 
        # ' Load Heat Pump Data
        first = True
        while True:
            
            if (LN==len(lines)):
                break
            LN += 1
            if LN<3:
                continue;
                
            tokens = lines[LN].split('\t') 
            if tokens[0]=='': break               
            if len(tokens)<50 : break
    
            part_Number.append({'Manufacturer':tokens[0], 'Model':tokens[2], 'Outdoor Unit':tokens[3], 
            'Indoor Units':tokens[4],'Variable?':tokens[5],'HSPF(IV)':tokens[6],'SEER':tokens[7],
            'Type':tokens[10],'Zones':tokens[11]})   
             
            try:
                # calculate linear parameters a and b from the NEEP data
                tData = [47,17,5]
                CAPMin = []
                CAPMax = []
                COPMin = []
                COPMax = []
                CAPMin.append(tF(tokens[13]))
                CAPMin.append(tF(tokens[23]))
                CAPMin.append(tF(tokens[33]))
                CAPMax.append(tF(tokens[15]))
                CAPMax.append(tF(tokens[25]))
                CAPMax.append(tF(tokens[35]))
                COPMin.append(tF(tokens[19]))
                COPMin.append(tF(tokens[29]))
                COPMin.append(tF(tokens[39]))
                COPMax.append(tF(tokens[21]))
                COPMax.append(tF(tokens[31]))
                COPMax.append(tF(tokens[41]))
                
                if tokens[47] != 'N/A':
                    tData.append(tF(tokens[47]))
                    CAPMin.append(tF(tokens[48]))
                    CAPMax.append(tF(tokens[50]))
                    COPMin.append(tF(tokens[54]))
                    COPMax.append(tF(tokens[56]))
                    
                CAPMinD.append(CAPMin)
                CAPMaxD.append(CAPMax)
                COPMinD.append(COPMin)
                COPMaxD.append(COPMax)
                tDataD.append(tData)
                
                # parametrizations of capacity and coefficient of performance
                c_Min.append([0.0,0.0])

                bMinCAP = (CAPMin[0]-CAPMin[2])/(47-5)
                bMinCOP = (COPMin[0]-COPMin[2])/(47-5)
                b_Min.append([bMinCOP,bMinCAP])
                
                aMinCAP = CAPMin[2] - 5.*bMinCAP
                aMinCOP = COPMin[2] - 5.*bMinCOP
                a_Min.append([aMinCOP,aMinCAP])
                
                c_Max.append([0.0,0.0])
                
                bMaxCAP = (CAPMax[0]-CAPMax[2])/(47-5)
                bMaxCOP = (COPMax[0]-COPMax[2])/(47-5)
                b_Max.append([bMaxCOP,bMaxCAP])
                
                aMaxCAP = CAPMax[2] - 5.*bMaxCAP
                aMaxCOP = COPMax[2] - 5.*bMaxCOP
                a_Max.append([aMaxCOP,aMaxCAP])
            except Exception as e:
                print(e)
                
    HP_MAX = len(part_Number)
def LoadTempDataRaw():
    
    T_Outdoor.clear()
    t_Data.clear()
    
    yearStart = purchase_Date[0].year
    yearEnd = purchase_Date[-1].year
    prevTemp = -999
    oneHour = datetime.timedelta(0,0,0,0,0,1,0)
    
    # loop over files from these years
    ClimaticDataPath = './Climate Data/KBED'
    for year in range(yearStart,yearEnd+1):
        filename = "%s-%i.txt" % (ClimaticDataPath, year) 
        print("Reading "+filename)
        LN = -1
        nextHour = datetime.datetime(year,1,1,0,0)
        for line in open(filename,'r',encoding='latin-1'):
            LN+=1
            if LN==0: 
                continue
            tokens = line.rstrip().split('\t')
            if len(tokens)<1:
                print("len(tokens)<1") 
                break
            try:
                datestring = tokens[0]
                if datestring.find('-') == 1 : 
                    datestring = "0"+datestring
                if datestring.find('-',3,5) == 4 :
                    datestring = datestring[0:3]+"0"+datestring[3:]
                if datestring.find(':') == 12 :
                    datestring = datestring[0:11]+"0"+datestring[11:]
                dateTime = datetime.datetime.strptime(datestring, "%m-%d-%Y %H:%M %Z")
            except:     # hit the line past the date lines
                break

            try:
                temp = float(tokens[1])
            except:
                pass
                
            # record hourly data when the next dateTime point is past the nextHour to be recorded     
            while nextHour<dateTime :
                t_Data.append(nextHour)
                T_Outdoor.append(temp)                
                nextHour = nextHour+oneHour  
            
def LoadTempData():
    # Load climatic data
    # Find location of the start of the year of the heating period

    # Improvement would be to load from mesowest.utah.edu for the location specified

    # read the climatic data file
    ClimaticDataFile = './Superseded/Modified Temp data.txt'
    first = True
    LN = -1
    NextLN = 2
    for line in open(ClimaticDataFile):
        LN += 1
        if LN<NextLN :  continue
        if len(line)>1 :            
            tokens = line.split('\t')
            dateTime = datetime.datetime.strptime(tokens[3], "%m/%d/%y %H:%M")
        else:
            break
        
        if first:
            # Find location of the start of the year of the heating period
            FirstDateTime = dateTime
            year_Start = 24 * (datetime.datetime(purchase_Date[0].year, 1, 1,0,0) - FirstDateTime)
           
            # Quickly jump to January 1st of the purchase date (or year under scrutiny)
#            LN += year_Start.days - 1
            NextLN = LN+year_Start.days
            first = False;

        else :
            #Loop through the temperature data
            t_Data.append(dateTime)
            T_Outdoor.append(float(tokens[4]))

    print("Temperature data loaded")


def animate(i):
#    dataLink = 'http://btc-e.com/api/3/trades/btc_usd?limit=2000'
#    data = urllib.request.urlopen(dataLink)
#    data = data.readall().decode("utf-8")
#    data = json.loads(data)
#    data = data["btc_usd"]
#    data = pd.DataFrame(data)
    
#    buys = data[(data['type'] == "bid")]
#    buys["datestamp"]=np.array(buys["timestamp"]).astype("datetime64[s]")
#    buyDates = (buys["datestamp"]).tolist()
#    buyPrices = (buys["price"]).tolist()
    
#    sells = data[(data['type'] == "ask")]
#    sells["datestamp"]=np.array(sells["timestamp"]).astype("datetime64[s]")
#    sellDates = (sells["datestamp"]).tolist()
#    sellPrices = (sells["price"]).tolist()
    global updateGraph

    if updateGraph :
    
#        a = plt.subplot2grid((6,4), (0,0), rowspan = 5, colspan = 4)
#        a2 = plt.subplot2grid((6,4), (5,0), rowspan = 1, colspan = 4, sharex = a)

        a.clear()
        a.plot_date(timeArray,Q_required, "g", label = "Total required heat")
        a.plot_date(timeArray,supplemental_Heat, "r", label = "Supplemental needed")
        a.plot_date(timeArray,capacity_Max, "b", label = "Maximum Capacity")
    
        a.legend(bbox_to_anchor=(0,0.92,1,.102),loc=3, ncol=3, borderaxespad=0)
        
        title = "Heat Pump Performance for "+part_Number[HPiD]['Manufacturer']+' Model '+part_Number[HPiD]['Outdoor Unit']
        a.set_title(title)
        f.canvas.draw()
        
        updateGraph = False
        
 
class HeatPumpPerformanceApp(tk.Tk):

    def __init__(self,*args, **kwargs):
        
        tk.Tk.__init__(self,*args,**kwargs)
        # tk.Tk.iconbitmap(self,default="preferences.ico")          # blows up
        tk.Tk.wm_title(self, string="Heat Pump Analysis Tool")
        
        container = tk.Frame(self)
        container.pack(side="top",fill="both",expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)
        
        self.frames = {}

        for F in (StartPage,HomePage, FuelDeliveryPage, BaselineHeatingPage, SelectHeatPumpPage,GraphPage):
            
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0,column=0,sticky="nsew")
            
        self.show_frame(StartPage)
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame) :
        
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        
        label=ttk.Label(self,text="PRELIMINARY: This heat pump analysis tool is a prototype which has been adaptated\n from the Tufts ME145 Spring 2015 project by J.Kadako et al.\nIt has limited applicability and needs to be extended to be useful\nUse at your own risk",font=NORM_FONT)        
        label.pack(pady=10,padx=10)

        label2=ttk.Label(self,text="Copyright 2015, Town of Concord Comprehensive Sustainable Energy Committee",font=SMALL_FONT)        
        label2.pack(pady=10,padx=10)

        label3=ttk.Label(self,text="This software tool can be freely distributed, and is covered by the GNU Public License",font=SMALL_FONT)        
        label3.pack(pady=10,padx=10)
 
        button1 = ttk.Button(self,text="Continue",
                    command = lambda: controller.show_frame(HomePage))
        button1.pack()

        def showLicense():
            input = open("LICENSE")
            text = input.read()
            
            popupmsg("License Information",text)

        button0 = ttk.Button(self,text="License Information",
                    command = lambda: showLicense())
        button0.pack()

        button2 = ttk.Button(self,text="Quit",
                    command = quit)
        button2.pack()
       
        
class HomePage(tk.Frame) :
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        
        label=ttk.Label(self,text="Home Page",font=LARGE_FONT)
        
        label.pack(pady=10,padx=10)
        
#        text1=ttk.Label(self,text="Analysis results to show here",font=NORM_FONT)
        text1=tk.Text(self,font=NORM_FONT, height=30, width=90)
        text1.insert(END,"\nResults:\n")
        button1 = ttk.Button(self,text="Baseline Heating Scenario",
                    command = lambda: controller.show_frame(BaselineHeatingPage))
        button1.pack()

        button2 = ttk.Button(self,text="Fuel Purchase History",
                    command = lambda: controller.show_frame(FuelDeliveryPage))
        button2.pack()

        button3 = ttk.Button(self,text="Select Heat Pump Options",
                    command = lambda: controller.show_frame(SelectHeatPumpPage))
        button3.pack()

        button4 = ttk.Button(self,text="Do Analysis",
                    command = lambda: doHeatPumpAnalysis(self, text1))
        button4.pack()

        button5 = ttk.Button(self,text="Show Graph",
                    command = lambda: controller.show_frame(GraphPage))
        button5.pack()
        
        buttonQ = ttk.Button(self,text = "Quit", command = quit)
        buttonQ.pack()
        
        text1.pack()

def doHeatPumpAnalysis(where,text): 
    global updateGraph
    global HPiD
    
#    H = 13   #   the heat pump chosen
    LoadTempDataRaw()
#   LoadTempData()      # old version, reading from a spreadsheet file
    approxResistance()
    p = heatPumpPerformance(HPiD)
    outputData(HPiD)
    
    totSavings = totBaseEmissions = totHPEmissions = totSuppEmissions = 0.

#    text.delete(where,0)
    results = "\nAnalysis of heat pump performance for "+part_Number[HPiD]['Manufacturer']+' Model '+part_Number[HPiD]['Outdoor Unit']+"\n\n"
    results += "\tBaseline ("+BaseHeatType+")\t\t\tHeat Pump\t\t\tSupplemental ("+SuppHeatType+")\n"
    results += "Year\t"+BaseEnergyUnits+"\tCost\t\tKWh\tCost\t\t#days\t"+SuppEnergyUnits+"\tCost\n"
    startYear = t_Data[t_Start].year
    endYear = t_Data[t_End].year
    for year in range(startYear,endYear+1):
        Y = year-startYear
        resultline = "%d\t%.1f\t$%.0f\t\t%.1f\t$%.0f\t\t%d\t%.1f\t$%.0f\n" % (year,BaseUnitsByYear[Y],BaseCostByYear[Y],KWhByYear[Y],KWhByYear[Y]*.15,SuppUsesByYear[Y],SuppUnitsByYear[Y],SuppUnitsByYear[Y]*3.0)
        results += resultline
        totSavings += BaseCostByYear[Y] - (KWhByYear[Y]*0.15 + SuppUnitsByYear[Y]*3)
        totBaseEmissions += BaseKgCO2PerUnit*BaseUnitsByYear[Y]
        totHPEmissions += ElecKgCO2PerUnit*KWhByYear[Y]
        totSuppEmissions += SuppKgCO2PerUnit*SuppUnitsByYear[Y]

    
    if totSavings>0 :
        savingsImpact = "saved"
    else:
        savingsImpact = "cost an additional"
        
    CO2_percent_impact = (100.*(totBaseEmissions - totHPEmissions - totSuppEmissions))/totBaseEmissions
    if CO2_percent_impact>0 : 
        CO2Impact = "less"
    else:
        CO2Impact = "more"
        
    results += "\nOver the years %d-%d, the heat pump would have %s $%.0f, emitting %.0f%% %s CO2eq than %s\n" % (startYear,endYear,savingsImpact, abs(totSavings), CO2_percent_impact, CO2Impact,BaseHeatType)
    text.insert(END,results)
    
    updateGraph = True
    

def LoadDeliveriesDlg(parent,listbox,lbHdr) :
    
    fname = filedialog.askopenfilename(filetypes=( ("text files","*.txt"),("All files","*.*") ), 
    title="Select file containing oil deliveries data" )
    if fname is None:
        print("no file selected")
    else:
        loadFuelDeliveries(fname)

    UpdateDeliveryHdrView(lbHdr)
    
    UpdateDeliveryDataView(listbox)
    
def SaveDeliveriesDlg() :
 #   root = tk.Tk()
 #   root.wm_title()
    
    fname = filedialog.asksaveasfilename(filetypes=( ("text files","*.txt"),("All files","*.*") ), 
    title="Select file to save fuel deliveries data" )
    if len(fname)>0:
        print("Saving delivery data to %s" % fname)
        saveOilDeliveries(fname)

def UpdateDeliveryDataView(listbox):
    listbox.delete(0,END)
    for h in range(numDeliveries-1) :
        datastring = "\t\t%s\t\t$%.2f\t\t%.1f" % (purchase_Date[h],purchase_Cost[h],purchase_Vol[h])
        listbox.insert(h,datastring)

def UpdateDeliveryHdrView(lb):
    lb.delete(0,END)
    
    if len(fuelDeliveryHeader)>0 :
        hl = fuelDeliveryHeader.split('\n')
        for h in range(len(hl)):
            hdrString = "\t\t"+hl[h]
            lb.insert(h,hl[h])
    else:
        lb.insert(0,"\t\tNo delivery data entered")
    
class AddDeliveryDlg(tkSimpleDialog.Dialog):
    """Dialog box that displays a calendar and returns the selected date"""
    
        
    def body(self, master):
#        self.calendar = ttkcalendar.Calendar(master)
#        self.calendar.pack()
        lblDate = ttk.Label(self,text="Delivery Date",font=SMALL_FONT)
        lblDate.pack()
#        self.lblDate.grid(row=3, column=1)
        today = datetime.date.today()
        dateString =datetime.date.isoformat(today)
#        deliveryDate = StringVar()
 #       deliveryDate.set(dateString)
        def setDeliveryDate():
            cd = CalendarDialog(self)
            dateString = datetime.date(cd.result.year, cd.result.month, cd.result.day).isoformat()
            deliveryDate.set(dateString)
            txtDate.delete(0,END)
            txtDate.insert( 0,dateString)       
        def updateDeliveryList():
            pass
        txtDate = Entry(self, width=10, textvariable=deliveryDate)
#        txtDate.grid(row=3, column=2)
        txtDate.pack()
        txtDate.delete(0, END)
        txtDate.insert(0,dateString)
        
        btnDate = tk.Button(self, text="Calendar", command=lambda: setDeliveryDate())
#        btnDate.grid(row=3, column=2)
        self.btnDate.pack()

        self.lblAmount = ttk.Label(self,text="Quantity",font=SMALL_FONT)
        self.lblAmount.pack()
        deliveryAmount = StringVar()
        txtAmount = tk.Entry(self, width=10, textvariable=deliveryAmount)
#        txtAmount.grid(row=3, column=2)
        txtAmount.pack()
        
        lblCost = ttk.Label(self,text="Total Cost",font=SMALL_FONT)
        lblCost.pack()
        deliveryCost = StringVar()
        txtCost = tk.Entry(self, width=10, textvariable=deliveryCost)
#        txtCost.grid(row=3, column=2)
        txtCost.pack()
        
        btnUpdate = tk.Button(self, text="Add and continue", command=lambda: updateDeliveryList())
#        btnUpdate.grid(row=3, column=2)
        btnUpdate.pack()

    def apply(self):
        result = (date,deliveryAmount,deliveryCost)
            
def AddDelivery(self,listbox):
    # dialog to inquire date cost and volume
    dDate,dCost,dAmount = AddDeliveryDlg(self)
    # find location in list
    
    # insert into lists
    
    UpdateDeliveryDataView(listbox)
        
def ClearDeliveryData(self,listbox):
    # are you sure
    global numDeliveries
    
    # clear the data
    numDeliveries = 0
    purchase_Date.clear()
    purchase_Cost.clear()
    purchase_Vol.clear()
    
    # Update the listbox
    
    UpdateDeliveryDataView(listbox)
        
def DeleteDelivery(listbox):
    # inquire "Are you sure" (proceed, cancel options, with don't ask again option)
    
    # get index to delivery
    
    # delete entry from lists
    
    UpdateDeliveryDataView(listbox)
        
def EditDelivery(listbox):
    # dialog with delivery info to modify (with save, cancel options)
    
    # if date changed, get new index
        # delete from existing loc, insert into new loc
    
    # update entry in lists
    
    UpdateDeliveryDataView(listbox)
        
class FuelDeliveryPage(tk.Frame):
    global fuelDeliveryHeader
    
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=ttk.Label(self,text="Fuel Deliveries Page: This is for current oil customers",font=LARGE_FONT)        
        label.grid(row=0,column=0,columnspan=4,sticky=(E,W), pady=10,padx=10)
        
        lblHdr=ttk.Label(self,text="Delivery header information (select to edit)",font=SMALL_FONT)        
        lblHdr.grid(row=1,column=1, pady=10)

        lblData=ttk.Label(self,text="Delivery data (select to edit)",font=SMALL_FONT)        
        lblData.grid(row=3,column=1, pady=10)

        button1 = ttk.Button(self,text="Load Delivery Data",
                    command = lambda: LoadDeliveriesDlg(self, lbData,lbHdr))
        button1.grid(row=8,column=0)

        button2 = ttk.Button(self,text="Enter/Edit Deliveries",
                    command = lambda: EditDeliveriesDlg(self))
        button2.grid(row=8,column=1)

        button3 = ttk.Button(self,text="Save Delivery data",
                    command = lambda: SaveDeliveriesDlg(self))
        button3.grid(row=8,column=2)

        lbHdr = tk.Listbox(self,selectmode=tk.SINGLE,height=2,width=80)
        lbHdr.grid(row=2,column=0,columnspan=3)

        lbData = tk.Listbox(self,selectmode=tk.SINGLE,height=20,width=80)
        lbData.grid(row=4,column=0,columnspan=3, rowspan=4)

        button4 = ttk.Button(self,text="Done",
                    command = lambda: controller.show_frame(HomePage))
        button4.grid(row=9,column=1)

        button5 = ttk.Button(self,text="Add Delivery",
                    command = lambda: AddDelivery(self,lbData))
        button5.grid(row=4,column=4)

        button6 = ttk.Button(self,text="Edit Delivery",
                    command = lambda: EditDelivery(self,lbData))
        button6.grid(row=5,column=4)

        button7 = ttk.Button(self,text="Delete Delivery",
                    command = lambda: DeleteDelivery(self,lbData))
        button7.grid(row=6,column=4)

        button7 = ttk.Button(self,text="Delete All Deliveries",
                    command = lambda: ClearDeliveryData(self,lbData))
        button7.grid(row=7,column=4)

        button8 = ttk.Button(self,text="Edit",command = lambda: EditHeaderInfo())
        button8.grid(row=2,column=4)
        
        UpdateDeliveryHdrView(lbHdr)    
        UpdateDeliveryDataView(lbData)
            
class BaselineHeatingPage(tk.Frame):
    global EfficiencyHVAC
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=ttk.Label(self,text="Baseline Heating Options: Select alternative system for comparison",font=LARGE_FONT)
        label.grid(row=0,column=2,columnspan=3,pady=10,padx=10)
  
        label1=ttk.Label(self,text="Select baseline system type, efficiency, and operating parameters",font=SMALL_FONT)
        label1.grid(row=1,column=2,columnspan=3,pady=30,padx=10)
        
        BLType = IntVar()
        BLType.set(0)
        
        rb1 = tk.Radiobutton(self, text=BASE_HEAT_NAME_OIL,      variable=BLType, value=0, command=lambda: SetBLScenario(BASE_HEAT_TYPE_OIL))
        rb2 = tk.Radiobutton(self, text=BASE_HEAT_NAME_GAS,  variable=BLType, value=1, command=lambda: SetBLScenario(BASE_HEAT_TYPE_GAS))
        rb3 = tk.Radiobutton(self, text=BASE_HEAT_NAME_ELEC,  variable=BLType, value=2, command=lambda: SetBLScenario(BASE_HEAT_TYPE_ELEC))
        rb4 = tk.Radiobutton(self, text=BASE_HEAT_NAME_LPG,  variable=BLType, value=3, command=lambda: SetBLScenario(BASE_HEAT_TYPE_LPG))
        rb5 = tk.Radiobutton(self, text="Other",  variable=BLType, value=4, command=lambda: SetBLScenario(BASE_HEAT_TYPE_OTHER))

        rb1.grid(row=2,column=0)
        rb2.grid(row=2,column=1)
        rb3.grid(row=2,column=2)
        rb4.grid(row=2,column=3)
        rb5.grid(row=2,column=4)
        rb1.invoke()
        
#        def getEfficiency():
#            global EFFICIENCY_HVAC
#            EFFICIENCY_HVAC = float1.getDouble()
        def evaluate(event):
            s = eff.get() 
            try:
                efficiency = float(s)
                EfficiencyHVAC = efficiency
            except:
                print("bad value")

        EfficiencyHVAC = EFFICIENCY_HVAC_OIL
        s = "%f" % (EfficiencyHVAC)
        
        eff = StringVar()
        eff.set(s)

        label2=ttk.Label(self,text="\tSet System Efficiency",font=SMALL_FONT)
        label2.grid(row=3,column=0,columnspan=3,pady=30,padx=10)
        e = Entry(self, width=5, textvariable=eff)
        e.bind("<Return>", evaluate)
        e.grid(row=3, column=3)

              
        def setStartDate() :
            cd = CalendarDialog(self)
            turn_ON_Date = datetime.date(cd.result.year, cd.result.month, cd.result.day)         
            print (turn_ON_Date)
        def setEndDate() :
            cd = CalendarDialog(self)
            turn_OFF_Date = datetime.date(cd.result.year, cd.result.month, cd.result.day)           
            print (turn_OFF_Date)

        label3=ttk.Label(self,text="Set Annual System Start/End Dates",font=SMALL_FONT)
        label3.grid(row=4,column=0,columnspan=3,pady=30,padx=10)
            
        button2 = ttk.Button(self,text="Start Date",
                    command = lambda: setStartDate())
        button2.grid(row=4,column=3)

        button3 = ttk.Button(self,text="End Date",
                    command = lambda: setEndDate())
        button3.grid(row=4,column=4)

        button4 = ttk.Button(self,text="Done",
                    command = lambda: controller.show_frame(HomePage))
        button4.grid(row=10, column=2)

def selHeatPump(H):
    global HPiD
    global firstPlot

    
    HPiD = H

    COPMax = []
    COPMin = []
    CAPMax = []
    CAPMin = []
            
    tMin=-5
    if len(tDataD[HPiD])>3 : tMin = tDataD[HPiD][3]
    
    if tMin>-20 and tMin<60 :
        tempArray=[tMin, 60]        
    else :
        tempArray = list(range(-20,60,2))
        
    for i in range(len(tempArray)):
        t = tempArray[i]
        COPMax.append(t*t*c_Max[HPiD][0] + t*b_Max[HPiD][0] + a_Max[HPiD][0])
        COPMin.append(t*t*c_Min[HPiD][0] + t*b_Min[HPiD][0] + a_Min[HPiD][0])
        CAPMax.append(t*t*c_Max[HPiD][1] + t*b_Max[HPiD][1] + a_Max[HPiD][1])
        CAPMin.append(t*t*c_Min[HPiD][1] + t*b_Min[HPiD][1] + a_Min[HPiD][1])
                
    a1.clear()
            
    if firstPlot:
        l1c, = a1.plot(tDataD[HPiD],COPMaxD[HPiD], linestyle='-', color="red", marker='*', markersize=10,label = "COP (max capacity)") 
        l1d, = a1.plot(tDataD[HPiD],COPMinD[HPiD], linestyle='-', color="blue", marker=r'*', markersize=10, label = "COP (min capacity)") 
    else:
        l1c.set_xdata(tDataD[HPiD])
        l1c.set_ydata(COPMaxD[HPiD])
        l1d.set_xdata(tDataD[HPiD])
        l1d.set_ydata(COPMinD[HPiD])

    a1.set_xlim(tMin-5., 60)
    a1.set_ylim(ymin=0.,ymax=6.)
    a1.legend(bbox_to_anchor=(0,0.80,1,.1),loc=3, ncol=3, borderaxespad=0)
        
    title = "COP for "+part_Number[HPiD]['Manufacturer']+' Model '+part_Number[HPiD]['Outdoor Unit']
    a1.set_title(title)

    a2.clear()
    if firstPlot:
                
        l2c, = a2.plot(tDataD[HPiD],CAPMaxD[HPiD], linestyle='-', color="red", marker=r'*', markersize=10, label = "Max capacity") 
        l2d, = a2.plot(tDataD[HPiD],CAPMinD[HPiD], linestyle='-', color="blue", marker=r'*', markersize=10, label = "Min capacity") 
        title = "Capacity vs temperature"
        a2.set_title(title)
        a2.legend(bbox_to_anchor=(0,0.80,1,.1),loc=3, ncol=3, borderaxespad=0)
    else:
        l2c.set_xdata(tDataD[HPiD])
        l2c.set_ydata(CAPMaxD[HPiD])
        l2d.set_xdata(tDataD[HPiD])
        l2d.set_ydata(CAPMinD[HPiD])
    a2.set_ylim(ymin=0.,ymax=60000.)
                
    f1.canvas.draw()
    
class SelectHeatPumpPage(tk.Frame):
    def __init__(self,parent,controller):
        global HPiD
        HPFilter = ['Ductless','Ducted','All']

        HPListIndex2ID = []
        
        tk.Frame.__init__(self,parent)
        label=ttk.Label(self,text="\tHeat Pump Selection Page: View parameters for NEEP recommended cold climate heat pumps\n",font=LARGE_FONT)
        label.grid(row=0,column=0,columnspan=5, sticky=(W,E))

        lb = tk.Listbox(self,selectmode=tk.SINGLE,height=15,width=50)

        HPType = IntVar()
        HPType.set(0)
                    
        def FillHPListBox(lb, filterVar):
            lb.delete(0,lb.size())
            filter = filterVar    # the string variable
            filter = HPFilter[filter]
            for h in range(HP_MAX):
                ductless = (part_Number[h]['Type'] == 'Ductless')
                if ( (ductless and (filter=='Ductless' or filter=='All')) or ((not ductless) and (filter != 'Ductless'))) :
                    insertText = part_Number[h]['Manufacturer']+" Model "+part_Number[h]['Model']+" "+part_Number[h]['Type']
                    if part_Number[h]['Type'] == 'Ductless':
                        insertText+='-'+part_Number[h]['Zones']
                    lb.insert(h,insertText)
                    HPListIndex2ID.append(h)

        rb1 = tk.Radiobutton(self, text="Ductless", variable=HPType, value=0, command=lambda: FillHPListBox(lb,0))
        rb2 = tk.Radiobutton(self, text="Ducted",   variable=HPType, value=1, command=lambda: FillHPListBox(lb,1))
        rb3 = tk.Radiobutton(self, text="Both",     variable=HPType, value=2, command=lambda: FillHPListBox(lb,2))

        rb1.grid(row=1,column=0)
        rb2.grid(row=1,column=1)
        rb3.grid(row=1,column=2)
        rb1.invoke()

        lb.grid(row=2,column=0, rowspan=1,columnspan=3,sticky=(N))
        lb.activate(HPiD)
        
        canvas = FigureCanvasTkAgg(f1,self)
        canvas.show()
        canvas.get_tk_widget().grid(column=3, columnspan=3, row=1, rowspan=3)  #fill=tk.BOTH,,pady=10

        text1 = ttk.Label(self,text='Selected Heat Pump Data',font=NORM_FONT)
        text1.grid(row=3,column=0,columnspan=3,sticky=(N,E,W))

        button1 = ttk.Button(self,text="Select Heat Pump",
                    command = lambda: selHeatPump(HPListIndex2ID[lb.curselection()[0]]))
        button1.grid(row=5, column=0)
  
        
        button4 = ttk.Button(self,text="Done",
                    command = lambda: controller.show_frame(HomePage))
        button4.grid(row=5,column=1)        
       

class GraphPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        
        label=ttk.Label(self,text="Heat Pump Graph",font=LARGE_FONT)        
        label.pack(pady=10,padx=10)
        
        button1 = ttk.Button(self,text="Done",
                    command = lambda: controller.show_frame(HomePage))
        button1.pack()
        
        canvas = FigureCanvasTkAgg(f,self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=True)
        
        toolbar = NavigationToolbar2TkAgg(canvas,self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP,fill=tk.BOTH,expand=True)

def isHeating(t) :

# Author: Jonah Kadoko
# this function determines if the heat pump should heat the room at this particular time
# Reasons why your heat pump may not turn ON include, but not limited to the following,:
# 1, The outdoor temp is lower than the min operating temp of the heat pump
# 2, It is in the summer time before your specified turn_ON_Date and after the turn_OFF_Date
# 3, The heat pump overshoot for that particular hour and so is cycling (not much modelling has been done to simumlate cycling)

    if t_Data[t] <= datetime.datetime(t_Data[t].year, turn_OFF_Date.month, turn_OFF_Date.day) :
        current_Heating_Year = t_Data[t].year - 1    
    else:
        current_Heating_Year = t_Data[t].year
    
    yr_Turn_OFF = datetime.datetime(current_Heating_Year + 1, turn_OFF_Date.month, turn_OFF_Date.day)
    yr_Turn_ON = datetime.datetime(current_Heating_Year, turn_ON_Date.month, turn_ON_Date.day)

    if (t_Data[t_Start] <= t_Data[t]) and (t_Data[t] <= yr_Turn_OFF) and \
    (yr_Turn_ON <= t_Data[t]) and (t_Data[t] <= t_Data[t_End]) and (T_Outdoor[t] < T_Indoor) :
        # t is within range of the heating period and purchase period and the outdoor temperature is below the indoor temperature
        return True
    else:
        return False        
    
def approxResistance():
    # Adapted from VBA project, Author: Jonah Kadoko
    # Decide the hour to start and stop the calculations
    # 1, t_Start should be the index of time corresponding to the second purchase date (since the customer fills up their tank each time)
    # 2, t_End should be  the date corresponding the last purchase date
    global t_Start
    global t_End
    global last_Purchase
    global average_Resistance
    
    p = 0
    approx_Resistance.clear()
    while True:
        approx_Resistance.append([0,0])
        p+=1
        if p==numDeliveries: break

    t = 0    
 
    p = numDeliveries-1
    last_Purchase = p
    if purchase_Vol[p] == 0 :
                last_Purchase = p - 1
    
    while t<len(t_Data):    # (t_Start == 0) or (t_End == 0):
        if (t_Start==0):
            if purchase_Date[0] == t_Data[t].date() :
                # All calculations should start a day after the customer fills up their tank around the start of the year
                # t_Start is the index of the time the customer fi
                t_Start = t

        elif (t_End==0 and purchase_Date[last_Purchase] == t_Data[t].date()) :
            # calculations should stop at the last purchase date of the year
            t_End = t
            break

        t = t + 1

    if t_End==0 :
        t_End = len(t_Data)-1
        
    startYear = t_Data[t_Start].year
    endYear = t_Data[t_End].year
    BaseUnitsByYear.clear()
    BaseCostByYear.clear()
    for year in range(startYear,endYear+1):
        BaseUnitsByYear.append(0.0)
        BaseCostByYear.append(0.0)

    # Calculate total annual delta T
    delta_T = 0.0
    for t in range(t_Start,t_End) :
        if isHeating(t):
            delta_T = delta_T + (T_Indoor - T_Outdoor[t])

    # Calculate the total oil used
    total_Vol = 0.0
    for p in range(0, last_Purchase):
        year = purchase_Date[p].year
        Y = year - startYear
        if year <= endYear:
            total_Vol = purchase_Vol[p] + total_Vol
            BaseUnitsByYear[Y] += purchase_Vol[p]
            BaseCostByYear[Y] += purchase_Cost[p]

    # Calculate the average resistance per heating period
    p = 0
    approx_Resistance[0][0] = t_Start
    approx_Resistance[0][1] = 0.0
    for t in range(t_Start,t_End):
        
        ti = t-t_Start
        dateTime = t_Data[t]
        year = dateTime.year
        Y = year - startYear
        
        thisDate = t_Data[t].date()
        if isHeating(t) and (purchase_Date[p] <= thisDate) and (thisDate <= purchase_Date[p + 1]) and (p < last_Purchase) :

            # Sum app eligible delta_T during each heating period
    
            approx_Resistance[p][1] += (T_Indoor - T_Outdoor[t]) / (BaseHvacEfficiency * purchase_Vol[p + 1] * BaseEnergyContent)
    
        else:
            if isHeating(t) and (purchase_Date[p + 1] <= thisDate) and (thisDate <= purchase_Date[last_Purchase]) and (p < last_Purchase): 
                # this particular time sample belongs to the next purchase period
                p = p + 1
                approx_Resistance[p][0] = t
                approx_Resistance[p][1] =  (T_Indoor - T_Outdoor[t]) / (BaseHvacEfficiency * purchase_Vol[p + 1] * BaseEnergyContent)
    
 
    # Average resistance during the heating period
    average_Resistance = delta_T / (BaseHvacEfficiency * BaseEnergyContent * total_Vol)

    
def heatPumpPerformance(H):
    #Author: Jonah Kadoko
    #this function calculates the approximate min, and max heating capacity, COPave and average electrical consumption
    #One would expect that the required heat be in between the max and min heating capacities

    global last_Purchase
    global average_Resistance
    global Q_required, timeArray
    global capacity_Max, capacity_Min, electric_Required, supplemental_Heat, COP_Ave

    use_Average_R = True
    
    p = 0

    startYear = t_Data[t_Start].year
    endYear = t_Data[t_End].year
    
    KWhByYear.clear()
    SuppUnitsByYear.clear()
    SuppUsesByYear.clear()
#    BaseUnitsByYear.clear()
#    BaseCostByYear.clear()
        
    timeArray = [t_Data[t] for t in range(t_Start,t_End)]
    Q_required = [0.0 for t in range(t_Start, t_End)]
    capacity_Max = [-1.0 for t in range(t_Start,t_End)]
    capacity_Min = [0.0 for t in range(t_Start,t_End)]
    electric_Required = [0.0 for t in range(t_Start,t_End)]
    supplemental_Heat = [0.0 for t in range(t_Start,t_End)]
    COP_Ave = [0.0 for t in range(t_Start,t_End)]
 
    supplementalLastDate = t_Data[0]   # for determining how many supplemental days there are
    oldYear = 1900
    
    for t in range(t_Start,t_End):
        ti = t-t_Start
        dateTime = timeArray[ti]
        year = timeArray[ti].year
        Y = year - startYear
        
        if year > oldYear:
            oldYear = year
            KWhByYear.append(0.0)
            SuppUnitsByYear.append(0.0)
            SuppUsesByYear.append(0)
            BaseUnitsByYear.append(0.0)
#BaseCostByYear.clear()
                    
        
        
        # Calculate the perfomance
        if (use_Average_R) : 
            resistance = average_Resistance            
        else :
            resistance = approx_Resistance[p][1]

        if isHeating(t):
    
            if (purchase_Date[p] <= t_Data[t].date()) and (t_Data[t].date() <= purchase_Date[p + 1]) and (p < last_Purchase) :
                # Sum app eligible delta_T during each heating period
                Q_required[ti] = (T_Indoor - T_Outdoor[t])/ resistance
            else:
                if (purchase_Date[p + 1] <= t_Data[t].date()) and (t_Data[t].date() <= purchase_Date[last_Purchase]) and (p < last_Purchase) :
                    # this particular time sample belongs to the next purchase period
                    p = p + 1
                    Q_required[ti] = (T_Indoor - T_Outdoor[t]) / resistance
    
                else:
                    #'Most likely this data point should not be heated or it falls out of the purchase period
                    print('Do nothing')
        
        
        # using the two point parametrization?
        twoPointFit = False
        
        if twoPointFit:
            # Calculate electrical energy required per heat pump
            COP_Max = c_Max[H][0] * T_Outdoor[t]**2 + b_Max[H][0] * T_Outdoor[t] + a_Max[H][0]
            COP_Min = c_Min[H][0] * T_Outdoor[t]**2 + b_Min[H][0] * T_Outdoor[t] + a_Min[H][0]
            capacity_Max[ti] = c_Max[H][1] * T_Outdoor[t]**2 + b_Max[H][1] * T_Outdoor[t] + a_Max[H][1]
            capacity_Min[ti] = c_Min[H][1] * T_Outdoor[t]**2 + b_Min[H][1] * T_Outdoor[t] + a_Min[H][1]
        else:
            if T_Outdoor[t]>tDataD[H][0]:
                # warmer than the 47 deg point
                capacity_Max[ti] = CAPMaxD[H][0]
                capacity_Min[ti] = CAPMinD[H][0]
                COP_Min = COPMinD[H][0]
                COP_Max = COPMaxD[H][0]
            elif T_Outdoor[t] <= tDataD[H][-1]:
                # colder than the coldest point specified
                # question as to how heat pump will perform here - assume it doesn't function at that temperature
                capacity_Max[ti] = CAPMaxD[H][-1]
                capacity_Min[ti] = CAPMinD[H][-1]
                COP_Max = COPMaxD[H][-1]
                COP_Min = COPMinD[H][-1]
            else:
                tB = -1
                for i in range(len(tDataD[H])-1):
                    if T_Outdoor[t] > tDataD[H][i+1] and T_Outdoor[t]<= tDataD[H][i] : tB = i
                if tB<0 :
                    pass    # shouldn't happen
                else:
                    # linear interpolation between the nearest reported points
                    frac = (T_Outdoor[t]-tDataD[H][tB])/float(tDataD[H][tB+1] - tDataD[H][tB])
                    COP_Max = COPMaxD[H][tB] + frac * (COPMaxD[H][tB+1] - COPMaxD[H][tB])
                    COP_Min = COPMinD[H][tB] + frac * (COPMinD[H][tB+1] - COPMinD[H][tB]) 
                    capacity_Max[ti] = CAPMaxD[H][tB] + frac * (CAPMaxD[H][tB+1] - CAPMaxD[H][tB])
                    capacity_Min[ti] = CAPMinD[H][tB] + frac * (CAPMinD[H][tB+1] - CAPMinD[H][tB])
            
            
        # calculate the average values of the above
        # Linear interpolation, doesn't work well
        # COP_Ave(t, h) = (Q_required(t) - capacity_Min(t, h)) * (COP_Max - COP_Min) / (capacity_Max(t, h) - capacity_Min(t, h)) + COP_Min          
        # Weighted average works better
#        c = (abs(Q_required[t] - capacity_Min[t]) * COP_Min + abs(Q_required[t] - capacity_Max[t]) * COP_Max)
        
        # Note times where the heat pump cannot meet demand
        if (Q_required[ti] > capacity_Max[ti]) :
            
            COP_Ave[ti] = COP_Max
            supplemental_Heat[ti] = Q_required[ti] - capacity_Max[ti]
            SuppUnitsByYear[Y] += supplemental_Heat[ti]/SuppHvacEfficiency/SuppEnergyContent
            
            # is this a new supplemental usage (within 24 hours of the past one)
            deltaTime = dateTime - supplementalLastDate
            if deltaTime>datetime.timedelta(1,0)  : #timeDelta(0,0,1,0,0)
                supplementalLastDate = dateTime
                SuppUsesByYear[Y] += 1
                
            # The amount of electricity required to heat the area with Q_required BTUs
            electric_Required[ti] = capacity_Max[ti] / COP_Ave[ti] /ENERGY_CONTENT_ELEC
            KWhByYear[Y] += electric_Required[ti]
        
        else:
            if (Q_required[ti] < capacity_Min[ti]):
                COP_Ave[ti] = COP_Min
            
            else:
                #Linear interpolation, doesn't work well
                #COP_Ave[t] = ((abs(Q_required[t] - capacity_Min[t]) * COP_Min + \
                #    abs(Q_required[t] - capacity_Max[t]) * COP_Max)) / abs(capacity_Max[t] - capacity_Min[t]) 
                COP_Ave[ti] = COP_Min + ((Q_required[ti] - capacity_Min[ti]) * (COP_Max - COP_Min)) / (capacity_Max[ti] - capacity_Min[ti]) 
                
            # The amount of electricity required to heat the area with Q_required BTUs
            electric_Required[ti] = Q_required[ti] / COP_Ave[ti]/ENERGY_CONTENT_ELEC     
            KWhByYear[Y] += electric_Required[ti]

        a = 1        
                
    #this could be a perfomance scale for heat pumps
    return 1
    
def outputData(HPiD):
    # This routine outputs all results to a text file
    global last_Purchase
    
    outputFile = './Output Data/Heat Pump Analysis.txt'
    output = open(outputFile,'w')
           
    output.write('Analysis for: '+part_Number[HPiD]['Manufacturer']+' Model '+part_Number[HPiD]['Model']+'\r')
    
    
    for tv in range(t_Start,t_End):
        t= tv-t_Start
    
        output.write(timeArray[t].ctime()+'\t{0:.2f}\t{1:f}\t{2:f}\t{3:f}\t{4:f}\n'.format(Q_required[t],electric_Required[t],supplemental_Heat[t], capacity_Max[t],COP_Ave[t]))
    
    output.close()
    
# initialization code
initializeData()
loadData()

# main routine 

app = HeatPumpPerformanceApp()
ani = animation.FuncAnimation(f,animate, interval=1000)
app.mainloop()
app.destroy()


