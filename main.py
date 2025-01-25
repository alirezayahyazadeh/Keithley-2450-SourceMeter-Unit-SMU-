from KeithleyDevice import Model2450
from general import suplemenaryFunctions as sf
from general.suplemenaryFunctions import fileManagement,Plots
from general import suplemenaryFunctions
import helperCLI as CLI

import pandas as pd
import time

print(sf.GenerateTimeDateString(separator='/',fillthegap=False))

print("bellow is a full list of connected devices to the system:\n",
      Model2450.__getAllResources__(),
      "\n----------------------\n\n")
# 4,9,17

#ResourceAddress = str(input('Please enter the GPIB/USB Address of the device: '))
ResourceAddress = 'USB0::0x05E6::0x2450::04586850::INSTR'

#Working Steps with the device
#1.Create an Object out of "KeithleyDeviceManager"
#2.Initialize the Object
#3.Run The Relevant Functions
#-------------------------------Test The Device Connectivity-----------------------------
KDM = Model2450.KeithleyDeviceManager(GPI_or_USB_Address=ResourceAddress,EstablishConnectionTest=False)
KDM.Initialize(Source_VoltageRange=20,
               Source_CurrentRange=0.95,
               Measure_VoltageRange=10,
               Measure_CurrentRange=0.95,
               Measure_ResistanceRange=None,
               NumberOfPowerCycle=0.1,
               Current_Limit=0.95,
               Voltage_limit=10,
               fourWireSensing=True,
              isActivateDefaultBuffer=True)


#KDM.SendVoltage_MeasureCurrent(MaxVoltageProtectionLimit=10,
#                               SourceLevel_Voltage=10)





#----------------------------------------------------------------------------------------
#KDM.SendVoltage_MeasureCurrent(MaxVoltageProtectionLimit=10, SourceLevel_Voltage=10)

print('Test Functions \n------------------------------\n')

a = CLI.MethodSelector()
#in shartaa ham ke zir gozashti enteghal bede be file helperCLI*************
# ******* Injoori file main ro sholoogh poloogh nakon
if a==1 :
    a='SendVoltage_MeasureCurrent'
    
    KDM.SendVoltage_MeasureCurrent(
       MaxVoltageProtectionLimit = None,   
          
      
      Voltage_Range=input('Voltage_Range='),
      VoltageLevel = input('VoltageLevel='),
      sourceLimit_i=input('s   urceLimit_i='),
      measure_Range=input('measure_Range='),
      use_measure_limits= input('use_measure_limits='),
      measure_limit_Low=input('use_measure_limits=-1e-01'),
      measure_Limit_high=input('use_measure_high=-3e-01,'),
      measure_Limit_beep_On_Limit_high_Exceeds=True,
      bufferName=None,
      showOutputasPrint=True,
                                  )
    
    result = KDM.ReturnBufferValues(bufferName=KDM.ActiveBuffer_Name)
    print(result,"----------------------------")
    
if a==2:
   a= "SendVoltageList_MeasureCurrents"
   print("SendVoltageList_MeasureCurrents")
   KDM.SendVoltageList_MeasureCurrents(MaxVoltageProtectionLimit = None,
                                   Voltage_Range=input('Voltage_Range='),
                                   VoltageLevelList = input('VoltageLevelList[1.,3.,5.,7.,8.,9.,10.,12.]='),
                                   sourceLimit_i=input('urceLimit_i='),
                                   measure_Range=input('measure_Range='),
                                   use_measure_limits=  input('use_measure_limits='),
                                   measure_limit_Low=input('use_measure_limits=ex(-1e-01)='),
                                   measure_Limit_high=input('use_measure_high=-ex(3e-01)='),
                                   measure_Limit_beep_On_Limit_high_Exceeds=True,
                                   bufferName=None,
                                   showOutputasPrint=True,
                                   delay=input("delay="))
#TO be Checked Later    
if a==3:
   a="SendCurrent_MeasureVoltage"
   print("SendCurrent_MeasureVoltage")
   KDM.SendCurrent_MeasureVoltage(MaxVoltageProtectionLimit = None,
                                   Current_Range =input("Current_Range="),
                                   CurrentLevel= input("CurrentLevel="),
                                   sourceLimit_v=input("sourceLimit_v="),
                                   measure_Range=input("measure_Range="),
                                   use_measure_limits= False,
                                   measure_limit_Low=input("measure_limit_Low="),
                                   measure_Limit_high=input("measure_Limit_high="),
                                   measure_Limit_beep_On_Limit_high_Exceeds=("measure_Limit_beep_On_Limit_high_Exceeds="),
                                   bufferName=None,
                                   showOutputasPrint=True,
                                  )
   
