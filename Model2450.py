import pyvisa as visa
from typing import List
import pandas as pd
import io
import time


class KeithleyDeviceManager(object):
    """
    Using the Model 2450, you can perform the following operations:
        • Source voltage and measure current, voltage, resistance, or power
        • Source current and measure voltage, current, resistance, or power
        • Measure voltage, current, resistance, or power
    """
        
    def __init__(self, GPI_or_USB_Address:str=None, EstablishConnectionTest:bool=False):
        """
        Gets the Physical Address (GPI or USB Address) of the Specified Device and Make an Object With Active Connection to The Device.
        The Address Sample is like: 'GPIB0::12::INSTR' or 'USB0::0x05F3::0x2AE2::01234560::INSTR'

        Set the EstablishConnectionTest to true to check if the device is connected to the running platform correctly.

        Args:
            GPI_or_USB_Address (str, optional): Gets the Device Port Address and make a connection. Defaults to None.
            EstablishConnectionTest (bool, optional): Tests if the device is connected by sending 3 beep commands to the device. It is possible to test device manually using the fuction TestDeviceConnection(). Defaults to False.
        """

        self.GPI_or_USB_Address = GPI_or_USB_Address
        self.Device = None

        self.resourceManager = visa.ResourceManager()
       
        #-----------------fields
        self.Source_VoltageRange:float = None
        self.Source_CurrentRange:float = None
        self.Measure_VoltageRange:float = None
        self.Measure_CurrentRange:float = None
        self.Measure_ResistanceRange:float = None
        self.Current_Limit:float = None
        self.Voltage_Limit:float = None
        self.nplc: float = None
        self.isFrontTerminalsActive:bool= None
        self.fourWireSensing:bool=  None
        self.isActivateDefaultBuffer:bool = None
        self.userDefinedBufferName:str = None
        self.userDefinedBufferCapacity:int = None
        self.ASCII_Percision:int = None
        self.isAutoZeroOnce:bool= None
        self.TurnAutoZeroOff:bool= None
        self.ActiveBuffer_Name:str=None
        self.ListOfAvailableBuffers = ['defbuffer1','defbuffer2']
        #-----------------------
        if(EstablishConnectionTest):
            try:
                self.Device = self.resourceManager.open_resource(self.GPI_or_USB_Address,send_end=False)
                if (self.Device is None):
                    self.Device = self.resourceManager.open_resource(self.GPI_or_USB_Address,send_end=False)

                #self.Device.write(f'smu.source.output = smu.ON') #Enables the Source Output. Beginnig of the Measurement.
                self.TestDeviceConnection()
                #self.Device.write(f'smu.source.output = smu.OFF') #Disables the Source Output. End Of the Measurement.

                print("Connection is Established ")
            except Exception as ex:
                print("Somthing went wrong during the connection's test process. The technical error is:\n", ex)
        
    def PrintAllResources(self):
        """
        Prints all a list of all the devices which are connected to the running system.
        """
        print(self.resourceManager.list_resources())
    #Test Function
    def TestDeviceConnection(self):
        """
        Its a manual test to see if the connection between the device and pyVisa is established or not. Makes the device to beep 3 times.
        """
        if (self.Device is None):
            self.Device = self.resourceManager.open_resource(self.GPI_or_USB_Address,send_end=False)
        try:
            #self.Device.write(f'smu.source.output = smu.ON') #Enables the Source Output. Beginnig of the Measurement.
            self.Device.write('beeper.beep(0.1, 2400)')
            self.Device.write('delay(0.500)')
            self.Device.write('beeper.beep(0.1, 2400)')
            self.Device.write('delay(0.500)')
            self.Device.write('beeper.beep(0.1, 2400)')
            
            #self.Device.write(f'smu.source.output = smu.OFF') #Disables the Source Output. End Of the Measurement.
        except Exception as ex:
            print("Error occured during the test of Connecntion to the Device. The technical information is: ",ex)
    #Global Settings    
    def Initialize(self,
                   Source_VoltageRange:float,
                   Source_CurrentRange:float,
                   Measure_VoltageRange:float,
                   Measure_CurrentRange:float,
                   Current_Limit:float,
                   Voltage_limit:float,
                   Measure_ResistanceRange:float=None,
                   NumberOfPowerCycle:float = None,
                   isFrontTerminalsActive:bool=True,
                   fourWireSensing:bool=True,
                   isActivateDefaultBuffer:bool = True,
                   userDefinedBufferName:str = None,
                   userDefinedBufferCapacity:int = 10000,
                   ASCII_Percision:int = 10,
                   isAutoZeroOnce:bool=True,
                   TurnAutoZeroOff:bool=False,
                   readBack:bool=True,
                   
                   ) -> None: 
        """
        The __init__ function makes an object out of this class. Some settings of the device can be set once and being used
        during the measurment process. These public properties are set at the phase of Initialization. To be controllable,
        the initializing phase is separated from __init__(), the constructor function, so it is more convenient to reset the
        setting whenever it is decided.

        Args:
            Source_VoltageRange (float): Source Voltage Range / Adjust the accuracy of the device's source voltage 
            Source_CurrentRange (float): Source Current Range / Adjust the accuracy of the device's source current
            
            Measure_VoltageRange (float): Measure Voltage Range / Adjust the accuracy of the device voltage measurement
            Measure_CurrentRange (float): Measure Current Range / Adjust the accuracy of the device current measurement
            
            NumberOfPowerCycle (float): You can adjust the amount of time that the input signal is measured.
            Adjustments to the amount of time affect the usable measurement resolution, the amount of reading noise, 
            and the reading rate of the instrument.
            e.g.  Each power line cycle for 60 Hz is 16.67 ms (1/60); for 50 Hz, it is 20 ms (1/50).
            
            fourWireSensing (bool, optional): If it is set to False, the device measures in the 2 wire sensing mode.
            Use 4-wire connections when you are concerned about voltage drops because of lead or contact 
            resistance that could affect measurement accuracy.
            You should use 4-wire, or remote sense, measurement techniques for the following conditions:
                • Low impedance applications
                • When sourcing high current
                • When sourcing low voltage
                • When sourcing higher current and measuring low voltages
                • When enforcing voltage limits directly at the device under test (DUT)
                • When sourcing or measuring voltage in low impedance (less than 100 Ω) test circuits
                • When optimizing the accuracy for low resistance, voltage source, or voltage measurements
            For example: 
            when testing low impedance devices (less than 100 Ω), usually a higher current is sourced and small 
            voltages are measured.
            Defaults to True.
            
            isActivateDefaultBuffer (bool, optional): New readings are stored in the active buffer by timestamp. 
            Note: The active buffer is cleared when the function is changed using the front panel. Also RESET command,
            clears the buffers.
            Defaults to True.

            isAutoZeroOnce (bool, optional):
            'Autozero' is a continuous or periodic process that adjusts measurements in real-time,
            while 'Autozero Once' is a one-time calibration that applies a fixed compensation for 
            the remainder of the measurement session. 
            Note: If the AutozeroOnce is set to False and TurnAutoZeroOff is False, the device will use the AutoZero callibration 
            which is a periodic callibration method for the measurements.
            Defaults to True.

            TurnAutoZeroOff (bool, optional): Turns AutoZero Calibration Off.
            'Autozero' is a continuous or periodic process that adjusts measurements in real-time,
            while 'Autozero Once' is a one-time calibration that applies a fixed compensation for 
            the remainder of the measurement session.
            Defaults to False.
        Returns:
            _type_: NONE

        """
        try:
            #Storing the values for the next steps
            self.Source_VoltageRange = Source_VoltageRange
            self.Source_CurrentRange = Source_CurrentRange
            self.Measure_VoltageRange = Measure_VoltageRange
            self.Measure_CurrentRange = Measure_CurrentRange
            self.Measure_ResistanceRange = Measure_ResistanceRange
            self.Current_Limit = Current_Limit
            self.Voltage_Limit = Voltage_limit
            self.nplc = NumberOfPowerCycle
            self.isFrontTerminalsActive=isFrontTerminalsActive
            self.fourWireSensing=fourWireSensing
            self.isActivateDefaultBuffer = isActivateDefaultBuffer
            self.userDefinedBufferName = userDefinedBufferName
            self.userDefinedBufferCapacity = userDefinedBufferCapacity
            self.ASCII_Percision = ASCII_Percision
            self.isAutoZeroOnce=isAutoZeroOnce
            self.TurnAutoZeroOff=TurnAutoZeroOff
            self.ActiveBuffer_Name=None
            self.readBack:bool=True
            if(self.Device is None):
                self.Device = self.resourceManager.open_resource(self.GPI_or_USB_Address,send_end=False)
            if(userDefinedBufferName is not None):
                self.__MakeUserDefinedBuffer(bufferName=self.userDefinedBufferName,
                                            bufferCapacity=userDefinedBufferCapacity)
            self.Device.timeout = None # default value is 25 and None means default value = 25 seconds
            #Reset and Setting the device
            self.__ResetAndSetUsersGeneralSettings()
        except Exception as ex:
            raise Exception(ex)

        """
        Extra Information:
        --Source configuration list settings:
                Front-panel setting SCPI-command & TSP-command Functions

                FUNCTION key
                :SOURce[1]:FUNCtion[:MODE] (on page 6-82)
                smu.source.func (on page 8-155)

                Auto range
                HOME > Source Range
                :SOURce[1]:<function>:RANGe:AUTO (on page 6-86)
                smu.source.autorange (on page 8-146)

                Delay
                MENU > Source > Settings > Source Delay
                :SOURce[1]:<function>:DELay (on page 6-76)
                smu.source.delay (on page 8-154)

                Auto delay
                Not available from the front panel
                :SOURce[1]:<function>:DELay:AUTO (on page 6-77)
                smu.source.autodelay (on page 8-147)
                
                Source level
                HOME > Source
                :SOURce[1]:<function>:<x>LIMit[:LEVel] (on page 6-81)
                smu.source.level (on page 8-156)
                
                Overvoltage protection
                MENU > Source > Settings > Overvoltage 
                
                Protection Limit
                :SOURce[1]:<function>:PROTection[:LEVel] (on page 6-
                83)
                smu.source.protect.level (on page 8-160)
               
                Output off state
                MENU > Source > Settings > Output Off State
                :OUTPut[1]:<function>:SMODe (on page 6-39)
                smu.source.offmode (on page 8-157)
               
                Range
                MENU > Source > Settings > Source Range
                :SOURce[1]:<function>:RANGe (on page 6-85)
                smu.source.range (on page 8-161)
                
                Limit
                HOME > Limit
                :SOURce[1]:<function>:<x>LIMit[:LEVel] (on page 6-81)
                smu.source.xlimit.level (on page 8-173)
                
                High capacitance
                MENU > Source > Settings > High Capacitance
                :SOURce[1]:<function>:HIGH:CAPacitance (on page 6-
                79)
                smu.source.highc (on page 8-156)
                
                Readback
                MENU > Source > Settings > Source Readback
                :SOURce[1]:<function>:READ:BACK (on page 6-87)
                smu.source.readback (on page 8-163)
                
                User delays
                Not available from the front panel
                :SOURce[1]:<function>:DELay:USER<n> (on page 6-78)
                smu.source.userdelay[N] (on page 8-172
        """
        
    def ReturnBufferValues(self,bufferName:str=None,return_type:int=2):
        """
        Reading buffers capture measurements, ranges, the output state of the instrument, and instrument 
        status. The Model 2450 has two default reading buffers. You can also create user-defined reading 
        buffers. In case you have created a user-defined buffer or you would like to use the second default buffer
        (the model 2450 has 2 default buffers named defbuffer1 and defbuffer2) of the device, pass 
        the buffer's specific name using the bufferName parameter. When it is set to None, the first
        default buffer will be read as the default buffer.
        Tips:
        When you create a reading buffer (user-defined buffer), that buffer becomes the active buffer until you 
        choose a different buffer => the device buffers/writes all the outputs into that specific buffer  
        
        Args:
            bufferName (str, optional): Gets the name of user-defined reading buffers 
            Defaults to None.
            return_type (str, optional): has different types. 1. AW: means as a whole 2. S: means separated. type 1 returns 1 string full of all datas separated by comma however type 2 returns a disctionary includes each column as a separated data. it is recommended that using the type 2.
        Note: In case you want to modify this method, please add an elif block into this method and make a dictionarz out of your requirements and return it as a return value. 
        Section 8: TSP command reference Model 2450 Interactive SourceMeter® Instrument Reference Manual
        8-96 2450-901-01 Rev. D / May 2015


        Attribute                               Description
        bufferName.readings                      The readings stored in a specified reading buffer.
        bufferName.dates                         The dates of readings stored in the reading buffer. 
        bufferName.statuses                      The status values of readings in the reading buffer.
        bufferName.formattedreadings             The stored readings formatted as they appear on the front-panel display.
        bufferName.sourceformattedvalues         The source levels formatted as they appear on the front-panel 
                                                display when the readings in the reading buffer were acquired. 
                                                See bufferVar.
        bufferName.sourcevalues                  The source levels that were being output when readings in the 
                                                reading buffer were acquired. See bufferVar.
        bufferName.sourcestatuses                The source status conditions of the instrument for the reading 
                                                point.
        bufferName.times                         The time when the instrument made the readings.
        bufferName.timestamps                    The timestamps of readings stored in the reading buffer.
        bufferName.relativetimestamps            The timestamps, in seconds, when each reading occurred 
                                                relative to the timestamp of reading buffer entry number 1.
        bufferName.sourceunits                   The units of measure of the source. See bufferVar.
        bufferName.seconds                       The nonfractional seconds portion of the timestamp when the 
                                                reading was stored in UTC format.
        bufferName.fractionalseconds             The fractional portion of the timestamp (in seconds) of when 
                                                each reading occurred. See bufferVar.fractionalseconds
        bufferName.units                         The unit of measure that is stored with readings in the reading 
                                                buffer.
        """
        if(bufferName is not None):
            self.Device.write('format.data = format.ASCII')
            self.Device.write(f'format.asciiprecision = {str(self.ASCII_Percision)}')
            dicOfDic = {}
            if(return_type == 1):
                commandstringSimple = f'printbuffer({bufferName}.startindex, {bufferName}.endindex, {bufferName}.readings, {bufferName}.units,  {bufferName}.relativetimestamps)'
                result = self.Device.query(commandstringSimple)
                return result
            elif(return_type == 2):
                
                commandstring = f'printbuffer({bufferName}.startindex, {bufferName}.endindex, {bufferName}.units)'
                result_units_readings = pd.read_csv(io.StringIO(self.Device.query(commandstring)),sep=',',header=None)
                commandstring2 = f'printbuffer({bufferName}.startindex, {bufferName}.endindex, {bufferName}.readings)'
                result_readings = pd.read_csv(io.StringIO(self.Device.query(commandstring2)),sep=',',header=None)
                commandstring3 = f'printbuffer({bufferName}.startindex, {bufferName}.endindex, {bufferName}.relativetimestamps)'
                result_timestamp = pd.read_csv(io.StringIO(self.Device.query(commandstring3)),sep=',',header=None)
                commandstring4 = f'printbuffer({bufferName}.startindex, {bufferName}.endindex, {bufferName}.sourcevalues)'
                result_sourcevalues = pd.read_csv(io.StringIO(self.Device.query(commandstring4)),sep=',',header=None)
                commandstring5 = f'printbuffer({bufferName}.startindex, {bufferName}.endindex, {bufferName}.sourceunits)'
                result_sourceunits = pd.read_csv(io.StringIO(self.Device.query(commandstring5)),sep=',',header=None)

                result = {'sourcevalues':result_sourcevalues.values[0].tolist(),
                          'sourceunits':result_sourceunits.values[0].tolist(),
                          'readings':result_readings.values[0].tolist(),
                          'units':result_units_readings.values[0].tolist(),
                          'timestamps':result_timestamp.values[0].tolist()}
                """
                result = {'sourcevalues':result_readings.values[0].tolist()}
                
                """
                return result
        
        """
        printbuffer()
        This function prints data from tables or reading buffer subtables.
            printbuffer(startIndex, endIndex, bufferVar)
            printbuffer(startIndex, endIndex, bufferVar, bufferVar2)
            printbuffer(startIndex, endIndex, bufferVar, ..., bufferVarN)
            
            .startIndex Beginning index of the buffer to print; this must be more than one
            and less than endIndex
            .endIndex Ending index of the buffer to print; this must be more than 
            startIndex and less than the index of the last entry in the tables
            .bufferVar Name of first table or reading buffer subtable to print; may be a 
            default buffer (defbuffer1 or defbuffer2) or a user-defined 
            buffer
            .bufferVar2 Second table or reading buffer subtable to print; may be a default 
            buffer (defbuffer1 or defbuffer2) or a user-defined buffer
            .bufferVarN The last table or reading buffer subtable to print; may be a default 
            buffer (defbuffer1 or defbuffer2) or a user-defined buffer
            ... One or more tables or reading buffer subtables separated with 
            commas

            Note: If startIndex is set to less than 1 or if endIndex is more than the size of the index, 9.910000e+37 
                  is returned for each value outside the allowed index and an event is generated.

            

        """
    def SaveDirectlyFromDevice(self, validAddressToSaveFile:str):
        #buffer.save()
        #buffer.saveappend()
        pass
        
    #set the user defined values specified when object is created
    def __ResetAndSetUsersGeneralSettings(self,BufferName_ToActivate:str=None):
        try:
            #Only Reset the Device In this Step
            self.Device.write('reset()')
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Connection is OK!")')
            self.__ResetTheConfigurations()
            #Activate the desired buffer
            self.__ActivateSpecificBuffer(BufferName_ToActivate)
            #This reset function, removes all user-defined buffers. So, the list should be regenerated.
            self.ListOfAvailableBuffers = ['defbuffer1','defbuffer2']
        except Exception as ex:
            raise Exception(ex)
    def __ResetTheConfigurations(self,):
        try:
            #Only Reset the Device In this Step
            self.Device.write('smu.reset()')
            #Automatic reference measurements
            if(self.TurnAutoZeroOff):
                self.Device.write('smu.measure.autozero.enable = smu.OFF')
            else:
                self.Device.write('smu.measure.autozero.enable = smu.ON')
            if(self.isFrontTerminalsActive):
                self.Device.write('smu.measure.terminals = smu.TERMINALS_FRONT')
            else:
                self.Device.write('smu.measure.terminals = smu.TERMINALS_REAR')
            if(self.isAutoZeroOnce):
                self.Device.write('smu.measure.autozero.once()')
            if(self.readBack):
                self.Device.write('smu.source.readback = smu.ON') # determines if the instrument records the measured source value or the configured source value when making a measurement
            self.Device.write('smu.measure.nplc=1')
            self.Device.write('tspnet.reset()')
        except Exception as ex:
            raise Exception(ex)
    #To Store the measurements inside a user-defined buffer
    def __MakeUserDefinedBuffer(self, bufferName:str='testBuffer1', bufferCapacity:int=100):
        """
        Buffer Capacity:
        -Standard: Store readings with full accuracy with formatting, maximum 6,875,000 readings.
        -Compact: Store readings with reduced accuracy (6.5 digits) with no formatting information, 
        1 μs accurate timestamp, maximum 27,500,000 readings. Once you store the first reading in 
        a compact buffer, you cannot change certain measurement settings, including range, display 
        digits, and units; you must clear the buffer first.
        -Full: Store the same information as standard, plus additional information.

        Args:
            bufferName (str, optional): The name of Buffer. Defaults to 'testBuffer1'.
            bufferCapacity (int, optional): How many readings the buffer have to hold. Defaults to 100.
        """
        try:
            self.Device.write(f'{bufferName} = buffer.make({str(bufferCapacity)})')
            self.ListOfAvailableBuffers.append(bufferName)
            self.ActiveBuffer_Name = bufferName
        except Exception as ex:
            raise Exception(ex)
    #To activate a determined buffer
    def __ActivateSpecificBuffer(self, bufferName:str=None,showBufferCapacity:bool=False):
        try:
            if(bufferName is not None):
                if(self.ListOfAvailableBuffers.count(bufferName) == 0):
                    raise Exception('The buffer name does not exists. Please Insert a valid name for user-defined Buffer. If it is not created yet, use MakeUserDefinedBuffer() function.')
                self.ActiveBuffer_Name = bufferName
            else:
                self.ActiveBuffer_Name = 'defbuffer1'
            #Activate the determined Buffer
            if(showBufferCapacity):
                capacity = self.Device.query(f'print({self.ActiveBuffer_Name}.capacity)') #To Activate a buffer, A buffer should be called once. So, This Line of code activates the current buffer.
                print(f'The capacity of the buffer <{self.ActiveBuffer_Name}> is {str(capacity)} readings')
        except Exception as ex:
            raise Exception(ex)
    #In case it is required to toggle between 4wire measurement and 2wire measurement
    def ChangeTerminals(self, 
                        ActiveRearChannels:bool = False,
                        ) ->None:
        """
        
        """
        try:
            if(ActiveRearChannels):
                self.Device.write('smu.measure.terminals = smu.TERMINALS_REAR')
            else:
                self.Device.write('smu.measure.terminals = smu.TERMINALS_FRONT')
        except Exception as ex:
            raise Exception(ex)
    
    #----------------Configuration-------------------------------
    """
    Instrument configuration:
    .An instrument configuration is a collection of settings that can be applied to the instrument.
        Active setting
    .At any given time, the instrument is operating using its active settings. For example, if you set the 
        measure NPLC to 1.0, the active NPLC setting is 1.0.
        Active state
    .At any given time, the complete set of active settings of the instrument is the active state. These 
        active settings can be subdivided into the following groups:
        • Measure settings
        • Source settings
        • General settings



    NOTE:
        To set the limit when sourcing current, send the commands:
        smu.source.func = smu.FUNC_DC_CURRENT
        smu.source.vlimit.level = limitValue
        To set the limit when sourcing voltage, send the commands:
        smu.source.func = smu.FUNC_DC_VOLTAGE
        smu.source.ilimit.level = limitValue
    """
    #------------------------------------------------------------

    #----------------Mesurement Functions------------------------
    #Measurement Function -> Send Voltage, Gets Current  
    def SendVoltage_MeasureCurrent(self,
                                   MaxVoltageProtectionLimit:int = None,
                                   Voltage_Range:float=None,
                                   VoltageLevel:float = 2,
                                   sourceLimit_i:float=None,
                                   measure_Range:float=None,
                                   use_measure_limits= False,
                                   measure_limit_Low:float=None,
                                   measure_Limit_high:float=None,
                                   measure_Limit_beep_On_Limit_high_Exceeds:bool=False,
                                   bufferName:str=None,
                                   showOutputasPrint:bool=False,
                                   ) -> List[float]:
        """
        Args:
            SourceLevel_Voltage (float): _description_
            MaxVoltageProtectionLimit (int, optional): _description_. Defaults to None.

        Returns:
            List[float]: _description_


        NOTE: MEASURE RANGE\n
        *The measure range determines the full-scale measurement span that is applied to the signal. 
        Therefore, it affects both the accuracy of the measurements and the maximum signal that can be 
        measured.\n
        *A change to the measure range can cause a change to the related current or voltage limit. When this 
        occurs, an event message is generated.\n
        *The total range is 22 W; no combination of voltage and current ranges can exceed 22 W. For 
        example, with a 200 V source range, the highest current measure range is 100 mA (200 V * 100 mA = 
        20 W).\n
        *Whether or not you can select a measure range is affected by other settings on the instrument. You 
        can only select a measure range if you are sourcing one type of measurement and measuring 
        another. For example, you can select a measure range if you are sourcing voltage and measuring 
        current. However, if you are sourcing voltage and measuring voltage, the measure range is the same
        as the source range and cannot be changed.\n

        NOTE: SOURCE RANGE\n
        The fixed current source ranges are 10 nA, 100 nA, 1 µA, 10 µA, 100 µA, 1 mA, 10 mA, 100 mA, and \n
        1 A.\n
        The fixed voltage source ranges are 20 mV, 200 mV, 2 V, 20 V, and 200 V.
        When you read this value, the instrument returns the positive full-scale value that the instrument is 
        presently using.\n
        This command is intended to eliminate the time required by the automatic range selection.
        To select the range, you can specify the approximate source value that you will use. The instrument 
        selects the lowest range that can accommodate that level. For example, if you expect to source levels 
        around 50 mV, send 0.05 (or 50e-3) to select the 200 mV range.\n

        NOTE: OVERVOLTAGE PROTECTION\n
        Overvoltage protection restricts the maximum voltage level that the instrument can source. It is in 
        effect when either current or voltage is sourced.
        This protection is in effect for both positive and negative output voltages.
        When this attribute is used in a test sequence, it should be set before turning the source on.\n
        ***The overvoltage protection only take a value out of a fixed and predefined voltages as: 2V, 5V, 10V, 
        20V, 40V, 60V, 80V, 100V, 120V, 140V, 160V, 180V, or NONE\n

        NOTE: LIMITS:\n
        *The values that can be set for this command are limited by the setting for the overvoltage protection 
        limit.\n
        *This value can also be limited by the measurement range. If a specific measurement range is set, the 
        limit must be more than 0.1 % of the measurement range and less than or equal to the maximum value of the
        measurement range. If you set the measurement range to be automatically selected, the measurement range 
        does not affect the limit.\n
        *If you change the <source range> to a level that is not appropriate for this limit, the instrument changes 
        the source limit to a limit that is appropriate to the range and a warning is generated.\n
        *Limits are absolute values.

        """
        try:
            #Check if the Protection Limit is Valid.
            listOfAllowedProtectionLimitVoltages = [2,5,10,20,40,60,80,100,120,140,160,180]
            if(MaxVoltageProtectionLimit is not None):
                if (listOfAllowedProtectionLimitVoltages.count(MaxVoltageProtectionLimit) < 1):
                    print(f'The MaxVoltageProtectionLimit can be one of these values: 2,5,10,20,40,60,80,100,120,140,160,180. The current value is {MaxVoltageProtectionLimit} and is not Valid.')
                    return None
            if(bufferName is not None):
                self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.Device.write('trigger.model.delay()')
            #Measurement Conditions
            if(measure_Range is None):
                measure_Range = self.Measure_CurrentRange
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            if(use_measure_limits):
                if((measure_limit_Low is None) or (measure_Limit_high is None)):
                    raise Exception('Error on not inserting adequate inputs. Please Insert Limit_low and Limit_High values to set the boundries and run the function again.')
                self.Device.write(f'smu.measure.limit[1].clear()')
                self.Device.write(f'smu.measure.limit[1].autoclear = smu.OFF')
                self.Device.write(f'smu.measure.limit[1].low.value = {measure_limit_Low}')
                self.Device.write(f'smu.measure.limit[1].high.value = {measure_Limit_high}')
                if(measure_Limit_beep_On_Limit_high_Exceeds):
                    self.Device.write(f'smu.measure.limit[1].audible = smu.AUDIBLE_FAIL')
                self.Device.write(f'smu.measure.limit[1].enable = smu.ON')
            #Sourcing Conditions
            self.Device.write(f'smu.source.func = smu.FUNC_DC_VOLTAGE')
            if(Voltage_Range is None):
                Voltage_Range = self.Source_VoltageRange
            self.Device.write(f'smu.source.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.range = {measure_Range}')
            #-----------------------------------------------------------
            self.Device.write(f'smu.source.range = {Voltage_Range}')
            if(MaxVoltageProtectionLimit is not None):
                self.Device.write(f'smu.source.protect.level = smu.PROTECT_{MaxVoltageProtectionLimit}V')
            if(VoltageLevel is not None):
                self.Device.write(f'smu.source.level = {VoltageLevel}')
            if(sourceLimit_i is not None):
                self.Device.write(f'smu.source.ilimit.level = {sourceLimit_i}')
            self.Device.write(f'smu.source.output = smu.ON') #Enables the Source Output. Beginnig of the Measurement.
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            self.Device.write(f'smu.measure.read({self.ActiveBuffer_Name})')
            self.Device.write(f'smu.source.output = smu.OFF') #Disables the Source Output. End Of the Measurement.
            #---------------------------------------------------Show in the output------------------------------
            if(showOutputasPrint):
                print(f"source voltage Range: {Voltage_Range}")
                print(f"Measured Current:")
                result = self.ReturnBufferValues(bufferName=self.ActiveBuffer_Name)
                print(result)
            #-------------------------------------------------------------------------------------------------------

        except Exception as ex:
            raise Exception(ex)
    def SendVoltageList_MeasureCurrents(self,
                                   MaxVoltageProtectionLimit:int = None,
                                   Voltage_Range:float=None,
                                   VoltageLevelList:List[float] = [0.2],
                                   sourceLimit_i:float=None,
                                   measure_Range:float=None,
                                   use_measure_limits= False,
                                   measure_limit_Low:float=None,
                                   measure_Limit_high:float=None,
                                   measure_Limit_beep_On_Limit_high_Exceeds:bool=False,
                                   bufferName:str=None,
                                   showOutputasPrint:bool=False,
                                   delay:float=0.01,
                                   ) -> List[float]:
        """
        Args:
            SourceLevel_Voltage (float): _description_
            MaxVoltageProtectionLimit (int, optional): _description_. Defaults to None.

        Returns:
            List[float]: _description_


        NOTE: MEASURE RANGE\n
        *The measure range determines the full-scale measurement span that is applied to the signal. 
        Therefore, it affects both the accuracy of the measurements and the maximum signal that can be 
        measured.\n
        *A change to the measure range can cause a change to the related current or voltage limit. When this 
        occurs, an event message is generated.\n
        *The total range is 22 W; no combination of voltage and current ranges can exceed 22 W. For 
        example, with a 200 V source range, the highest current measure range is 100 mA (200 V * 100 mA = 
        20 W).\n
        *Whether or not you can select a measure range is affected by other settings on the instrument. You 
        can only select a measure range if you are sourcing one type of measurement and measuring 
        another. For example, you can select a measure range if you are sourcing voltage and measuring 
        current. However, if you are sourcing voltage and measuring voltage, the measure range is the same
        as the source range and cannot be changed.\n

        NOTE: SOURCE RANGE\n
        The fixed current source ranges are 10 nA, 100 nA, 1 µA, 10 µA, 100 µA, 1 mA, 10 mA, 100 mA, and \n
        1 A.\n
        The fixed voltage source ranges are 20 mV, 200 mV, 2 V, 20 V, and 200 V.
        When you read this value, the instrument returns the positive full-scale value that the instrument is 
        presently using.\n
        This command is intended to eliminate the time required by the automatic range selection.
        To select the range, you can specify the approximate source value that you will use. The instrument 
        selects the lowest range that can accommodate that level. For example, if you expect to source levels 
        around 50 mV, send 0.05 (or 50e-3) to select the 200 mV range.\n

        NOTE: OVERVOLTAGE PROTECTION\n
        Overvoltage protection restricts the maximum voltage level that the instrument can source. It is in 
        effect when either current or voltage is sourced.
        This protection is in effect for both positive and negative output voltages.
        When this attribute is used in a test sequence, it should be set before turning the source on.\n
        ***The overvoltage protection only take a value out of a fixed and predefined voltages as: 2V, 5V, 10V, 
        20V, 40V, 60V, 80V, 100V, 120V, 140V, 160V, 180V, or NONE\n

        NOTE: LIMITS:\n
        *The values that can be set for this command are limited by the setting for the overvoltage protection 
        limit.\n
        *This value can also be limited by the measurement range. If a specific measurement range is set, the 
        limit must be more than 0.1 % of the measurement range and less than or equal to the maximum value of the
        measurement range. If you set the measurement range to be automatically selected, the measurement range 
        does not affect the limit.\n
        *If you change the <source range> to a level that is not appropriate for this limit, the instrument changes 
        the source limit to a limit that is appropriate to the range and a warning is generated.\n
        *Limits are absolute values.

        """
        try:
            #Check if the Protection Limit is Valid.
            listOfAllowedProtectionLimitVoltages = [2,5,10,20,40,60,80,100,120,140,160,180]
            if(MaxVoltageProtectionLimit is not None):
                if (listOfAllowedProtectionLimitVoltages.count(MaxVoltageProtectionLimit) < 1):
                    print(f'The MaxVoltageProtectionLimit can be one of these values: 2,5,10,20,40,60,80,100,120,140,160,180. The current value is {MaxVoltageProtectionLimit} and is not Valid.')
                    return None
            if(bufferName is not None):
                self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.Device.write('trigger.model.delay()')
            #Measurement Conditions
            if(measure_Range is None):
                measure_Range = self.Measure_CurrentRange
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            if(use_measure_limits):
                if((measure_limit_Low is None) or (measure_Limit_high is None)):
                    raise Exception('Error on not inserting adequate inputs. Please Insert Limit_low and Limit_High values to set the boundries and run the function again.')
                self.Device.write(f'smu.measure.limit[1].clear()')
                self.Device.write(f'smu.measure.limit[1].autoclear = smu.OFF')
                self.Device.write(f'smu.measure.limit[1].low.value = {measure_limit_Low}')
                self.Device.write(f'smu.measure.limit[1].high.value = {measure_Limit_high}')
                if(measure_Limit_beep_On_Limit_high_Exceeds):
                    self.Device.write(f'smu.measure.limit[1].audible = smu.AUDIBLE_FAIL')
                self.Device.write(f'smu.measure.limit[1].enable = smu.ON')
            #Sourcing Conditions
            if(Voltage_Range is None):
                Voltage_Range = self.Source_VoltageRange
            self.Device.write(f'smu.source.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.range = {measure_Range}')
            #-----------------------------------------------------------
            self.Device.write(f'smu.source.range = {Voltage_Range}')
            if(MaxVoltageProtectionLimit is not None):
                self.Device.write(f'smu.source.protect.level = smu.PROTECT_{MaxVoltageProtectionLimit}V')
            if(sourceLimit_i is not None):
                self.Device.write(f'smu.source.ilimit.level = {sourceLimit_i}')
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            
            self.Device.write(f'smu.source.output = smu.ON') #Enables the Source Output. Beginnig of the Measurement.
            if(len(VoltageLevelList) > 0):
                for VoltageLevel in VoltageLevelList:
                    self.Device.write(f'smu.source.level = {VoltageLevel}')
                    self.Device.write(f'smu.measure.read({self.ActiveBuffer_Name})')
                    self.Device.write(f'delay({str(delay)})')
            self.Device.write(f'smu.source.output = smu.OFF') #Disables the Source Output. End Of the Measurement.
            
            #---------------------------------------------------Show in the output------------------------------
            if(showOutputasPrint):
                print(f"source voltage Range: {Voltage_Range}")
                print(f"Measured Current:")
                result = self.ReturnBufferValues(bufferName=self.ActiveBuffer_Name)
                print(result)
            #-------------------------------------------------------------------------------------------------------

        except Exception as ex:
            raise Exception(ex)
    #Measurement Function -> Send Current, Gets Voltage 
    def SendCurrent_MeasureVoltage(self,
                                   MaxVoltageProtectionLimit:int = None,
                                   Current_Range:float=None,
                                   CurrentLevel:float = 2,
                                   sourceLimit_v:float=None,
                                   measure_Range:float=None,
                                   use_measure_limits= False,
                                   measure_limit_Low:float=None,
                                   measure_Limit_high:float=None,
                                   measure_Limit_beep_On_Limit_high_Exceeds:bool=False,
                                   bufferName:str=None,
                                   showOutputasPrint:bool=False,
                                   ) -> List[float]:
        """
        Args:
            SourceLevel_Voltage (float): _description_
            MaxVoltageProtectionLimit (int, optional): _description_. Defaults to None.

        Returns:
            List[float]: _description_


        NOTE: MEASURE RANGE\n
        *The measure range determines the full-scale measurement span that is applied to the signal. 
        Therefore, it affects both the accuracy of the measurements and the maximum signal that can be 
        measured.\n
        *A change to the measure range can cause a change to the related current or voltage limit. When this 
        occurs, an event message is generated.\n
        *The total range is 22 W; no combination of voltage and current ranges can exceed 22 W. For 
        example, with a 200 V source range, the highest current measure range is 100 mA (200 V * 100 mA = 
        20 W).\n
        *Whether or not you can select a measure range is affected by other settings on the instrument. You 
        can only select a measure range if you are sourcing one type of measurement and measuring 
        another. For example, you can select a measure range if you are sourcing voltage and measuring 
        current. However, if you are sourcing voltage and measuring voltage, the measure range is the same
        as the source range and cannot be changed.\n

        NOTE: SOURCE RANGE\n
        The fixed current source ranges are 10 nA, 100 nA, 1 µA, 10 µA, 100 µA, 1 mA, 10 mA, 100 mA, and \n
        1 A.\n
        The fixed voltage source ranges are 20 mV, 200 mV, 2 V, 20 V, and 200 V.
        When you read this value, the instrument returns the positive full-scale value that the instrument is 
        presently using.\n
        This command is intended to eliminate the time required by the automatic range selection.
        To select the range, you can specify the approximate source value that you will use. The instrument 
        selects the lowest range that can accommodate that level. For example, if you expect to source levels 
        around 50 mV, send 0.05 (or 50e-3) to select the 200 mV range.\n

        NOTE: OVERVOLTAGE PROTECTION\n
        Overvoltage protection restricts the maximum voltage level that the instrument can source. It is in 
        effect when either current or voltage is sourced.
        This protection is in effect for both positive and negative output voltages.
        When this attribute is used in a test sequence, it should be set before turning the source on.\n
        ***The overvoltage protection only take a value out of a fixed and predefined voltages as: 2V, 5V, 10V, 
        20V, 40V, 60V, 80V, 100V, 120V, 140V, 160V, 180V, or NONE\n

        NOTE: LIMITS:\n
        *The values that can be set for this command are limited by the setting for the overvoltage protection 
        limit.\n
        *This value can also be limited by the measurement range. If a specific measurement range is set, the 
        limit must be more than 0.1 % of the measurement range and less than or equal to the maximum value of the
        measurement range. If you set the measurement range to be automatically selected, the measurement range 
        does not affect the limit.\n
        *If you change the <source range> to a level that is not appropriate for this limit, the instrument changes 
        the source limit to a limit that is appropriate to the range and a warning is generated.\n
        *Limits are absolute values.

        """
        try:
            #Check if the Protection Limit is Valid.
            listOfAllowedProtectionLimitVoltages = [2,5,10,20,40,60,80,100,120,140,160,180]
            if(MaxVoltageProtectionLimit is not None):
                if (listOfAllowedProtectionLimitVoltages.count(MaxVoltageProtectionLimit) < 1):
                    print(f'The MaxVoltageProtectionLimit can be one of these values: 2,5,10,20,40,60,80,100,120,140,160,180. The current value is {MaxVoltageProtectionLimit} and is not Valid.')
                    return None
            if(bufferName is not None):
                self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.Device.write('trigger.model.delay()')
            #Measurement Conditions
            if(measure_Range is None):
                measure_Range = self.Measure_VoltageRange
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            if(use_measure_limits):
                if((measure_limit_Low is None) or (measure_Limit_high is None)):
                    raise Exception('Error on not inserting adequate inputs. Please Insert Limit_low and Limit_High values to set the boundries and run the function again.')
                self.Device.write(f'smu.measure.limit[1].clear()')
                self.Device.write(f'smu.measure.limit[1].autoclear = smu.OFF')
                self.Device.write(f'smu.measure.limit[1].low.value = {measure_limit_Low}')
                self.Device.write(f'smu.measure.limit[1].high.value = {measure_Limit_high}')
                if(measure_Limit_beep_On_Limit_high_Exceeds):
                    self.Device.write(f'smu.measure.limit[1].audible = smu.AUDIBLE_FAIL')
                self.Device.write(f'smu.measure.limit[1].enable = smu.ON')
            #Sourcing Conditions
            if(Current_Range is None):
                Current_Range = self.Source_CurrentRange
            self.Device.write(f'smu.source.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.range = {measure_Range}')
            #-----------------------------------------------------------
            self.Device.write(f'smu.source.range = {Current_Range}')
            if(MaxVoltageProtectionLimit is not None):
                self.Device.write(f'smu.source.protect.level = smu.PROTECT_{MaxVoltageProtectionLimit}V')
            if(CurrentLevel is not None):
                self.Device.write(f'smu.source.level = {CurrentLevel}')
            if(sourceLimit_v is not None):
                self.Device.write(f'smu.source.vlimit.level = {sourceLimit_v}')
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            self.Device.write(f'smu.source.output = smu.ON') #Enables the Source Output. Beginnig of the Measurement.
            self.Device.write(f'smu.measure.read({self.ActiveBuffer_Name})')
            self.Device.write(f'smu.source.output = smu.OFF') #Disables the Source Output. End Of the Measurement.
            #---------------------------------------------------Show in the output------------------------------
            if(showOutputasPrint):
                print(f"source current Range: {Current_Range}")
                print(f"Measured Voltage:")
                result = self.ReturnBufferValues(bufferName=self.ActiveBuffer_Name)
                print(result)
            #-------------------------------------------------------------------------------------------------------

        except Exception as ex:
            raise Exception(ex)
    def SendCurrentList_MeasureVoltages(self,
                                   MaxVoltageProtectionLimit:int = None,
                                   Current_Range:float=None,
                                   CurrentLevelList:List[float] = [0.01],
                                   sourceLimit_v:float=None,
                                   measure_Range:float=None,
                                   use_measure_limits= False,
                                   measure_limit_Low:float=None,
                                   measure_Limit_high:float=None,
                                   measure_Limit_beep_On_Limit_high_Exceeds:bool=False,
                                   bufferName:str=None,
                                   showOutputasPrint:bool=False,
                                   delay:float = 0.01,
                                   ) -> List[float]:
        """
        Args:
            SourceLevel_Voltage (float): _description_
            MaxVoltageProtectionLimit (int, optional): _description_. Defaults to None.

        Returns:
            List[float]: _description_


        NOTE: MEASURE RANGE\n
        *The measure range determines the full-scale measurement span that is applied to the signal. 
        Therefore, it affects both the accuracy of the measurements and the maximum signal that can be 
        measured.\n
        *A change to the measure range can cause a change to the related current or voltage limit. When this 
        occurs, an event message is generated.\n
        *The total range is 22 W; no combination of voltage and current ranges can exceed 22 W. For 
        example, with a 200 V source range, the highest current measure range is 100 mA (200 V * 100 mA = 
        20 W).\n
        *Whether or not you can select a measure range is affected by other settings on the instrument. You 
        can only select a measure range if you are sourcing one type of measurement and measuring 
        another. For example, you can select a measure range if you are sourcing voltage and measuring 
        current. However, if you are sourcing voltage and measuring voltage, the measure range is the same
        as the source range and cannot be changed.\n

        NOTE: SOURCE RANGE\n
        The fixed current source ranges are 10 nA, 100 nA, 1 µA, 10 µA, 100 µA, 1 mA, 10 mA, 100 mA, and \n
        1 A.\n
        The fixed voltage source ranges are 20 mV, 200 mV, 2 V, 20 V, and 200 V.
        When you read this value, the instrument returns the positive full-scale value that the instrument is 
        presently using.\n
        This command is intended to eliminate the time required by the automatic range selection.
        To select the range, you can specify the approximate source value that you will use. The instrument 
        selects the lowest range that can accommodate that level. For example, if you expect to source levels 
        around 50 mV, send 0.05 (or 50e-3) to select the 200 mV range.\n

        NOTE: OVERVOLTAGE PROTECTION\n
        Overvoltage protection restricts the maximum voltage level that the instrument can source. It is in 
        effect when either current or voltage is sourced.
        This protection is in effect for both positive and negative output voltages.
        When this attribute is used in a test sequence, it should be set before turning the source on.\n
        ***The overvoltage protection only take a value out of a fixed and predefined voltages as: 2V, 5V, 10V, 
        20V, 40V, 60V, 80V, 100V, 120V, 140V, 160V, 180V, or NONE\n

        NOTE: LIMITS:\n
        *The values that can be set for this command are limited by the setting for the overvoltage protection 
        limit.\n
        *This value can also be limited by the measurement range. If a specific measurement range is set, the 
        limit must be more than 0.1 % of the measurement range and less than or equal to the maximum value of the
        measurement range. If you set the measurement range to be automatically selected, the measurement range 
        does not affect the limit.\n
        *If you change the <source range> to a level that is not appropriate for this limit, the instrument changes 
        the source limit to a limit that is appropriate to the range and a warning is generated.\n
        *Limits are absolute values.

        """
        try:
            #Check if the Protection Limit is Valid.
            listOfAllowedProtectionLimitVoltages = [2,5,10,20,40,60,80,100,120,140,160,180]
            if(MaxVoltageProtectionLimit is not None):
                if (listOfAllowedProtectionLimitVoltages.count(MaxVoltageProtectionLimit) < 1):
                    print(f'The MaxVoltageProtectionLimit can be one of these values: 2,5,10,20,40,60,80,100,120,140,160,180. The current value is {MaxVoltageProtectionLimit} and is not Valid.')
                    return None
            if(bufferName is not None):
                self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            #self.Device.write('trigger.model.delay()')
            #Measurement Conditions
            if(measure_Range is None):
                measure_Range = self.Measure_VoltageRange
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            if(use_measure_limits):
                if((measure_limit_Low is None) or (measure_Limit_high is None)):
                    raise Exception('Error on not inserting adequate inputs. Please Insert Limit_low and Limit_High values to set the boundries and run the function again.')
                self.Device.write(f'smu.measure.limit[1].clear()')
                self.Device.write(f'smu.measure.limit[1].autoclear = smu.OFF')
                self.Device.write(f'smu.measure.limit[1].low.value = {measure_limit_Low}')
                self.Device.write(f'smu.measure.limit[1].high.value = {measure_Limit_high}')
                if(measure_Limit_beep_On_Limit_high_Exceeds):
                    self.Device.write(f'smu.measure.limit[1].audible = smu.AUDIBLE_FAIL')
                self.Device.write(f'smu.measure.limit[1].enable = smu.ON')
            #Sourcing Conditions
            if(Current_Range is None):
                Current_Range = self.Source_CurrentRange
            self.Device.write(f'smu.source.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.range = {measure_Range}')
            #-----------------------------------------------------------
            self.Device.write(f'smu.source.range = {Current_Range}')
            if(MaxVoltageProtectionLimit is not None):
                self.Device.write(f'smu.source.protect.level = smu.PROTECT_{MaxVoltageProtectionLimit}V')
                
            if(sourceLimit_v is not None):
                self.Device.write(f'smu.source.vlimit.level = {sourceLimit_v}')
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            
            self.Device.write(f'smu.source.output = smu.ON') #Enables the Source Output. Beginnig of the Measurement.
            if(len(CurrentLevelList) > 0):
                for CurrentLevel in CurrentLevelList:
                    self.Device.write(f'smu.source.level = {CurrentLevel}')
                    self.Device.write(f'smu.measure.read({self.ActiveBuffer_Name})')
                    self.Device.write(f'delay({str(delay)})')
            self.Device.write(f'smu.source.output = smu.OFF') #Disables the Source Output. End Of the Measurement.
            #---------------------------------------------------Show in the output------------------------------
            if(showOutputasPrint):
                print(f"source current Range: {Current_Range}")
                print(f"Measured Voltage:")
                result = self.ReturnBufferValues(bufferName=self.ActiveBuffer_Name)
                print(result)
            #-------------------------------------------------------------------------------------------------------

        except Exception as ex:
            raise Exception(ex)
    #Measurement Function -> Send Current, Gets Resitance
    def SendCurrent_MeasureResistance(self,
                                   MaxVoltageProtectionLimit:int = None,
                                   Current_Range:float=None,
                                   CurrentLevel:float = 2,
                                   sourceLimit_v:float=None,
                                   measure_Range:float=None,
                                   use_measure_limits= False,
                                   measure_limit_Low:float=None,
                                   measure_Limit_high:float=None,
                                   measure_Limit_beep_On_Limit_high_Exceeds:bool=False,
                                   bufferName:str=None,
                                   showOutputasPrint:bool=False,
                                   ):
        try:
            #Check if the Protection Limit is Valid.
            listOfAllowedProtectionLimitVoltages = [2,5,10,20,40,60,80,100,120,140,160,180]
            if(MaxVoltageProtectionLimit is not None):
                if (listOfAllowedProtectionLimitVoltages.count(MaxVoltageProtectionLimit) < 1):
                    print(f'The MaxVoltageProtectionLimit can be one of these values: 2,5,10,20,40,60,80,100,120,140,160,180. The current value is {MaxVoltageProtectionLimit} and is not Valid.')
                    return None
            if(bufferName is not None):
                self.__ActivateSpecificBuffer(bufferName=bufferName)
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Send C - Measure R")')
            self.Device.write('display.settext(display.TEXT2, "OneTime Measurement")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            #Measurement Conditions
            if(measure_Range is None):
                measure_Range = self.Measure_ResistanceRange
            self.Device.write(f'smu.measure.func = smu.FUNC_RESISTANCE')
            #???????????????????????????????????
            if(self.fourWireSensing):
                self.Device.write(f'smu.measure.offsetcompensation = smu.ON')
            #---> measure.range will always set after source.func is set
            if(use_measure_limits):
                if((measure_limit_Low is None) or (measure_Limit_high is None)):
                    raise Exception('Error on not inserting adequate inputs. Please Insert Limit_low and Limit_High values to set the boundries and run the function again.')
                self.Device.write(f'smu.measure.limit[1].clear()')
                self.Device.write(f'smu.measure.limit[1].autoclear = smu.OFF')
                self.Device.write(f'smu.measure.limit[1].low.value = {measure_limit_Low}')
                self.Device.write(f'smu.measure.limit[1].high.value = {measure_Limit_high}')
                if(measure_Limit_beep_On_Limit_high_Exceeds):
                    self.Device.write(f'smu.measure.limit[1].audible = smu.AUDIBLE_FAIL')
                self.Device.write(f'smu.measure.limit[1].enable = smu.ON')
            #Sourcing Conditions
            if(Current_Range is None):
                Current_Range = self.Source_CurrentRange
            self.Device.write(f'smu.source.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            if(measure_Range is not None):
                self.Device.write(f'smu.measure.range = {measure_Range}')
            else:
                self.Device.write('smu.measure.autorange = smu.ON')    
            #-----------------------------------------------------------
            self.Device.write(f'smu.source.range = {Current_Range}')
            if(MaxVoltageProtectionLimit is not None):
                self.Device.write(f'smu.source.protect.level = smu.PROTECT_{MaxVoltageProtectionLimit}V')
            if(CurrentLevel is not None):
                self.Device.write(f'smu.source.level = {CurrentLevel}')
            if(sourceLimit_v is not None):
                self.Device.write(f'smu.source.vlimit.level = {sourceLimit_v}')
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            self.Device.write(f'smu.source.output = smu.ON') #Enables the Source Output. Beginnig of the Measurement.
            self.Device.write(f'smu.measure.read({self.ActiveBuffer_Name})')
            self.Device.write(f'smu.source.output = smu.OFF') #Disables the Source Output. End Of the Measurement.
            #---------------------------------------------------Show in the output------------------------------
            if(showOutputasPrint):
                print(f"source current Range: {Current_Range}")
                print(f"Measured Resitance:")
                result = self.ReturnBufferValues(bufferName=self.ActiveBuffer_Name)
                print(result)
            #-------------------------------------------------------------------------------------------------------

        except Exception as ex:
            raise Exception(ex)
    def SendCurrent_MeasureVoltage_CalculateResistance(self,
                                   MaxVoltageProtectionLimit:int = None,
                                   Current_Range:float=None,
                                   CurrentLevel:float = 2,
                                   sourceLimit_v:float=None,
                                   measure_Range:float=None,
                                   use_measure_limits= False,
                                   measure_limit_Low:float=None,
                                   measure_Limit_high:float=None,
                                   measure_Limit_beep_On_Limit_high_Exceeds:bool=False,
                                   bufferName:str=None,
                                   showOutputasPrint:bool=False,
                                   ):
        try:
            #Check if the Protection Limit is Valid.
            listOfAllowedProtectionLimitVoltages = [2,5,10,20,40,60,80,100,120,140,160,180]
            if(MaxVoltageProtectionLimit is not None):
                if (listOfAllowedProtectionLimitVoltages.count(MaxVoltageProtectionLimit) < 1):
                    print(f'The MaxVoltageProtectionLimit can be one of these values: 2,5,10,20,40,60,80,100,120,140,160,180. The current value is {MaxVoltageProtectionLimit} and is not Valid.')
                    return None
            if(bufferName is not None):
                self.__ActivateSpecificBuffer(bufferName=bufferName)
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Send C - Measure V")')
            self.Device.write('display.settext(display.TEXT2, "Calculate R")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.Device.write('trigger.model.delay()')
            #Measurement Conditions
            if(measure_Range is None):
                measure_Range = self.Measure_VoltageRange
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_VOLTAGE')
            self.Device.write(f'smu.measure.unit = smu.UNIT_OHM')
            if(self.fourWireSensing):
                self.Device.write(f'smu.measure.offsetcompensation = smu.ON')
            #---> measure.range will always set after source.func is set
            if(use_measure_limits):
                if((measure_limit_Low is None) or (measure_Limit_high is None)):
                    raise Exception('Error on not inserting adequate inputs. Please Insert Limit_low and Limit_High values to set the boundries and run the function again.')
                self.Device.write(f'smu.measure.limit[1].clear()')
                self.Device.write(f'smu.measure.limit[1].autoclear = smu.OFF')
                self.Device.write(f'smu.measure.limit[1].low.value = {measure_limit_Low}')
                self.Device.write(f'smu.measure.limit[1].high.value = {measure_Limit_high}')
                if(measure_Limit_beep_On_Limit_high_Exceeds):
                    self.Device.write(f'smu.measure.limit[1].audible = smu.AUDIBLE_FAIL')
                self.Device.write(f'smu.measure.limit[1].enable = smu.ON')
            #Sourcing Conditions
            if(Current_Range is None):
                Current_Range = self.Source_CurrentRange
            self.Device.write(f'smu.source.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            if(measure_Range is not None):
                self.Device.write(f'smu.measure.range = {measure_Range}')
            else:
                self.Device.write('smu.measure.autorange = smu.ON')    
            #-----------------------------------------------------------
            self.Device.write(f'smu.source.range = {Current_Range}')
            if(MaxVoltageProtectionLimit is not None):
                self.Device.write(f'smu.source.protect.level = smu.PROTECT_{MaxVoltageProtectionLimit}V')
            if(CurrentLevel is not None):
                self.Device.write(f'smu.source.level = {CurrentLevel}')
            if(sourceLimit_v is not None):
                self.Device.write(f'smu.source.vlimit.level = {sourceLimit_v}')
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            self.Device.write(f'smu.source.output = smu.ON') #Enables the Source Output. Beginnig of the Measurement.
            self.Device.write(f'smu.measure.read({self.ActiveBuffer_Name})')
            self.Device.write(f'smu.source.output = smu.OFF') #Disables the Source Output. End Of the Measurement.
            #---------------------------------------------------Show in the output------------------------------
            if(showOutputasPrint):
                print(f"source current Range: {Current_Range}")
                print(f"Calculated Resitance:")
                result = self.ReturnBufferValues(bufferName=self.ActiveBuffer_Name)
                print(result)
            #-------------------------------------------------------------------------------------------------------

        except Exception as ex:
            raise Exception(ex)
    def SendVoltage_MeasureCurrent_CalculateResistance(self,
                                   MaxVoltageProtectionLimit:int = None,
                                   Voltage_Range:float=None,
                                   VoltageLevel:float = 2,
                                   sourceLimit_i:float=None,
                                   measure_Range:float=None,
                                   use_measure_limits= False,
                                   measure_limit_Low:float=None,
                                   measure_Limit_high:float=None,
                                   measure_Limit_beep_On_Limit_high_Exceeds:bool=False,
                                   bufferName:str=None,
                                   showOutputasPrint:bool=False,
                                   ):
        try:
            #Check if the Protection Limit is Valid.
            listOfAllowedProtectionLimitVoltages = [2,5,10,20,40,60,80,100,120,140,160,180]
            if(MaxVoltageProtectionLimit is not None):
                if (listOfAllowedProtectionLimitVoltages.count(MaxVoltageProtectionLimit) < 1):
                    print(f'The MaxVoltageProtectionLimit can be one of these values: 2,5,10,20,40,60,80,100,120,140,160,180. The current value is {MaxVoltageProtectionLimit} and is not Valid.')
                    return None
            if(bufferName is not None):
                self.__ActivateSpecificBuffer(bufferName=bufferName)
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Send C - Measure V")')
            self.Device.write('display.settext(display.TEXT2, "Calculate R")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            #Measurement Conditions
            if(measure_Range is None):
                measure_Range = self.Measure_CurrentRange
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_CURRENT')
            self.Device.write(f'smu.measure.unit = smu.UNIT_OHM')
            if(self.fourWireSensing):
                self.Device.write(f'smu.measure.offsetcompensation = smu.ON')
            #---> measure.range will always set after source.func is set
            if(use_measure_limits):
                if((measure_limit_Low is None) or (measure_Limit_high is None)):
                    raise Exception('Error on not inserting adequate inputs. Please Insert Limit_low and Limit_High values to set the boundries and run the function again.')
                self.Device.write(f'smu.measure.limit[1].clear()')
                self.Device.write(f'smu.measure.limit[1].autoclear = smu.OFF')
                self.Device.write(f'smu.measure.limit[1].low.value = {measure_limit_Low}')
                self.Device.write(f'smu.measure.limit[1].high.value = {measure_Limit_high}')
                if(measure_Limit_beep_On_Limit_high_Exceeds):
                    self.Device.write(f'smu.measure.limit[1].audible = smu.AUDIBLE_FAIL')
                self.Device.write(f'smu.measure.limit[1].enable = smu.ON')
            self.Device.write('trigger.model.delay()')    
            #Sourcing Conditions
            if(Voltage_Range is None):
                Voltage_Range = self.Source_VoltageRange
            self.Device.write(f'smu.source.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            if(measure_Range is not None):
                self.Device.write(f'smu.measure.range = {measure_Range}')
            else:
                self.Device.write('smu.measure.autorange = smu.ON')    
            #-----------------------------------------------------------
            self.Device.write(f'smu.source.range = {Voltage_Range}')
            if(MaxVoltageProtectionLimit is not None):
                self.Device.write(f'smu.source.protect.level = smu.PROTECT_{MaxVoltageProtectionLimit}V')
            if(VoltageLevel is not None):
                self.Device.write(f'smu.source.level = {VoltageLevel}')
            if(sourceLimit_i is not None):
                self.Device.write(f'smu.source.ilimit.level = {sourceLimit_i}')
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            self.Device.write(f'smu.source.output = smu.ON') #Enables the Source Output. Beginnig of the Measurement.
            self.Device.write(f'smu.measure.read({self.ActiveBuffer_Name})')
            self.Device.write(f'smu.source.output = smu.OFF') #Disables the Source Output. End Of the Measurement.
            #---------------------------------------------------Show in the output------------------------------
            if(showOutputasPrint):
                print(f"source current Range: {Voltage_Range}")
                print(f"Calculated Resitance:")
                result = self.ReturnBufferValues(bufferName=self.ActiveBuffer_Name)
                print(result)
            #-------------------------------------------------------------------------------------------------------
            
        except Exception as ex:
            raise Exception(ex)
    #------------------------------------------------------------

    #----------------SweepLinear Functions------------------------
    #Swepp logarithmic - Sweep Voltage, Measures Current
    def logarithmic_sweepcaseByPoints_Voltage(self,
                   ArbitraryConfigurationName:str,
                   startValue:float,
                   stopValue:float,
                   pointsToMeasure:int=10,
                   delayTime:float=0.00005,
                   Iterations:int=1,
                   dual:bool=False,
                   bufferName:str=None):
       
        try:
            if(bufferName is not None):
                self.ActiveBuffer_Name = bufferName
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Pulse V - Measure C")')
            self.Device.write('display.settext(display.TEXT2, "SweepLinearByPoints")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.__ActivateSpecificBuffer(bufferName=bufferName)
            self.Device.write('smu.source.func = smu.FUNC_DC_VOLTAGE')
            self.Device.write('smu.source.range = 20')
            self.Device.write('smu.measure.func = smu.FUNC_DC_CURRENT')
            self.Device.write('smu.measure.range = 100e-3')
            self.Device.write('smu.source.sweeplog("VoltLogSweep", 1, 10, 20, 1e-3, 1, smu.RANGE_FIXED')
            self.Device.write('trigger.model.initiate()')
          
           
            commandString = f'smu.source.sweeplinear("{ArbitraryConfigurationName}", {startValue}, {stopValue}, {pointsToMeasure}, {delayTime}, {Iterations}, smu.RANGE_FIXED, smu.ON, {dual}, {self.ActiveBuffer_Name})'
            
            self.Device.write(commandString)
            
            self.Device.write('trigger.model.initiate()')
            self.Device.write('waitcomplete()')
            self.Device.write('trigger.model.delay(0.00001)')
            #Notification
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT2, "Process Successful!")')
        except Exception as ex:
            raise Exception(ex)



        """


        To set up a sweep using TSP commands, you send one of the following commands:
            • smu.source.sweeplinear(): Sets up a linear sweep for a fixed number of measurement 
            points.
            • smu.source.sweeplinearstep(): Sets up a linear source sweep configuration list and 
            trigger model with a fixed number of steps.
            • smu.source.sweeplist(): Sets up a sweep based on a configuration list, which allows you to 
            customize the sweep.
            • smu.source.sweeplog(): Sets up a logarithmic sweep for a set number of measurement 
            points.
            To create a sweep:
            1. Set the source function using smu.source.func.
            2. Set the source range using smu.source.range.
            3. Set any other source settings that apply to your sweep. You must set source settings before the 
            sweep function is called.
            4. If you are using smu.source.sweeplist(), set up the source configuration list for your sweep.
            5. Set the parameters for the sweep command.
            6. Set the measurement function using smu.measure.func.
            7. Set the measurement range using smu.measure.range.
            8. Make any other settings appropriate to your sweep.
            9. Send trigger.model.initiate() to start the sweep.

        
            biasVoltage (float): _description_
        """
    
    def Sweep_LinearcaseByPoints_Voltage(self,
                   ArbitraryConfigurationName:str,
                   startValue:float,
                   stopValue:float,
                   pointsToMeasure:int=10,
                   delayTime:float=0.00005,
                   Iterations:int=1,
                   failAbort:bool=False,
                   dual:bool=False,
                   bufferName:str=None):
        """
        
        When the sweep is started, the instrument sources a specific voltage or current value to the device 
        under test (DUT). A measurement is made for each point of the sweep.
        NOTE: To increase the speed of sweeps:
            • Reduce the NPLC.
            • Turn autozero off.
        Note: Some commands have optional parameters. If there are optional parameters, they must be 
        entered in the order presented in the Usage section. You cannot leave out any parameters that 
        precede the optional parameter. Optional parameters are shown as separate lines in usage, 
        presented in the required order with each valid permutation of the optional parameters.

        Note: Points = [(StopValue - StartValue)/Step] + 1. 

        Args:
        ArbitraryConfigurationName: A string that contains the name of the configuration list that the instrument will 
        create for this sweep
        startValue: The voltage (For This Function) or current (for other functions) source level at which the sweep starts:
            • Current: -1.05 A to 1.05 A
            • Voltage: -210 V to 210 V
        stopValue: The voltage (For This Function) or current (for other functions) at which the sweep stops:
            • Current: -1.05 A to 1.05 A
            • Voltage: -210 V to 210 V
        pointsToMeasure: The number of source-measure points between the start and stop values of the 
        sweep (2 to 1e6); to calculate the number of source-measure points in a sweep, use 
        the following formula:
            --Points = [(Stop - Start) / Step] + 1
        delayTime: The delay between measurement points; default is smu.DELAY_AUTO, which 
        enables autodelay, or a specific delay value from 50 µs to 10 ks, or 0 for no delay
        Iterations: The number of times to run the sweep; default is 1:
            • Infinite loop: smu.INFINITE
            • Finite loop: 1 to 268,435,455
        rangeType: The source range that is used for the sweep:
            • Most sensitive source range for each source level in the sweep: 
          smu.RANGE_AUTO
            • Best fixed range: smu.RANGE_BEST (default)
            • Present source range for the entire sweep: smu.RANGE_FIXED <-- This one is used here.
        failAbort: Complete the sweep if the source limit is exceeded: smu.OFF 
        Abort the sweep if the source limit is exceeded: smu.ON (default) <-- This one is used here.
        dual: Determines if the sweep runs from start to stop and then from stop to start:
            • Sweep from start to stop only: smu.OFF (default)
            • Sweep from start to stop, then stop to start: smu.ON
        bufferName: The name of a reading buffer; the default buffers (defbuffer1 or defbuffer2) or 
        the name of a user-defined buffer; if no buffer is specified, this parameter by default is set to 
        defbuffer1.

        Note: The application always use the LAST ACTIVE BUFFER if the user does not mention any specific buffer to store data in it.
        """
        try:
            if(bufferName is not None):
                self.ActiveBuffer_Name = bufferName
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Pulse V - Measure C")')
            self.Device.write('display.settext(display.TEXT2, "SweepLinearByPoints")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Measurement Conditions
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_CURRENT')
          
            #---> measure.range will always set after source.func is set
            #Sourcing Conditions
            self.Device.write(f'smu.source.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.range = {self.Measure_CurrentRange}')
            #-----------------------------------------------------------
            self.Device.write(f'smu.source.range = {self.Source_VoltageRange}')
            #Note: This line of code should be changed if it is required to append the data
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            #Sweep Function
            #sample: smu.source.sweeplinear(configListName, start, stop, points, delay, count, rangeType, failAbort, dual, bufferName)
            if failAbort:
                failAbortCommand = "smu.ON"
            else:
                failAbortCommand = "smu.OFF"
            commandString = f'smu.source.sweeplinear("{ArbitraryConfigurationName}", {startValue}, {stopValue}, {pointsToMeasure}, {delayTime}, {Iterations}, smu.RANGE_FIXED, {failAbortCommand}, {dual}, {self.ActiveBuffer_Name})'
            #Send the Ccommand
            #time.sleep(1)
            self.Device.write(commandString)
            #Sweep mechanism does not require smu.source.output = smu.ON command.
            #Instead it uses triggers.
            #Run the sweep command
            self.Device.write('trigger.model.initiate()')
            self.Device.write('waitcomplete()')
            self.Device.write('trigger.model.delay(0.00001)')
            #Notification
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT2, "Process Successful!")')
        except Exception as ex:
            raise Exception(ex)




        """


        To set up a sweep using TSP commands, you send one of the following commands:
            • smu.source.sweeplinear(): Sets up a linear sweep for a fixed number of measurement 
            points.
            • smu.source.sweeplinearstep(): Sets up a linear source sweep configuration list and 
            trigger model with a fixed number of steps.
            • smu.source.sweeplist(): Sets up a sweep based on a configuration list, which allows you to 
            customize the sweep.
            • smu.source.sweeplog(): Sets up a logarithmic sweep for a set number of measurement 
            points.
            To create a sweep:
            1. Set the source function using smu.source.func.
            2. Set the source range using smu.source.range.
            3. Set any other source settings that apply to your sweep. You must set source settings before the 
            sweep function is called.
            4. If you are using smu.source.sweeplist(), set up the source configuration list for your sweep.
            5. Set the parameters for the sweep command.
            6. Set the measurement function using smu.measure.func.
            7. Set the measurement range using smu.measure.range.
            8. Make any other settings appropriate to your sweep.
            9. Send trigger.model.initiate() to start the sweep.

        
            biasVoltage (float): _description_
        """
    
    def Sweep_LinearcaseByStep_Voltage(self,
                ArbitraryConfigurationName:str,
                startValue:float,
                stopValue:float,
                stepValue:int,
                delayTime:float=0,
                Iterations:int=1,
                failAbort:bool=False,
                dual:bool=False,
                bufferName:str=None):
        if(bufferName is not None):
            self.ActiveBuffer_Name = bufferName
        """
        Get s a Start and Stop Votage Value and measures the current at each increasing step.

        Note: Some commands have optional parameters. If there are optional parameters, they must be 
        entered in the order presented in the Usage section. You cannot leave out any parameters that 
        precede the optional parameter. Optional parameters are shown as separate lines in usage, 
        presented in the required order with each valid permutation of the optional parameters.

        When the sweep is started, the instrument sources a specific voltage or current value to the device 
        under test (DUT). A measurement is made for each step of the sweep.
        NOTE: To increase the speed of sweeps:
            • Reduce the NPLC.
            • Turn autozero off.
        
        Args:
        ArbitraryConfigurationName: A string that contains the name of the configuration list that the instrument will 
        create for this sweep
        startValue: The voltage (For This Function) or current (for other functions) source level at which the sweep starts:
            • Current: -1.05 A to 1.05 A
            • Voltage: -210 V to 210 V
        stopValue: The voltage (For This Function) or current (for other functions) at which the sweep stops:
            • Current: -1.05 A to 1.05 A
            • Voltage: -210 V to 210 V
        stepValue: The step size at which the source level will change; must be more than 0
        delayTime: The delay between measurement points; default is smu.DELAY_AUTO, which 
        enables autodelay, or a specific delay value from 50 µs to 10 ks, or 0 for no delay
        Iterations: The number of times to run the sweep; default is 1:
            • Infinite loop: smu.INFINITE
            • Finite loop: 1 to 268,435,455
        rangeType: The source range that is used for the sweep:
            • Most sensitive source range for each source level in the sweep: 
          smu.RANGE_AUTO
            • Best fixed range: smu.RANGE_BEST (default)
            • Present source range for the entire sweep: smu.RANGE_FIXED <-- This one is used here.
        failAbort: Complete the sweep if the source limit is exceeded: smu.OFF 
        Abort the sweep if the source limit is exceeded: smu.ON (default) <-- This one is used here.
        dual: Determines if the sweep runs from start to stop and then from stop to start:
            • Sweep from start to stop only: smu.OFF (default)
            • Sweep from start to stop, then stop to start: smu.ON
        bufferName: The name of a reading buffer; the default buffers (defbuffer1 or defbuffer2) or 
        the name of a user-defined buffer; if no buffer is specified, this parameter by default is set to 
        defbuffer1.

        Note: The application always use the LAST ACTIVE BUFFER if the user does not mention any specific buffer to store data in it.
        """
        try:
            if(bufferName is not None):
                self.ActiveBuffer_Name = bufferName
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Pulse V - Measure C")')
            self.Device.write('display.settext(display.TEXT2, "SweepLinearByStep")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Measurement Conditions
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            #Sourcing Conditions
            self.Device.write(f'smu.source.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.range = {self.Measure_CurrentRange}')
            #--------------------------------------------------------------------
            self.Device.write(f'smu.source.range = {self.Source_VoltageRange}')
            #Note: This line of code should be shanged if it is required to append the data
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            #Sweep Function:
            #sample: smu.source.sweeplinearstep(configListName, start, stop, step, delay, count, rangeType, failAbort, dual, bufferName)
            if failAbort:
                failAbortCommand = "smu.ON"
            else:
                failAbortCommand = "smu.OFF"
            commandString = f'smu.source.sweeplinearstep("{ArbitraryConfigurationName}", {startValue}, {stopValue}, {stepValue}, {delayTime}, {Iterations}, smu.RANGE_FIXED, {failAbortCommand}, {dual},{self.ActiveBuffer_Name})'
            #Send the commands
            self.Device.write(commandString)
            #Sweep mechanism does not require smu.source.output = smu.ON command.
            #Instead it uses triggers.
            #Run the sweep command
            self.Device.write('trigger.model.initiate()')
            self.Device.write('waitcomplete()')
            self.Device.write('trigger.model.delay()')
            #Notification
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT2, "Process Successful!")')
        except Exception as ex:
            raise Exception(ex)
    def Sweeplog_ByPoints_Voltage(self,
                ArbitraryConfigurationName:str,
                startValue:float,
                stopValue:float,
                pointsToMeasure:int,
                delayTime:float=0,
                Iterations:int=1,
                failAbort:bool=False,
                dual:bool=False,
                bufferName:str=None):
        if(bufferName is not None):
            self.ActiveBuffer_Name = bufferName
        """
        smu.source.sweeplog(configListName, start, stop, points, delay, count, rangeType, 
        failAbort, dual, bufferName, asymptote)
        
        Get s a Start and Stop Votage Value and measures the current at each increasing step.

        Note: Some commands have optional parameters. If there are optional parameters, they must be 
        entered in the order presented in the Usage section. You cannot leave out any parameters that 
        precede the optional parameter. Optional parameters are shown as separate lines in usage, 
        presented in the required order with each valid permutation of the optional parameters.

        When the sweep is started, the instrument sources a specific voltage or current value to the device 
        under test (DUT). A measurement is made for each step of the sweep.
        NOTE: To increase the speed of sweeps:
            • Reduce the NPLC.
            • Turn autozero off.
        
        Args:
        ArbitraryConfigurationName: A string that contains the name of the configuration list that the instrument will 
        create for this sweep
        startValue: The voltage (For This Function) or current (for other functions) source level at which the sweep starts:
            • Current: -1.05 A to 1.05 A
            • Voltage: -210 V to 210 V
        stopValue: The voltage (For This Function) or current (for other functions) at which the sweep stops:
            • Current: -1.05 A to 1.05 A
            • Voltage: -210 V to 210 V
        stepValue: The step size at which the source level will change; must be more than 0
        delayTime: The delay between measurement points; default is smu.DELAY_AUTO, which 
        enables autodelay, or a specific delay value from 50 µs to 10 ks, or 0 for no delay
        Iterations: The number of times to run the sweep; default is 1:
            • Infinite loop: smu.INFINITE
            • Finite loop: 1 to 268,435,455
        rangeType: The source range that is used for the sweep:
            • Most sensitive source range for each source level in the sweep: 
          smu.RANGE_AUTO
            • Best fixed range: smu.RANGE_BEST (default)
            • Present source range for the entire sweep: smu.RANGE_FIXED <-- This one is used here.
        failAbort: Complete the sweep if the source limit is exceeded: smu.OFF 
        Abort the sweep if the source limit is exceeded: smu.ON (default) <-- This one is used here.
        dual: Determines if the sweep runs from start to stop and then from stop to start:
            • Sweep from start to stop only: smu.OFF (default)
            • Sweep from start to stop, then stop to start: smu.ON
        bufferName: The name of a reading buffer; the default buffers (defbuffer1 or defbuffer2) or 
        the name of a user-defined buffer; if no buffer is specified, this parameter by default is set to 
        defbuffer1.

        Note: The application always use the LAST ACTIVE BUFFER if the user does not mention any specific buffer to store data in it.
        """
        try:
            if(bufferName is not None):
                self.ActiveBuffer_Name = bufferName
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Pulse V - Measure C")')
            self.Device.write('display.settext(display.TEXT2, "SweepLogByPoints")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Measurement Conditions
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            #Sourcing Conditions
            self.Device.write(f'smu.source.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.range = {self.Measure_CurrentRange}')
            #--------------------------------------------------------------------
            self.Device.write(f'smu.source.range = {self.Source_VoltageRange}')
            #Note: This line of code should be shanged if it is required to append the data
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            #Sweep Function:
            #sample: smu.source.sweeplinearstep(configListName, start, stop, step, delay, count, rangeType, failAbort, dual, bufferName)
            if failAbort:
                failAbortCommand = "smu.ON"
            else:
                failAbortCommand = "smu.OFF"
            commandString = f'smu.source.sweeplog("{ArbitraryConfigurationName}", {startValue}, {stopValue}, {pointsToMeasure}, {delayTime}, {Iterations}, smu.RANGE_FIXED, {failAbortCommand}, {dual},{self.ActiveBuffer_Name})'
            #Send the commands
            self.Device.write(commandString)
            #Sweep mechanism does not require smu.source.output = smu.ON command.
            #Instead it uses triggers.
            #Run the sweep command
            self.Device.write('trigger.model.initiate()')
            self.Device.write('waitcomplete()')
            self.Device.write('trigger.model.delay()')
            #Notification
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT2, "Process Successful!")')
        except Exception as ex:
            raise Exception(ex)
    
    #Swepp Linear - Sweep Current, Measures Voltage
    def Sweep_LinearcaseByPoints_Current(self,
                   ArbitraryConfigurationName:str,
                   startValue:float,
                   stopValue:float,
                   pointsToMeasure:int=10,
                   delayTime:float=0,
                   Iterations:int=1,
                   dual:bool=False,
                   bufferName:str=None):
        """
        
        When the sweep is started, the instrument sources a specific voltage or current value to the device 
        under test (DUT). A measurement is made for each point of the sweep.
        NOTE: To increase the speed of sweeps:
            • Reduce the NPLC.
            • Turn autozero off.
        Note: Some commands have optional parameters. If there are optional parameters, they must be 
        entered in the order presented in the Usage section. You cannot leave out any parameters that 
        precede the optional parameter. Optional parameters are shown as separate lines in usage, 
        presented in the required order with each valid permutation of the optional parameters.

        Note: Points = [(StopValue - StartValue)/Step] + 1. 

        Args:
        ArbitraryConfigurationName: A string that contains the name of the configuration list that the instrument will 
        create for this sweep
        startValue: The voltage (For This Function) or current (for other functions) source level at which the sweep starts:
            • Current: -1.05 A to 1.05 A
            • Voltage: -210 V to 210 V
        stopValue: The voltage (For This Function) or current (for other functions) at which the sweep stops:
            • Current: -1.05 A to 1.05 A
            • Voltage: -210 V to 210 V
        pointsToMeasure: The number of source-measure points between the start and stop values of the 
        sweep (2 to 1e6); to calculate the number of source-measure points in a sweep, use 
        the following formula:
            --Points = [(Stop - Start) / Step] + 1
        delayTime: The delay between measurement points; default is smu.DELAY_AUTO, which 
        enables autodelay, or a specific delay value from 50 µs to 10 ks, or 0 for no delay
        Iterations: The number of times to run the sweep; default is 1:
            • Infinite loop: smu.INFINITE
            • Finite loop: 1 to 268,435,455
        rangeType: The source range that is used for the sweep:
            • Most sensitive source range for each source level in the sweep: 
          smu.RANGE_AUTO
            • Best fixed range: smu.RANGE_BEST (default)
            • Present source range for the entire sweep: smu.RANGE_FIXED <-- This one is used here.
        failAbort: Complete the sweep if the source limit is exceeded: smu.OFF 
        Abort the sweep if the source limit is exceeded: smu.ON (default) <-- This one is used here.
        dual: Determines if the sweep runs from start to stop and then from stop to start:
            • Sweep from start to stop only: smu.OFF (default)
            • Sweep from start to stop, then stop to start: smu.ON
        bufferName: The name of a reading buffer; the default buffers (defbuffer1 or defbuffer2) or 
        the name of a user-defined buffer; if no buffer is specified, this parameter by default is set to 
        defbuffer1.

        Note: The application always use the LAST ACTIVE BUFFER if the user does not mention any specific buffer to store data in it.
        """
        try:
            if(bufferName is not None):
                self.ActiveBuffer_Name = bufferName
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Pulse V - Measure C")')
            self.Device.write('display.settext(display.TEXT2, "SweepLinearByPoints")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Measurement Conditions
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            #Sourcing Conditions
            self.Device.write(f'smu.source.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.range = {self.Measure_VoltageRange}')
            #-----------------------------------------------------------
            self.Device.write(f'smu.source.range = {self.Source_CurrentRange}')
            #Note: This line of code should be changed if it is required to append the data
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            #Sweep Function
            #sample: smu.source.sweeplinear(configListName, start, stop, points, delay, count, rangeType, failAbort, dual, bufferName)
            commandString = f'smu.source.sweeplinear("{ArbitraryConfigurationName}", {startValue}, {stopValue}, {pointsToMeasure}, {delayTime}, {Iterations}, smu.RANGE_FIXED, smu.ON, {dual}, {self.ActiveBuffer_Name})'
            #Send the Ccommand
            self.Device.write(commandString)
            #Sweep mechanism does not require smu.source.output = smu.ON command.
            #Instead it uses triggers.
            #Run the sweep command
            self.Device.write('trigger.model.initiate()')
            self.Device.write('waitcomplete()')
            self.Device.write('trigger.model.delay()')
            #Notification
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT2, "Process Successful!")')
        except Exception as ex:
            raise Exception(ex)




        """


        To set up a sweep using TSP commands, you send one of the following commands:
            • smu.source.sweeplinear(): Sets up a linear sweep for a fixed number of measurement 
            points.
            • smu.source.sweeplinearstep(): Sets up a linear source sweep configuration list and 
            trigger model with a fixed number of steps.
            • smu.source.sweeplist(): Sets up a sweep based on a configuration list, which allows you to 
            customize the sweep.
            • smu.source.sweeplog(): Sets up a logarithmic sweep for a set number of measurement 
            points.
            To create a sweep:
            1. Set the source function using smu.source.func.
            2. Set the source range using smu.source.range.
            3. Set any other source settings that apply to your sweep. You must set source settings before the 
            sweep function is called.
            4. If you are using smu.source.sweeplist(), set up the source configuration list for your sweep.
            5. Set the parameters for the sweep command.
            6. Set the measurement function using smu.measure.func.
            7. Set the measurement range using smu.measure.range.
            8. Make any other settings appropriate to your sweep.
            9. Send trigger.model.initiate() to start the sweep.

        
            biasVoltage (float): _description_
        """
    def Sweep_LinearcaseByStep_Current(self,
                ArbitraryConfigurationName:str,
                startValue:float,
                stopValue:float,
                stepValue:int,
                delayTime:float=0,
                Iterations:int=1,
                dual:bool=False,
                bufferName:str=None):
        if(bufferName is not None):
            self.ActiveBuffer_Name = bufferName
        """
        Get s a Start and Stop Votage Value and measures the current at each increasing step.

        Note: Some commands have optional parameters. If there are optional parameters, they must be 
        entered in the order presented in the Usage section. You cannot leave out any parameters that 
        precede the optional parameter. Optional parameters are shown as separate lines in usage, 
        presented in the required order with each valid permutation of the optional parameters.

        When the sweep is started, the instrument sources a specific voltage or current value to the device 
        under test (DUT). A measurement is made for each step of the sweep.
        NOTE: To increase the speed of sweeps:
            • Reduce the NPLC.
            • Turn autozero off.
        
        Args:
        ArbitraryConfigurationName: A string that contains the name of the configuration list that the instrument will 
        create for this sweep
        startValue: The voltage (For This Function) or current (for other functions) source level at which the sweep starts:
            • Current: -1.05 A to 1.05 A
            • Voltage: -210 V to 210 V
        stopValue: The voltage (For This Function) or current (for other functions) at which the sweep stops:
            • Current: -1.05 A to 1.05 A
            • Voltage: -210 V to 210 V
        stepValue: The step size at which the source level will change; must be more than 0
        delayTime: The delay between measurement points; default is smu.DELAY_AUTO, which 
        enables autodelay, or a specific delay value from 50 µs to 10 ks, or 0 for no delay
        Iterations: The number of times to run the sweep; default is 1:
            • Infinite loop: smu.INFINITE
            • Finite loop: 1 to 268,435,455
        rangeType: The source range that is used for the sweep:
            • Most sensitive source range for each source level in the sweep: 
          smu.RANGE_AUTO
            • Best fixed range: smu.RANGE_BEST (default)
            • Present source range for the entire sweep: smu.RANGE_FIXED <-- This one is used here.
        failAbort: Complete the sweep if the source limit is exceeded: smu.OFF 
        Abort the sweep if the source limit is exceeded: smu.ON (default) <-- This one is used here.
        dual: Determines if the sweep runs from start to stop and then from stop to start:
            • Sweep from start to stop only: smu.OFF (default)
            • Sweep from start to stop, then stop to start: smu.ON
        bufferName: The name of a reading buffer; the default buffers (defbuffer1 or defbuffer2) or 
        the name of a user-defined buffer; if no buffer is specified, this parameter by default is set to 
        defbuffer1.

        Note: The application always use the LAST ACTIVE BUFFER if the user does not mention any specific buffer to store data in it.
        """
        try:
            if(bufferName is not None):
                self.ActiveBuffer_Name = bufferName
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Pulse V - Measure C")')
            self.Device.write('display.settext(display.TEXT2, "SweepLinearByStep")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Measurement Conditions
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            #Sourcing Conditions
            self.Device.write(f'smu.source.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.range = {self.Measure_VoltageRange}')
            #-----------------------------------------------------------
            self.Device.write(f'smu.source.range = {self.Source_CurrentRange}')
            #Note: This line of code should be shanged if it is required to append the data
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            #Sweep Function:
            #sample: smu.source.sweeplinearstep(configListName, start, stop, step, delay, count, rangeType, failAbort, dual, bufferName)
            commandString = f'smu.source.sweeplinearstep("{ArbitraryConfigurationName}", {startValue}, {stopValue}, {stepValue}, {delayTime}, {Iterations}, smu.RANGE_FIXED, smu.ON, {dual},{self.ActiveBuffer_Name})'
            #Send the commands
            self.Device.write(commandString)
            #Sweep mechanism does not require smu.source.output = smu.ON command.
            #Instead it uses triggers.
            #Run the sweep command
            self.Device.write('trigger.model.initiate()')
            self.Device.write('waitcomplete()')
            self.Device.write('trigger.model.delay()')
            #Notification
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT2, "Process Successful!")')
        except Exception as ex:
            raise Exception(ex)
    #Sweep Linear - Measure Resistance ??????????????????????????????????
    def Sweep_LinearcaseByPoints_SourceCurrent_MeasureResistance(self,
                   ArbitraryConfigurationName:str,
                   startValue:float,
                   stopValue:float,
                   pointsToMeasure:int=10,
                   delayTime:float=0,
                   Iterations:int=1,
                   dual:bool=False,
                   bufferName:str=None):
        """
        .Measure resistance using the resistance function:
            Resistance function => smu.measure.func = smu.FUNC_RESISTANCE
        
        NOTE:   When the measurement function is set to resistance, the Model 2450 measures resistances by "sourcing current".
                The instrument automatically sets the magnitude of the current source, voltage limit, and the measure range.

        NOTE:   (General Note when using the resistance measurement functions)
                When you make resistance measurements, the resistance is calculated by either sourcing current 
                and measuring voltage or by sourcing voltage and measuring current.
                When source readback is on, the instrument measures both voltage and current and uses these 
                values in the ohms calculations. When source readback is off, the instrument uses the programmed 
                source value and the measured value in the ohms calculations. Note that the measured source value 
                is more accurate than the programmed source value, so measurements made with source readback 
                on are more accurate
                
        NOTE:   (General Note when using the resistance measurement functions)
                From a remote interface, you can use one of following methods to measure resistance with the Model 
                2450:
                • Source voltage, measure current, and set measure units to ohms 
                • Source current, measure voltage, and set measure units to ohms 
                • Set the measure function to resistance. When the measure function is set to resistance, the 
                instrument sets the source current and source limit automatically <- This function works as described here
        """
        
        
        try:
            if(bufferName is not None):
                self.ActiveBuffer_Name = bufferName
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Pulse C - Measure R")')
            self.Device.write('display.settext(display.TEXT2, "SweepLinearByPoint")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Measurement Conditions
            self.Device.write(f'smu.measure.func = smu.FUNC_RESISTANCE')
            if(self.fourWireSensing):
                self.Device.write(f'smu.measure.offsetcompensation = smu.ON')
            #Sourcing Conditions
            self.Device.write(f'smu.source.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            if(self.Measure_ResistanceRange is not None):
                self.Device.write(f'smu.measure.range = {self.Measure_ResistanceRange}')
            else:
                self.Device.write('smu.measure.autorange = smu.ON')
            #-----------------------------------------------------------
            self.Device.write(f'smu.source.range = {self.Source_CurrentRange}')
            #Note: This line of code should be shanged if it is required to append the data
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            #Sweep Function:
            #sample: smu.source.sweeplinearstep(configListName, start, stop, step, delay, count, rangeType, failAbort, dual, bufferName)
            commandString = f'smu.source.sweeplinearstep("{ArbitraryConfigurationName}", {startValue}, {stopValue}, {pointsToMeasure}, {delayTime}, {Iterations}, smu.RANGE_FIXED, smu.ON, {dual},{self.ActiveBuffer_Name})'
            #Send the commands
            self.Device.write(commandString)
            #Sweep mechanism does not require smu.source.output = smu.ON command.
            #Instead it uses triggers.
            #Run the sweep command
            self.Device.write('trigger.model.initiate()')
            self.Device.write('waitcomplete()')
            self.Device.write('trigger.model.delay()')
            #Notification
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT2, "Process Successful!")')
        except Exception as ex:
            raise Exception(ex)
    
    def Sweep_LinearcaseByPoints_SourceCurrent_MeasureVoltage_CalculateResistance(self,
                   ArbitraryConfigurationName:str,
                   startValue:float,
                   stopValue:float,
                   pointsToMeasure:int=10,
                   delayTime:float=0,
                   Iterations:int=1,
                   dual:bool=False,
                   bufferName:str=None):
        """
        NOTE:   (General Note when using the resistance measurement functions)
                When you make resistance measurements, the resistance is calculated by either sourcing current 
                and measuring voltage or by sourcing voltage and measuring current.
                When source readback is on, the instrument measures both voltage and current and uses these 
                values in the ohms calculations. When source readback is off, the instrument uses the programmed 
                source value and the measured value in the ohms calculations. Note that the measured source value 
                is more accurate than the programmed source value, so measurements made with source readback 
                on are more accurate

        NOTE:   (General Note when using the resistance measurement functions)
                From a remote interface, you can use one of following methods to measure resistance with the Model 2450:
                • Source voltage, measure current, and set measure units to ohms 
                • Source current, measure voltage, and set measure units to ohms <- This function works as described here
                • Set the measure function to resistance. When the measure function is set to resistance, the 
                instrument sets the source current and source limit automatically
        """
        
        
        try:
            if(bufferName is not None):
                self.ActiveBuffer_Name = bufferName
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Pulse C - Measure R")')
            self.Device.write('display.settext(display.TEXT2, "SweepLinearByPoint")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Measurement Conditions
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.unit = smu.UNIT_OHM')
            #Sourcing Conditions
            self.Device.write(f'smu.source.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.range = {self.Measure_VoltageRange}')
            #----------------------------------------------------------
            self.Device.write(f'smu.source.range = {self.Source_CurrentRange}')
            #Note: This line of code should be shanged if it is required to append the data
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            #Sweep Function:
            #sample: smu.source.sweeplinearstep(configListName, start, stop, step, delay, count, rangeType, failAbort, dual, bufferName)
            commandString = f'smu.source.sweeplinear("{ArbitraryConfigurationName}", {startValue}, {stopValue}, {pointsToMeasure}, {delayTime}, {Iterations}, smu.RANGE_FIXED, smu.ON, {dual},{self.ActiveBuffer_Name})'
            #Send the commands
            self.Device.write(commandString)
            #Sweep mechanism does not require smu.source.output = smu.ON command.
            #Instead it uses triggers.
            #Run the sweep command
            self.Device.write('trigger.model.initiate()')
            self.Device.write('waitcomplete()')
            self.Device.write('trigger.model.delay()')
            #Notification
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT2, "Process Successful!")')
        except Exception as ex:
            raise Exception(ex)
    def Sweep_LinearcaseByPoints_SourceVoltage_MeasureCurrent_CalculateResistance(self,
                   ArbitraryConfigurationName:str,
                   startValue:float,
                   stopValue:float,
                   pointsToMeasure:int=10,
                   delayTime:float=0,
                   Iterations:int=1,
                   dual:bool=False,
                   bufferName:str=None):
        """
        NOTE:   (General Note when using the resistance measurement functions)
                When you make resistance measurements, the resistance is calculated by either sourcing current 
                and measuring voltage or by sourcing voltage and measuring current.
                When source readback is on, the instrument measures both voltage and current and uses these 
                values in the ohms calculations. When source readback is off, the instrument uses the programmed 
                source value and the measured value in the ohms calculations. Note that the measured source value 
                is more accurate than the programmed source value, so measurements made with source readback 
                on are more accurate

        NOTE:   (General Note when using the resistance measurement functions)
                From a remote interface, you can use one of following methods to measure resistance with the Model 2450:
                • Source voltage, measure current, and set measure units to ohms 
                • Source current, measure voltage, and set measure units to ohms <- This function works as described here
                • Set the measure function to resistance. When the measure function is set to resistance, the 
                instrument sets the source current and source limit automatically
        """
        
        
        try:
            if(bufferName is not None):
                self.ActiveBuffer_Name = bufferName
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Pulse V - Measure R")')
            self.Device.write('display.settext(display.TEXT2, "SweepLinearByPoint")')
            #Setting Up the Device ///// Configuration settings
            self.__ResetTheConfigurations()
            self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Measurement Conditions
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_CURRENT')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.unit = smu.UNIT_OHM')
            #Sourcing Conditions
            self.Device.write(f'smu.source.func = smu.FUNC_DC_VOLTAGE')
            #---> measure.range will always set after source.func is set
            self.Device.write(f'smu.measure.range = {self.Measure_CurrentRange}')
            #----------------------------------------------------------
            self.Device.write(f'smu.source.range = {self.Source_VoltageRange}')
            #Note: This line of code should be shanged if it is required to append the data
            self.Device.write(f'{self.ActiveBuffer_Name}.clear()')
            #Sweep Function:
            #sample: smu.source.sweeplinearstep(configListName, start, stop, step, delay, count, rangeType, failAbort, dual, bufferName)
            commandString = f'smu.source.sweeplinear("{ArbitraryConfigurationName}", {startValue}, {stopValue}, {pointsToMeasure}, {delayTime}, {Iterations}, smu.RANGE_FIXED, smu.ON, {dual},{self.ActiveBuffer_Name})'
            #Send the commands
            self.Device.write(commandString)
            #Sweep mechanism does not require smu.source.output = smu.ON command.
            #Instead it uses triggers.
            #Run the sweep command
            self.Device.write('trigger.model.initiate()')
            self.Device.write('waitcomplete()')
            self.Device.write('trigger.model.delay()')
            #Notification
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT2, "Process Successful!")')
        except Exception as ex:
            raise Exception(ex)
    #-------------------------------------------------------------------------------------
    #----------------Custom Sweep---------------------------------------------------------
    def Sweep_Custom_SourceVoltage_MeasureCurrent(self,source_Range:float=None,
                                                  measure_range:float=None,
                                                  Source_ListOfLevels:List[float]=[0.00,0.01],
                                                  AribtraryConfigName:str="SweepList1",
                                                  startIndex:int=1,
                                                  delay:float=0.001,
                                                  count:int=1,
                                                  bufferName:str=None):
        try:
            if(source_Range is None):
                source_Range = self.Source_VoltageRange
            if(measure_range is None):
                measure_range = self.Measure_CurrentRange
            if(bufferName is not None):
                self.__ActivateSpecificBuffer(bufferName=bufferName)
            #Setting Up the device
            self.Device.write('display.changescreen(display.SCREEN_USER_SWIPE)')
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT1, "Pulse V - Measure C")')
            self.Device.write('display.settext(display.TEXT2, "Custom Sweep")')
            self.__ResetTheConfigurations()
            #Set the Source
            self.Device.write(f'smu.source.configlist.create("{AribtraryConfigName}")')
            self.Device.write(f'smu.source.func = smu.FUNC_DC_VOLTAGE')
            self.Device.write(f'smu.source.range = {source_Range}')
            for value in Source_ListOfLevels:
                self.Device.write(f'smu.source.range = {value}')
                self.Device.write(f'smu.source.configlist.store("{AribtraryConfigName}")')
            #sample: smu.source.sweeplist(configListName, index, delay, count, failAbort, bufferName)
            self.Device.write(f'smu.source.sweeplist("{AribtraryConfigName}", {startIndex}, {delay},{count}, smu.ON, {self.ActiveBuffer_Name})')
            #Set the Measure
            self.Device.write(f'smu.measure.func = smu.FUNC_DC_CURRENT')
            self.Device.write(f'smu.measure.range = {measure_range}')
            #Run the sweep command
            self.Device.write('trigger.model.initiate()')
            self.Device.write('waitcomplete()')
            self.Device.write('trigger.model.delay()')
            #Notification
            self.Device.write('display.clear()')
            self.Device.write('display.settext(display.TEXT2, "Process Successful!")')
        except Exception as ex:
            raise Exception(ex)
    #------------------------------------------------------------------------------------- 





def pulseCurrentMeasureVoltage(sourceVoltageLevel, 
                               biasCurrent, 
                               startVoltage_1, 
                               stopVoltage_1, 
                               startVoltage_2, 
                               stopVoltage_2, 
                               currentlimit, 
                               timeON, 
                               timeOFF, 
                               points1, 
                               points2, 
                               tag1, 
                               tag2, 
                               cycleCounter):
    pass
























#General Purpose Functions. Please Do not Manipulate these Functions
def __getAllResources__():
    return visa.ResourceManager().list_resources()

















#Pyvisa Comments
"""
Write:
The write() method is used to send commands or instructions to the instrument without expecting a response. It is commonly used to configure settings, start measurements, or control various functionalities of the instrument. This method is useful when you need to send commands to the instrument that don't require a response back.
e.g. -> instrument.write("CONF:VOLT:DC 10,0.001")

Read:
The read() method is used to read data from the instrument after sending a command. It's typically used when the instrument is expected to send a response back that you want to capture and use in your program. This is useful for retrieving measurement results, instrument status, or other information from the instrument.
e.g. -> measurement_result = instrument.read()

Query:
The query() method combines the write() and read() operations in a single call. It sends a command to the instrument and waits for and returns the response. This method is particularly useful when you want to send a command and immediately receive a response without the need for separate write and read calls.
e.g. -> instrument.query("MEAS:VOLT:DC?")

Close:
The close() method is used to close the connection to the instrument. After you have finished interacting with the instrument, it's important to close the connection to release any resources associated with it. Failing to close connections properly can lead to resource leaks and affect the overall performance of your program.
e.g. -> instrument.close()

"""

#Instrument Comments
"""

1.Range: To adjust the accuracy of the device
The range refers to the adjustable or selectable values that the source-measure unit can operate within. For example, a voltage source might have multiple range settings (e.g., ±10V, ±100V), allowing you to choose the appropriate voltage range for your application. Similarly, a current source might have different range settings (e.g., ±1mA, ±100mA). Choosing the appropriate range ensures that the source-measure unit operates optimally and can accurately provide the desired voltage or current output.

2.Level: To adjust the exact operating values
The level specifies the specific value within the selected range at which the source-measure unit will operate. It represents the desired voltage or current output that you want the instrument to provide. For instance, if you're sourcing a voltage, you would set the level to the specific voltage you want to output. Similarly, if you're sourcing a current, you would set the level to the desired current value.

3.Limit: Safety Mechanism
The limit refers to a safety threshold or boundary that you set to protect the device under test (DUT) or the source-measure unit itself. These limits are used to prevent overloading the DUT or the SMU, which could potentially cause damage. There are usually two types of limits: compliance limits and protection limits.

    .Compliance Limits: These limits are used to define the maximum voltage or current that the source-measure unit can provide. If the DUT draws too much current or exceeds the set voltage, the source-measure unit will limit its output to stay within these compliance limits. This prevents excessive stress on the DUT and maintains safe operation.

    .Protection Limits: These limits are designed to safeguard the SMU from potential damage caused by improper connections or transient events. If the output current or voltage exceeds the protection limits, the source-measure unit will take measures to protect itself, such as shutting down the output or activating a protection mechanism.
-----------------------------------------------
-----------------------------------------------
-----------------------------------------------





        Using NPLCs to adjust speed and accuracy
            You can adjust the amount of time that the input signal is measured. Adjustments to the amount of 
            time affect the usable measurement resolution, the amount of reading noise, and the reading rate of 
            the instrument.
            The amount of time is specified in parameters that are based on the number of power line cycles 
            (NPLCs). Each power line cycle for 60 Hz is 16.67 ms (1/60); for 50 Hz, it is 20 ms (1/50).
            The shortest amount of time results in the fastest reading rate, but increases the reading noise and 
            decreases the number of usable digits.
            The longest amount of time provides the lowest reading noise and more usable digits, but has the 
            slowest reading rate.
            Settings between the fastest and slowest number of PLCs are a compromise between speed and 
            noise
            Using TSP commands:
            To set NPLC, send the command smu.measure.nplc. For example, to set the NPLC value to 0.5 
            for voltage measurements, send the commands:
                smu.measure.func = smu.FUNC_DC_VOLTAGE
                smu.measure.nplc = 0.5 #Sets the measurement time to 0.0083 (0.5/60) seconds.
            To assign a different measure function, replace smu.FUNC_DC_VOLTAGE with one of the following:
            • For current measurements: smu.FUNC_DC_CURRENT
            • For resistance measurements: smu.FUNC_RESISTANCE

        FourWire:
            You can use 2-wire or 4-wire measurement techniques with the Model 2450.
            You should use 4-wire, or remote sense, measurement techniques for the following conditions:
            • Low impedance applications
            • When sourcing high current
            • When sourcing low voltage
            • When sourcing higher current and measuring low voltages
            • When enforcing voltage limits directly at the device under test (DUT)
            • When sourcing or measuring voltage in low impedance (less than 100 Ω) test circuits
            • When optimizing the accuracy for low resistance, voltage source, or voltage measurements
            
            You can use 2-wire, or local sensing, measurement techniques for the following source-measure 
            conditions: 
            • Sourcing and measuring low current. 
            • Sourcing and measuring voltage in high impedance (more than 1 kΩ) test circuits. 
            • Measure-only operation (voltage or current). 
            When you use 2-wire sensing, voltage is sensed at the output connectors. 
            You should only use 2-wire connections if the error contributed by test-lead IR drop is acceptable. 
            

            To change to 4-wire sensing, send these commands:
            smu.measure.func = smu.FUNC_DC_VOLTAGE
            smu.measure.sense = smu.SENSE_4WIRE
            To assign a different measure function, replace smu.FUNC_DC_VOLTAGE with one of the following:
            • For current measurements: smu.FUNC_DC_CURRENT
            • For resistance measurements: smu.FUNC_RESISTANCE

        Source and measure order:
            When you are using a remote interface, you should set the measure function first, then set the source 
            function, because setting the measure function may change the source function. This is not 
            necessary when you use the front-panel FUNCTION key to set the source and measure functions.
            Once you have set the source and measure functions, you can change other measure and source 
            settings as needed.
            When setting range, you should first set the limit (compliance) to a value higher than the measure 
            range you intend to set.

            Source and measure using TSP commands
            The TSP commands that set up the source functions begin with smu.source.
            The source commands are specific to each source function (voltage or current). For example, to set 
            the range to 100 mA for the current source function, you would send:
            smu.source.func = smu.FUNC_DC_CURRENT
            smu.source.range = .1
            To set the range to 20 V for the voltage function, you would send:
            smu.source.func = smu.FUNC_DC_VOLTAGE
            smu.source.range = 20

        Example: The TSP commands that set up the measurement functions begin with smu.measure.
            The sense commands are also specific to each measure function (voltage, current, or resistance). For 
            example, to set the NPLC cycles to 0.5 for the current measurement function, you would send:
                smu.measure.func = smu.FUNC_DC_CURRENT
                smu.measure.nplc = .5
            For the voltage measurement function, you would send:
                smu.source.func = smu.FUNC_DC_VOLTAGE
                smu.measure.nplc = .5
            For the resistance measurement function, you would send:
                smu.source.func = smu.FUNC_RESISTANCE
                smu.measure.nplc = .5
            To make a measurement, you set the measurement function and then send the 
            smu.measure.read() command. For example, to make a current measurement, send the 
            commands:
                smu.measure.func = smu.FUNC_CURRENT
                print(smu.measure.read())
            To make a voltage measurement, send the commands:
                smu.measure.func = smu.FUNC_DC_VOLTAGE
                print(smu.measure.read())
            To make a resistance measurement, send the commands:
                smu.measure.func = smu.FUNC_RESISTANCE
                print(smu.measure.read())

            
        Overvoltage protection:
            Overvoltage protection restricts the maximum voltage level that the instrument can source. It is in 
            effect when either current or voltage is sourced. This protects the device under test (DUT) from high 
            voltage levels. 
            For example, if a sense lead is disconnected or broken during a 4-wire sense measurement, the 
            instrument can interpret the missing sense lead as a decrease in voltage and respond by increasing 
            the source output. If overvoltage protection is set, the sourced output is not allowed to exceed the 
            overvoltage protection limit.
            The value set for overvoltage protection takes precedence over the source limit settings. When it is 
            enabled, it is always in effect.
            When overvoltage protection is set and the sourced voltage exceeds the setting:
            • The output is clamped at the overvoltage protection value
            • On the front panel, an indicator to the right of the voltage displays OVP
            When overvoltage protection is used in a test sequence, it should be set before turning the source on
            Set the source function and send the smu.source.protect.level command with the value of the 
            limit. For example, to set the overvoltage limit to 20 V for the voltage source function, send the 
            commands:
                smu.source.func = smu.FUNC_DC_VOLTAGE
                smu.source.protect.level = smu.PROTECT_20V
            
        Source limits:
            The source limits (also known as compliance) prevent the instrument from sourcing a voltage or 
            current over a set value. This helps prevent damage to the device under test (DUT).
            The values that can be set for the limits must be below the setting for the overvoltage protection limit.
            This limit can also be restricted by the measurement range. If a specific measurement range is set, 
            the limit must be more than 0.1 % of the measurement range. If not, an event is generated and the 
            limit is automatically changed to an appropriate value for the selected range. If you set the 
            measurement range to be automatically selected, the measurement range does not affect the limit.
            If you attempt to change the source limit to a value that is not appropriate for the selected source 
            range, the source limit is not changed and a warning is generated. You must change the source 
            range before you can select the new limit.
            The lowest allowable limit is based on the load and the source value. For example, if you are sourcing 
            1 V to a 1 kΩ resistor, the lowest allowable current limit is 1 mA (1 V/1 kΩ = 1 mA). Setting a limit 
            lower than 1 mA limits the source.
            For example, assume the following conditions:
            • Current limit 10 mA
            • Instrument sources a voltage of 10 V
            • DUT resistance of 10 Ω
            With a source voltage of 10 V and a DUT resistance of 10 Ω, the current through the DUT should be: 
            10 V / 10 Ω = 1 A. However, because the limit is set to 10 mA, the current will not exceed 10 mA, and 
            the voltage across the resistance is limited to 100 mV. In effect, the 10 V voltage source is 
            transformed into a 10 mA current source.
            In steady-state conditions, the set limit restricts the instrument output unless there are fast transient 
            load conditions.
            If the source output exceeds the source limit:
            • On the Home screen, LIMIT is displayed to the right of the source voltage.
            • The Source value changes to yellow.
            The source is clamped at the maximum limit value. For example, if the measurement limit is set to 1 V 
            and the measurement range is 2 V, the output voltage is clamped at 1 V.
            Using TSP commands:
            To set the limit when sourcing current, send the commands:
                smu.source.func = smu.FUNC_DC_CURRENT
                smu.source.vlimit.level = limitValue
            To set the limit when sourcing voltage, send the commands:
                smu.source.func = smu.FUNC_DC_VOLTAGE
                smu.source.ilimit.level = limitValue
            Where limitValue is the limit value
            

            



"""