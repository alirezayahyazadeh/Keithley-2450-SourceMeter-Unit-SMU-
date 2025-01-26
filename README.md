# Keithley 2450 SMU Automation Library

## Overview
This repository contains Python scripts to automate the usage of the Keithley 2450 SourceMeter Unit (SMU) for various test and measurement scenarios. Due to restrictions on publishing client-specific code, only the original library and general-purpose scripts are provided.

The library simplifies interaction with the Keithley 2450 for applications such as:

- **Sourcing and Measuring**: Automates sourcing of voltage/current while measuring corresponding values (e.g., current, voltage, resistance, or power).  
- **Sweeps**: Performs linear or logarithmic sweeps for voltage or current measurements.  
- **Configuration and Calibration**: Manages advanced settings, buffers, and calibration routines.  
- **Data Export and Visualization**: Exports results for analysis and provides visualization tools.  

---

## Features
- **Device Communication**: Interface with the Keithley 2450 using PyVisa.
- **Measurement Automation**: Automates voltage/current sweeps and captures measurement data.
- **Configurable Operations**: Supports 2-wire/4-wire sensing, user-defined buffers, and advanced measurement limits.
- **Data Export and Visualization**: Exports measurement results to CSV files and visualizes them with built-in plots.
- **Error Handling**: Robust mechanisms for managing device communication and runtime errors.

---

## Installation

### **Requirements**
- Python 3.8+
- Required Python libraries:
  - `pyvisa`
  - `pandas`
  - `matplotlib`
  - Any additional dependencies listed in the `requirements.txt` file.

### **Setup**
1. Clone the repository:
   ```bash
   git clone https://github.com/alirezayahyazadeh/Keithley-2450-SourceMeter-Unit-SMU-

   cd keithley-2450-automation
File Descriptions
Main Scripts
Model2450.py:
Contains the core class KeithleyDeviceManager, which wraps device communication and automation functionalities.

Key methods include:
Initialization
Device connection tests
Buffer management
Measurement operations (voltage/current sourcing, resistance measurement)
main.py:
Demonstrates how to use the library to perform various tests, such as:

Voltage/current sweeps
Resistance measurement
Logging and exporting results
Supplementary Functions
Helper Functions:
Include utilities for data formatting, file management, and plotting (found in supplementary functions and related modules).
Usage
Basic Workflow
Connect to the Device:
Use the KeithleyDeviceManager class to establish a connection.


from Model2450 import KeithleyDeviceManager

KDM = KeithleyDeviceManager(
    "USB0::XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX::INSTR",
    EstablishConnectionTest=True
)
Initialize the Device:
Configure the Keithley 2450 device with desired parameters.


KDM.Initialize(
    Source_VoltageRange=20,
    Source_CurrentRange=1,
    Measure_VoltageRange=10,
    Measure_CurrentRange=1,
    Current_Limit=1,
    Voltage_limit=20
)
Perform Measurements:
Example: Voltage sweep with current measurement.


KDM.Sweep_LinearcaseByPoints_Voltage(
    ArbitraryConfigurationName='TestConfig',
    startValue=0.1,
    stopValue=5,
    pointsToMeasure=10,
    delayTime=0.01
)
Save Results:
Results can be exported as CSV files and visualized using built-in plotting utilities.

Running the Scripts
To execute main.py and test the functionality:

python main.py
Contribution
Contributions to improve the library or add new features are welcome! Submit a pull request or raise