if a==4:   
   a="SendCurrentList_MeasureVoltages"
   print("SendCurrentList_MeasureVoltages")
   KDM.SendCurrentList_MeasureVoltages(MaxVoltageProtectionLimit = None,
                                   Current_Range =input("Current_Range="),
                                   CurrentLevelList= input("Current_Range=,[0.01,0.03,0.09,0.29,0.7]=="),
                                   sourceLimit_v=input("sourceLimit_v="),
                                   measure_Range=input("measure_Range="),
                                   use_measure_limits= False,
                                   measure_limit_Low=input("measure_limit_Low="),
                                   measure_Limit_high=input("measure_Limit_high="),
                                   measure_Limit_beep_On_Limit_high_Exceeds=False,
                                   bufferName='defbuffer1',  
                                   showOutputasPrint=True,
                                   delay=input("delay=")
                                  )

if a==5:
   a='SendCurrent_MeasureResistance'  
    
   
   KDM.Sweep_LinearcaseByPoints_SourceCurrent_MeasureVoltage_CalculateResistance(
                  ArbitraryConfigurationName='testConfig1',
                   startValue=input("startValue="),
                   stopValue=input("stopValue="),
                   pointsToMeasure=input("pointsToMeasure="),
                   delayTime=input("delayTime="),
                   Iterations=input("Iterations="),
                   dual='smu.OFF',
                   bufferName=None, )
   result = KDM.ReturnBufferValues(bufferName=KDM.ActiveBuffer_Name)
   print(result,"----------------------------")
   print("Sweep_LinearcaseByPoints_SourceVoltage_MeasureCurrent_CalculateResistance")
if a==6:
   a="SendVoltage_MeasureCurrent"
   print("SendVoltage_MeasureCurrent")
   KDM.SendVoltage_MeasureCurrent(MaxVoltageProtectionLimit = None,
                                   Voltage_Range=input('Voltage_Range='),
                                   VoltageLevel = input('VoltageLeve='),
                                   sourceLimit_i=input('sourceLimit_i='),
                                   measure_Range=input(' measure_Range='),
                                   use_measure_limits= input('use_measure_limits='),
                                   measure_limit_Low=input('measure_limit_Low='),
                                   measure_Limit_high=input('measure_Limit_high='),
                                   measure_Limit_beep_On_Limit_high_Exceeds=True,
                                   bufferName=None,
                                   showOutputasPrint=True,
                                  )   
if a==7:
   a="SendCurrent_MeasureVoltage_CalculateResistance"
   print()
   KDM.SendCurrent_MeasureVoltage_CalculateResistance(MaxVoltageProtectionLimit = None,
                                   Current_Range =input("Current_Range="),
                                   CurrentLevel=input(" CurrentLevel="),
                                   sourceLimit_v=input("sourceLimit_v="),
                                   measure_Range=input(' measure_Range='),
                                   use_measure_limits= input('use_measure_limits='),
                                   measure_limit_Low=input('measure_limit_Low='),
                                   measure_Limit_high=input('measure_Limit_high='),
                                   measure_Limit_beep_On_Limit_high_Exceeds=True,
                                   bufferName='defbuffer1',
                                   showOutputasPrint=True,
                                  )   
   
if a==8:
   a="SendVoltage_MeasureCurrent_CalculateResistance"
   print("SendVoltage_MeasureCurrent_CalculateResistance")
   KDM.SendVoltage_MeasureCurrent_CalculateResistance(MaxVoltageProtectionLimit = None,
                                   Voltage_Range=input('Voltage_Range='),
                                   VoltageLevel= input('VoltageLeve='),
                                   sourceLimit_i=input('sourceLimit_i='),
                                   measure_Range=input(' measure_Range='),
                                   use_measure_limits= input('use_measure_limits='),
                                   measure_limit_Low=input('measure_limit_Low='),
                                   measure_Limit_high=input('measure_Limit_high='),
                                   measure_Limit_beep_On_Limit_high_Exceeds=True,
                                   bufferName= None,
                                   showOutputasPrint=True,
                                  )

if a==9: 
    a="logarithmic_sweepcaseByPoints_Voltage"
   
    print("logarithmic_sweepcaseByPoints_Voltage")
    KDM.logarithmic_sweepcaseByPoints_Voltage(
         ArbitraryConfigurationName='testCo nfig1',
                    startValue=input("startValue="),
                    stopValue=input("stopValue="),
                    pointsToMeasure=input("pointsToMeasure="),
                    delayTime=input("delayTime="),
                    Iterations=input("Iterations="),
                    dual='smu.OFF',
                    bufferName=None,
                                    )     

