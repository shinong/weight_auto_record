from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread,QTimer,pyqtSignal
from PyQt5.QtWidgets import QLineEdit,QDialog,QDialogButtonBox,QFormLayout
import mainwindow as gui
import os.path
from os import path
import serial
import serial.tools.list_ports
import csv
import re
from pdf import pdfWeightGen
from math import isclose

### this specifies the abslute path of the code, that will then be patch to 
# the subfolder path for readind and saving data
script_dir = path.dirname(__file__)
data_storage_path = 'data/'
db_storage_path = 'db/'
abs_file_path = path.join(script_dir,data_storage_path)
abs_db_path = path.join(script_dir,db_storage_path)


class mainWindow(QtWidgets.QMainWindow,gui.Ui_MainWindow):
    def __init__(self):
        super(mainWindow,self).__init__()
        self.setupUi(self)
        self.tableWidget.resizeColumnsToContents()
        self.allPorts = serial.tools.list_ports.comports()
        self.serialPortSelectInit()
        self.tableWidget.setRowCount(25)
        self.tableWidget.setColumnCount(4)
        self.exportButton.clicked.connect(self.saveData)
        self.list_all_files()
        self.fileSelect.activated.connect(self.tableUpdate)
        self.threadStatus = False
        self.startButton.clicked.connect(self.threadInit)
        self.stopButton.clicked.connect(self.threadEnd)
        self.measurementStatus = None
        self.checkData()
        self.pdfGen.clicked.connect(self.pdfGenerate)

    def serialPortSelectInit(self):
        self.comPortSelect.addItems([p.device for p in self.allPorts])

    # get all the files in data dir, and list them in the fileSelect combobox
    def list_all_files(self):
        for (dirpath,dirnames,filenames) in os.walk(abs_file_path):
            for i in range(len(filenames)):
                filenames[i] = filenames[i].split('.')[0]
        self.fileSelect.addItems(filenames)

    # this func read the weight data from csv file and update on the Qtableweight
    def tableUpdate(self):
        #this parameter records which weight has been measured, has values of 0,1,2,3
        # (0:nothing measured, 1:dry cell, 2:loaded cell, 3:all done)
        self.measurementStatus = 0
        self.tableWidget.clear()
        self.read_filename = abs_file_path + self.fileSelect.currentText() + '.csv'
        templist = fileIO(self.read_filename).readFile()
        if len(templist) != 25:
            print('error, sample number does not match')
        elif len(templist[0]) == 1:
            for i in range(25):
                self.tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(templist[i][0]))
        elif len(templist[0]) == 2:
            for i in range(25):
                self.tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(templist[i][0]))
                self.tableWidget.setItem(i,1,QtWidgets.QTableWidgetItem(templist[i][1]))
                self.measurementStatus = 1
        elif len(templist[0]) == 3:
            for i in range(25):
                self.tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(templist[i][0]))
                self.tableWidget.setItem(i,1,QtWidgets.QTableWidgetItem(templist[i][1]))
                self.tableWidget.setItem(i,2,QtWidgets.QTableWidgetItem(templist[i][2]))
                self.measurementStatus = 2
        elif len(templist[0]) == 4:
            for i in range(25):
                self.tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(templist[i][0]))
                self.tableWidget.setItem(i,1,QtWidgets.QTableWidgetItem(templist[i][1]))
                self.tableWidget.setItem(i,2,QtWidgets.QTableWidgetItem(templist[i][2]))
                self.tableWidget.setItem(i,3,QtWidgets.QTableWidgetItem(templist[i][3]))
                self.measurementStatus = 3
        else:
            print('error, please check the csv file')
    
    def saveData(self):
        # when the cell is empty, it will return none, however, delete the cell content
        # from the QtableWidget does not work for this(still return true)
        #filename = self.fileSelect.currentText() + '.csv'
        tempList = []
        firstColCheck = self.tableWidget.item(0,0)
        secondColCheck = self.tableWidget.item(0,1)
        thirdColCheck = self.tableWidget.item(0,2)
        fourthColCheck = self.tableWidget.item(0,3)
        if (fourthColCheck != None):
            for i in range(25):
                tempList.append([self.tableWidget.item(i,0).text(),self.tableWidget.item(i,1).text(),self.tableWidget.item(i,2).text(),self.tableWidget.item(i,3).text()])
        elif (fourthColCheck == None) & (thirdColCheck != None):
            for i in range(25):
                tempList.append([self.tableWidget.item(i,0).text(),self.tableWidget.item(i,1).text(),self.tableWidget.item(i,2).text()])
        elif (thirdColCheck == None) & (secondColCheck != None):
            for i in range(25):
                tempList.append([self.tableWidget.item(i,0).text(),self.tableWidget.item(i,1).text()])
        elif (secondColCheck == None) & (firstColCheck != None):
            for i in range(25):
                tempList.append([self.tableWidget.item(i,0).text()])           
        elif (firstColCheck == None):
            print('empty form')
            return 0
        else:
            print('error, pleaes check the from')
            return 0
        fileIO(self.read_filename).saveFile(tempList)
        print('data saved to' + self.fileSelect.currentText())
    
    def threadInit(self):
        if not self.threadStatus:
            self.thread = scaleSignal(self.comPortSelect.currentText())
            self.thread.dataChanged.connect(self.fillCell)
            self.thread.start()
            self.posIndex = 0
            self.threadStatus = True

    def threadEnd(self):
        if self.threadStatus:
            self.thread.terminate()
            self.threadStatus = False
    
    #this function fill the weight received from the serial port and fill the str into the cell
    # the fucniton is triggered by the serial thread signal
    def fillCell(self,data):
        if self.measurementStatus != None and self.measurementStatus <3 and self.posIndex <25:
            print('connected')
            data = re.findall("\d+\.\d+",data)[0]
            print(data)
            '''
            if self.fileSelect.text()[0] == 'p':
                if data == self.PrunBuffer[self.posIndex][0]:
                    print('matched!')
                else:
                    print('not matched!')
            else:
                if data == self.JRunBuffer[self.posIndex][0]:
                    print('matched!')
                else:
                    print('not matched!')
            '''
            self.tableWidget.setItem(self.posIndex,self.measurementStatus+1,QtWidgets.QTableWidgetItem(data))
            self.posIndex = self.posIndex+1
        else:
            print('error,file might not be slected or all weight are already measured!')

    # this funciton will update the backgournd color of the cell by comparing the values 
    def setColor(self,value_a,value_b,position1,position2,tolerance):
        if isclose(value_a,value_b,abs_tol=tolerance):
            self.tableWidget.item(position1,position2).setBackground(QtGui.QColor('green'))
        else:
            self.tableWidget.item(position1,position2).setBackground(QtGui.QColor('green'))
    
    def checkData(self):
        # this function read the prestored dry cell weight and temporayly save them to the lists
        #  for later comparison with the current measured weights 
        JFilePath = db_storage_path+'JRun.csv'
        PFilePath = db_storage_path+'PRun.csv'
        self.JRunBuffer = fileIO(JFilePath).readFile()
        self.PrunBuffer = fileIO(PFilePath).readFile()
    
    def pdfGenerate(self):
        templist = fileIO(self.read_filename).readFile()
        if len(templist) == 25 and len(templist[0])==4 and len(templist[24]) ==4:
            pdfWeightGen(templist)
            print('weight data generated to file'+self.read_filename)
        else:
            print(len(templist),len(templist[0]),len(templist[24]))
            print('error! table might not complete')
        

