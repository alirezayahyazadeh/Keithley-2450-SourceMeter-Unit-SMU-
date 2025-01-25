Keithley 2450 SMU Automation Library
Overview

I have a restriction on publishing the client's project code, so I only upload the original file and cannot post the entire project.
This repository contains Python scripts to automate the usage of the Keithley 2450 SourceMeter Unit (SMU) for various test and measurement scenarios. The library simplifies interaction with the device for applications such as:

Sourcing voltage/current while measuring corresponding values (current, voltage, resistance, or power).
Performing sweep operations (linear, logarithmic) to measure voltage or current.
Configuring device settings, managing buffers, and calibrating measurements.
Exporting results for analysis and visualization.
Features
Device Communication: Interface with the Keithley 2450 via PyVisa.
Measurement Automation: Automates voltage/current sweeps and captures measurement data.
Configurable Operations: Support for 2-wire/4-wire sensing, user-defined buffers, and advanced measurement limits.
Data Export and Visualization: Export measurement results to CSV files and visualize them with plots.
Error Handling: Robust mechanisms for managing device communication and runtime errors.
Installation
Requirements
Python 3.8+
Required Python libraries:
pyvisa
pandas
matplotlib
Any additional dependencies listed in the requirements.txt file
Setup
Clone this repository:

git clone https://github.com/your-username/keithley-2450-automation.git
cd keithley-2450-automation
Install dependencies:

pip install -r requirements.txt
File Descriptions
Main Scripts
Model2450.py: Contains the core class KeithleyDeviceManager, which wraps device communication and automation functionalities.
Methods include initialization, device connection tests, buffer management, and measurement operations (voltage/current sourcing, resistance measurement).
main.py: Demonstrates how to use the library to perform various tests, such as:
Voltage/current sweeps
Resistance measurement
Logging and exporting results
Supplementary Functions
Helper Functions: Include utilities for data formatting, file management, and plotting (found in suplemenaryFunctions and related modules).
Usage
Basic Workflow
Connect to the Device:


from Model2450 import KeithleyDeviceManager
KDM = KeithleyDeviceManager("USB0::XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX::INSTR", EstablishConnectionTest=True)
Initialize the Device:

KDM.Initialize(
    Source_VoltageRange=20,
    Source_CurrentRange=1,
    Measure_VoltageRange=10,
    Measure_CurrentRange=1,
    Current_Limit=1,
    Voltage_limit=20
)
Perform Measurements: Example: Voltage Sweep with Current Measurement:


KDM.Sweep_LinearcaseByPoints_Voltage(
    ArbitraryConfigurationName='TestConfig',
    startValue=0.1,
    stopValue=5,
    pointsToMeasure=10,
    delayTime=0.01
)
Save Results: Results can be exported as CSV and visualized using built-in plotting utilities.

Running the Scripts
To execute main.py and test the functionality:


python main.py
Contribution
Contributions to improve the library or add new features are welcome! Submit a pull request or raise an issue in this repository.