if a==10:
    a="Sweep_LinearcaseByPoints_Voltage"
    print("Sweep_LinearcaseByPoints_Voltage")
    KDM.Sweep_LinearcaseByPoints_Voltage(
         ArbitraryConfigurationName='testConfig1',
                    startValue=-1,
                    stopValue=1,
                    pointsToMeasure=100,
                    delayTime=0.00005,
                    Iterations=1,
                    dual='smu.OFF',
                    bufferName=None,
   )   

if a==11 :  
    a="Sweep_LinearcaseByStep_Voltage" 
    print("Sweep_LinearcaseByStep_Voltage")
    KDM.Sweep_LinearcaseByStep_Voltage(
      ArbitraryConfigurationName='testConfig1',
                   startValue=0.1,
                   stopValue=0.9,
                   stepValue=0.3,
                   delayTime=0.01,
                   Iterations=1,
                   dual='smu.OFF',
                   bufferName=None, 
                                  ) 
    result = KDM.ReturnBufferValues(bufferName=KDM.ActiveBuffer_Name)
    print(result,"----------------------------")
    
   
if a==12:
   a="Sweep_LinearcaseByPoints_Current"
   print("Sweep_LinearcaseByPoints_Current")   
   KDM.Sweep_LinearcaseByPoints_Current(
                  ArbitraryConfigurationName='testConfig1',
                   startValue=0.005,
                   stopValue=0.02,
                   pointsToMeasure=13,
                   delayTime=0.01,
                   Iterations=1,
                   dual='smu.OFF',
                   bufferName=None, )
   result = KDM.ReturnBufferValues(bufferName=KDM.ActiveBuffer_Name)
   print(result,"----------------------------")
   
if a==13:
   a="Sweep_LinearcaseByStep_Current"  
   print("Sweep_LinearcaseByStep_Current") 
   KDM.Sweep_LinearcaseByStep_Current(
                  ArbitraryConfigurationName='testConfig1',
                   startValue=0.1,
                   stopValue=0.6,
                   stepValue=0.1,
                   delayTime=0.001,
                   Iterations=1,
                   dual='smu.OFF',
                   bufferName=None, )
   result = KDM.ReturnBufferValues(bufferName=KDM.ActiveBuffer_Name)
   print(result,"----------------------------")
   
if a==14:  
   a="Sweep_LinearcaseByPoints_SourceCurrent_MeasureResistance"
   print("Sweep_LinearcaseByPoints_SourceCurrent_MeasureResistance")  
   KDM.Sweep_LinearcaseByPoints_SourceCurrent_MeasureResistance(
                   ArbitraryConfigurationName='testConfig1',
                   startValue=0.1,
                   stopValue=0.9,
                   pointsToMeasure=7,
                   delayTime=0.001,
                   Iterations=1,
                   dual='smu.OFF',
                   bufferName=None, )
   result = KDM.ReturnBufferValues(bufferName=KDM.ActiveBuffer_Name)
   print(result,"----------------------------")
 
if a==15: 
   a="Sweep_LinearcaseByPoints_SourceCurrent_MeasureVoltage_CalculateResistance"
   print("Sweep_LinearcaseByPoints_SourceCurrent_MeasureVoltage_CalculateResistance")  
   KDM.Sweep_LinearcaseByPoints_SourceCurrent_MeasureVoltage_CalculateResistance(
                  ArbitraryConfigurationName='testConfig1',
                   startValue=0.1,
                   stopValue=0.9,
                   pointsToMeasure=7,
                   delayTime=0.001,
                   Iterations=1,
                   dual='smu.OFF',
                   bufferName=None, )
   result = KDM.ReturnBufferValues(bufferName=KDM.ActiveBuffer_Name)
   print(result,"----------------------------")
   
if a==16:   
   a="Sweep_LinearcaseByPoints_SourceVoltage_MeasureCurrent_CalculateResistance"
   print("Sweep_LinearcaseByPoints_SourceVoltage_MeasureCurrent_CalculateResistance")

   KDM.Sweep_LinearcaseByPoints_SourceVoltage_MeasureCurrent_CalculateResistance(
                  ArbitraryConfigurationName='testConfig1',
                   startValue=0.1,
                   stopValue=0.9,
                   pointsToMeasure=7,
                   delayTime=0.001,
                   Iterations=1,
                   dual='smu.OFF',
                   bufferName=None, )
   result = KDM.ReturnBufferValues(bufferName=KDM.ActiveBuffer_Name)
   print(result,"----------------------------")