class fileIO():
    def __init__(self,filePath):
        if not path.exists(filePath):
            print('file not exists')
        self.path = filePath
    
    #save the weight data readed from the Qtableweight to the csv files,
    # data is passed in as list, and path is passed by self.path    
    def saveFile(self,saveData):
        with open(self.path,'w',newline='') as f:
            writer = csv.writer(f)
            for row in saveData:
                writer.writerow(row)
        f.close()

    #read sample number and prestored weight info, and pass them to the 
    #Qtable as list of lists, read from csv files 
    def readFile(self):
        temp_list = []
        with open(self.path,newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                temp_list.append(row)
        f.close()
        return temp_list

class scaleSignal(QThread):
    dataChanged = pyqtSignal(str)
    def __init__(self,serialPort):
        QThread.__init__(self)
        self.scale = serial.Serial(serialPort,baudrate = 9600,bytesize=serial.SEVENBITS,parity=serial.PARITY_ODD,timeout=1)

    def __del__(self):
        self.wait()
    
    def run(self):
        self.scale.close()
        self.scale.open()
        self.scale.flush()
        self.scale.reset_input_buffer()

        while True:
            while self.scale.inWaiting == 0:
                pass
            try:
                data = self.scale.readline().decode()
                self.scale.reset_input_buffer()
                if len(data) !=0:
                    self.dataChanged.emit(data)
            except(KeyboardInterrupt,SystemExit,IndexError,ValueError):
                pass


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = mainWindow()
    w.show()
    sys.exit(app.exec_())
