import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np




def GenerateTimeDateString(separator:str='_', fillthegap:bool=True):
    """
    returns the date and time

    Args:
        separator (str, optional): use this separator to separate day, month, year also hour, minute, second. Defaults to '_'.
    Args:
        fillthegap (bool, optional): True: use '_' between the date and time. False: use white-space. If False it is recommended to use '/' as separator. Defaults to 'True'.
    Returns:
        _type_: _description_
    """
    if(fillthegap):
        return time.strftime(f'%d{separator}%m{separator}%Y_%H{separator}%M{separator}%S', time.localtime())
    return time.strftime(f'%d{separator}%m{separator}%Y %H{separator}%M{separator}%S', time.localtime())

def calculat_Ma(listOfCurrents):
    
    j = [i / 1000 for i in listOfCurrents]
    return j
def calculat_J(listOfCurrents,cm2):
    
    j = [i / cm2  for i in listOfCurrents]
    return j

def Calculate_Log(listToConvert):
    result = None
    NewList = []
    for value in listToConvert:
        if (value< 0):
            result = -1*np.log10(-1*value)
        else:
            result = np.log10(value)
        NewList.append(result)
    return NewList

class fileManagement():
    #defaultFullPath:str = "C:/Hiwi/result_";

    def __init__(self) -> None:
        #self.defaultFullPath = "C:/Hiwi/result_"+GenerateTimeDateString()
        pass

    def SaveToDrive(self, directoryPath:str= 'D:\\HiWi', filename = 'result', fileType:str='xlsx', inputList:dict={'value':'None'}, 
                    WantAlsoALogFile:str=False, authorName:str='', extraDescription:str='',):
        #Check if the directory does not exist, create it
        fullPath = directoryPath + "\\" + filename + "_" + GenerateTimeDateString()
        savePath = fullPath + '.' + fileType
        dataFrame1 = pd.DataFrame(inputList)
        fileType = fileType.lower()
        if (fileType == "xlsx"):
            dataFrame1.to_excel(savePath, header=True, index=False, engine='xlsxwriter')

        elif (fileType == "csv"):
            dataFrame1.to_csv(savePath, header=True, index=False)

        if (WantAlsoALogFile):
            header1 = self.__MakeLogHeader(AuthorName=authorName, extraDescription= extraDescription)
            header1 += '\n' + dataFrame1.to_string(index=False)
            header1 += '\n'
            logPath = fullPath + '.txt'
            with open(logPath, 'w') as f:
                f.write(header1)

    def __MakeLogHeader(self, AuthorName='NONE', extraDescription=None):
            header = '====================================================================\n'
            header += f'Date: {GenerateTimeDateString(separator="/",fillthegap=False)}'
            header += '\n'
            header += f'Author: {AuthorName}'
            if (extraDescription is not None):
                header += '\n' + extraDescription
            header += '\n===================================================================\n'
            return header

class Plots(object):
    defaultFullPath:str = "C:/Hiwi/";
    defaultFileName:str = "result_";
    def __init__(self) -> None:
        self.defaultFullPath = "C:/Hiwi/"
        self.defaultFileName = "result_"+ GenerateTimeDateString()
     
    
    def Plot(self, X_AxisData, X_AxisCaption,Y_AxisData, Y_AxixCaption, X_AxisData1, X_AxisCaption1, Y_AxisData1, Y_AxixCaption1, title = 'Source Voltage - Measure current',
             _plotType = 'line', _isPlotShown = True,
             _isSaveToDirectory = False, _fileType = 'png', _directory = defaultFullPath, _fileName= defaultFileName):
    
        #fig = plt.subplot()
        #ax1 = plt.Axes(fig=fig)
        plt.figure(figsize=(12,6))
        plt.subplot(1, 2, 1)
        plt.plot(X_AxisData,Y_AxisData,marker='o',linestyle='-',color='b')
        plt.xlabel(X_AxisCaption)
        plt.ylabel(Y_AxixCaption, color='r')
        plt.title(title)
        plt.grid(True)
        
        
        plt.subplot(1, 2, 2)
        plt.plot(X_AxisData1,Y_AxisData1,marker='o',linestyle='-',color='r')
        plt.xlabel(X_AxisCaption1)
        plt.ylabel(Y_AxixCaption1, color='r')
        plt.title(title)
        plt.grid(True)

        plt.tight_layout()
        plt.show()
           
    """        
    def TwinAxisPlot(self, commonAxisData, commonAxisCaption,
                    leftAxisData, leftAxixCaption, rightAxisData, rightAxisCaption, title = 'Source Voltage - Measure current',
                    _plotType = 'dot' , _isPlotShown = True,
                    _isSaveToDirectory = False, _fileType = 'png', _directory= defaultFullPath, _fileName= defaultFileName
                    ):
        
        fig, ax1 = plt.subplots()

        color_r = 'tab:red'
        ax1.set_xlabel(commonAxisCaption)
        ax1.set_ylabel(leftAxixCaption, color=color_r)
        #ax1.plot(commonAxisData, leftAxisData, color=color_r)


        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        color_b = 'tab:blue'
        ax2.set_ylabel(rightAxisCaption, color=color_b)  # we already handled the x-label with ax1
        if (_plotType.lower() == 'dot'):
            ax1.scatter(commonAxisData, leftAxisData, color=color_r)
            ax2.scatter(commonAxisData, rightAxisData, color=color_b)
        elif(_plotType.lower() == 'line'):
            ax1.plot(commonAxisData, leftAxisData, color=color_r)
            ax2.plot(commonAxisData, rightAxisData, color=color_b)

        plt.grid(True, axis='y')
        plt.grid(True, axis='x')
        plt.title(title)
        fig.tight_layout()  # otherwise the right y-label is slightly clipped

        if (_isSaveToDirectory):
            pathtosave = _directory + _fileName + '.' + _fileType
            plt.savefig(pathtosave)
        if (_isPlotShown):
            plt.show()
            
    """
             
    def Plot_with_multiInput(self,):
        pass
    


    # ... (other methods)