if a==17:
   a="Sweep_Custom_SourceVoltage_MeasureCurrent"
   KDM.Sweep_Custom_SourceVoltage_MeasureCurrent(
                  source_Range=2,
                  measure_range=0.1,
                  Source_ListOfLevels=[0.00,0.09],
                  AribtraryConfigName="SweepList1",
                  startIndex=1,
                  delay=0.001,
                  count=1,
                  bufferName=None)  
 
'''   
if a==15:   
   print("Sweep_LinearcaseByPoints_SourceCurrent_MeasureVoltage_CalculateResistance")
   KDM.Sweep_LinearcaseByPoints_SourceCurrent_MeasureVoltage_CalculateResistance(
                  ArbitraryConfigurationName='testConfig1',
                   startValue=0.1,
                   stopValue=0.9,
                   pointsToMeasure=7,
                   delayTime=0.001,
                   Iterations=1,
                   dual='smu.OFF',
                   bufferName=None, )
'''
"""                   
if a==15 :                  
   KDM.SendVoltageList_MeasureCurrents(MaxVoltageProtectionLimit = None,
                                   Voltage_Range=None,
                                   VoltageLevelList = voltage_list,
                                   sourceLimit_i=None,
                                   measure_Range=None,
                                   use_measure_limits= False,
                                   measure_limit_Low=None,
                                   
                                   
                                   bufferName=None,
                                   showOutputasPrint=True,
                                   delay=0.001)
"""                                   
"""                                  
plt.TwinAxisPlot(commonAxisCaption='VoltageList_MeasureCurrents & Time Stamp LOG',
                       commonAxisData=result['timestamps'],
                       leftAxixCaption='source-Voltage logarimic',
                       leftAxisData=result['sourcevalues'],
                       rightAxisCaption='Measured-current logarimic',
                       rightAxisData=result['readings'],
                       title='VoltageList_MeasureCurrents logaritmic ',_plotType = 'line')
       


print("SendVoltageList_MeasureCurrents")
voltage_list = [-0.2,-0.19,-0.18,-0.17,-0.16,-0.15,-0.14,-0.13
,-0.12,-0.11,-0.1,-0.09,-0.08,-0.07,-0.06,-0.05,-0.04,-0.03,-0.02,-0.01,0.0,0.01,0.02,]
'''
#q=int(input('number='))
#if q==1:
"""


                                   
                                                                    
#else :
      
  #print('please choose currect number')    
result = KDM.ReturnBufferValues(bufferName=KDM.ActiveBuffer_Name)

print(result)

#result = pd.DataFrame(result)
#print(result)

#run this
#Sweeplog_ByPoints_Voltage

fm = fileManagement()
plt = Plots()
try:
      listOfJs = suplemenaryFunctions.calculat_J(listOfCurrents=result['readings'], cm2=0.1) 
      dic_to_Updaate = {'jvalues':listOfJs}
      result.update(dic_to_Updaate)
      
      listOfJs_log = suplemenaryFunctions.Calculate_Log(result['jvalues'])
      dic_to_Updaate = {'jvalues_log':listOfJs_log}
      result.update(dic_to_Updaate)
      
      log_readings = suplemenaryFunctions.Calculate_Log(result['readings'])
      dic_to_Updaate = {'readings_log':log_readings}
      result.update(dic_to_Updaate)
      
      log_sourcevalues = suplemenaryFunctions.Calculate_Log(result['sourcevalues'])
      dic_to_Updaate = {'sourcevalues_log':log_sourcevalues}
      result.update(dic_to_Updaate)
      
      fm.SaveToDrive(directoryPath='D:\\',inputList=result,filename='output' ,fileType='csv',WantAlsoALogFile=True,authorName='Alireza yahyazadeh',extraDescription=a)
      
      plt.Plot(title=a,
               X_AxisCaption='Source Voltage',
               X_AxisData=result['sourcevalues'],
               Y_AxixCaption='current',
               Y_AxisData= result['jvalues'],
      
               X_AxisCaption1='Source: Voltage - Log10',
               X_AxisData1=result['sourcevalues'],
               Y_AxixCaption1='Measure: Current - Log10',
               Y_AxisData1= result['jvalues_log'],
              
               )
      
      
except Exception as err:
      print(err)

#fm.SaveToDrive(_fullpath='D:\\result__',_inputList=result) 