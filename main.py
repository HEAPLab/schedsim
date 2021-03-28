# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView, QAction, QToolBar
from PySide2.QtGui import QIcon
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Slot, Signal

import re
import Scheduler
import Task
import numpy as np
import SchedIo

def ShowErrorBox(errorStr):
    messageBox=QMessageBox()
    messageBox.setWindowTitle('Error')
    messageBox.setIcon(QMessageBox.Critical)
    messageBox.setText(errorStr)
    messageBox.show()
    return messageBox

def isIdLegit(id, tasks):
    for task in tasks:
        if task.id == id:
            return False
    return True


class AddNewDialog(QDialog):
    signal_task = Signal(object)

    def __init__(self, parent, tasks, deadlineNeeded):
        super(AddNewDialog, self).__init__(parent)
        self.tasks = tasks
        self.deadlineNeeded = deadlineNeeded
        self.load_ui()

    def appendActionListeners(self):
        self.window.okBtn.clicked.connect(self.createTask)
        self.window.cancelBtn.clicked.connect(self.close)

    def createTask(self):
        errorStr = ''
        try:
            id = int(self.window.idInput.text().strip())
            error = False
            if self.newTask and not isIdLegit(id, self.tasks):
                error = True
                errorStr += 'Id is not unique'
            deadlineInput = self.window.deadlineInput.text().strip()
            deadlineOk = False
            if len(deadlineInput) == 0 and not self.deadlineNeeded:
                deadline = -1
                deadlineOk = True
            else:
                deadline = int(deadlineInput)
            wcet = int(self.window.wcetInput.text().strip())
            period = int(self.window.periodInput.text().strip())
            if wcet > period:
                error = True
                if len(errorStr) > 0:
                    errorStr += '\n'
                errorStr += 'WCET is greater than period'
            if deadline != -1 and deadline < wcet:
                error = True
                if len(errorStr) > 0:
                    errorStr += '\n'
                errorStr += 'Deadline is earlier than WCET'
            if id < 0 or wcet <= 0 or period <= 0 or (not deadlineOk
                                                      and deadline <= 0):
                error = True
                if len(errorStr) > 0:
                    errorStr += '\n'
                errorStr += 'All fields must hold a positive value'
        except ValueError:
            error = True
            if len(errorStr) > 0:
                errorStr += '\n'
            errorStr += 'All the fields must hold a numeric value'
        if error:
            self.error_dialog=ShowErrorBox(errorStr)
        else:
            newTask = Task.Task(id, wcet, period, deadline)
            self.signal_task.emit(newTask)
            self.close()

    def suggestedId(self):
        i = -1
        valid = False
        while valid is False:  # no do while in python
            i += 1
            valid = True
            for task in self.tasks:
                if task.id == i:
                    valid = False
                    break
        return i

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "adddialog.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, self)
        ui_file.close()
        self.appendActionListeners()

    def new(self):
        self.setWindowTitle('Add task')
        self.newTask = True
        self.window.idInput.setText(str(self.suggestedId()))

    def edit(self, task):
        self.setWindowTitle('Edit task')
        self.newTask = False
        self.window.idInput.setText(str(task.id))
        self.window.idInput.setEnabled(False)
        self.window.periodInput.setText(str(task.period))
        if task.deadline == -1:
            self.window.deadlineInput.setText('')
        else:
            self.window.deadlineInput.setText(str(task.deadline))
        self.window.wcetInput.setText(str(task.wcet))


class SchedSim(QMainWindow):
    def __init__(self):
        super(SchedSim, self).__init__()
        self.resize(1000, 800)
        self.load_ui()
        self.setWindowTitle('SchedSim')
        self.tasks = []

    def runScheduler(self):
        schedClass = Scheduler.schedulers[
            self.window.schedulersDropdown.currentIndex()]
        deadlineDefined = True
        if schedClass.deadlineNeeded:
            for task in self.tasks:
                if task.deadline == -1:
                    deadlineDefined = False
                    break
        if deadlineDefined:
            if schedClass.isFeasible(self.tasks):
                sched = schedClass(self.tasks)
                try:
                    sched.execute(int(self.window.endTimeInput.text()))
                    self.confirm_dialog = QMessageBox()
                    self.confirm_dialog.setIcon(QMessageBox.Information)
                    self.confirm_dialog.setWindowTitle('Success')
                    self.confirm_dialog.setText("out.txt succesfully written")
                    self.confirm_dialog.show()
                except Exception as e:
                    self.error_dialog=ShowErrorBox("Cannot write output file:\n" +
                    str(e))
            else:
                self.error_dialog=ShowErrorBox("Schedule not feasible")
        else:
            self.error_dialog=ShowErrorBox('All deadlines must be defined for selected scheduler')

    def updateEndTimeInput(self):
        if self.window.majorCycleCB.checkState() and len(self.tasks) > 0:
            periods = []
            for task in self.tasks:
                periods.append(task.period)
            a = np.array(periods)
            self.window.endTimeInput.setValue(np.lcm.reduce(a))

    @Slot(object)
    def addTask(self, task):
        if (isIdLegit(task.id, self.tasks)):
            self.tasks.append(task)
            rowCt = self.window.tableWidget.rowCount()
            self.window.tableWidget.insertRow(rowCt)
            self.window.tableWidget.setItem(rowCt, 0,
                                            QTableWidgetItem(str(task.id)))
            self.window.tableWidget.setItem(rowCt, 1,
                                            QTableWidgetItem(str(task.wcet)))
            self.window.tableWidget.setItem(rowCt, 2,
                                            QTableWidgetItem(str(task.period)))
            if task.deadline == -1:
                self.window.tableWidget.setItem(rowCt, 3, QTableWidgetItem(''))
            else:
                self.window.tableWidget.setItem(
                    rowCt, 3, QTableWidgetItem(str(task.deadline)))
            self.updateEndTimeInput()
            if not self.window.runBtn.isEnabled():
                self.window.runBtn.setEnabled(True)
            if not self.window.exportSched.isEnabled():
                self.window.exportSched.setEnabled(True)

    @Slot(object)
    def editTask(self, task):
        for count in range(0, len(self.tasks)):
            if task.id == self.tasks[count].id:
                self.window.tableWidget.setItem(
                    count, 1, QTableWidgetItem(str(task.wcet)))
                if task.deadline == -1:
                    self.window.tableWidget.setItem(count, 3,
                                                    QTableWidgetItem(''))
                else:
                    self.window.tableWidget.setItem(
                        count, 3, QTableWidgetItem(str(task.deadline)))
                self.window.tableWidget.setItem(
                    count, 2, QTableWidgetItem(str(task.period)))
                self.tasks[count] = task
                self.updateEndTimeInput()
                break

    def ShowNewDialog(self):
        self.addDialog = AddNewDialog(
            self, self.tasks, Scheduler.schedulers[
                self.window.schedulersDropdown.currentIndex()].deadlineNeeded)
        self.addDialog.new()
        self.addDialog.signal_task.connect(self.addTask)
        self.addDialog.show()

    def ShowEditDialog(self):
        if len(self.window.tableWidget.selectedRanges())>0:
            self.addDialog = AddNewDialog(
                self, self.tasks, Scheduler.schedulers[
                    self.window.schedulersDropdown.currentIndex()].deadlineNeeded)
            r = self.window.tableWidget.selectedRanges()[0]
            dn = r.bottomRow()
            up = r.topRow()
            if dn == up:
                self.addDialog.edit(self.tasks[dn])
                self.addDialog.signal_task.connect(self.editTask)
                self.addDialog.show()

    def removeTask(self):
        if len(self.window.tableWidget.selectedRanges())>0:
            r = self.window.tableWidget.selectedRanges()[0]
            dn = r.bottomRow()
            up = r.topRow()
            for count in range(dn, up - 1, -1):
                self.window.tableWidget.removeRow(count)
            del self.tasks[up:dn + 1]
            self.updateEndTimeInput()
            if len(self.tasks) == 0:
                if self.window.runBtn.isEnabled():
                    self.window.runBtn.setEnabled(False)
                if self.window.exportSched.isEnabled():
                    self.window.exportSched.setEnabled(False)

    def initSchedulerDropdown(self, window):
        for i in Scheduler.schedulers:
            window.schedulersDropdown.addItem(i.name)

    def majorCycleCBStatusChange(self):
        if self.window.majorCycleCB.checkState():
            self.window.endTimeInput.setEnabled(False)
            self.updateEndTimeInput()
        else:
            self.window.endTimeInput.setEnabled(True)

    def importSchedule(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('Task set (*.xml)')
        dialog.setViewMode(QFileDialog.List)
        if dialog.exec_():
            fileName = dialog.selectedFiles()
            if len(fileName)>0:
                self.tasks = []
                self.window.tableWidget.clearContents()
                for i in range(self.window.tableWidget.rowCount() - 1, -1, -1):
                    self.window.tableWidget.removeRow(0)
                try:
                    SchedIo.importFile(fileName[0], self.addTask)
                except Exception as e:
                    self.error_dialog=ShowErrorBox("Cannot parse selected file:\n" +
                                          str(e))

    def exportSchedule(self):
        if len(self.tasks)>0:
            fileNameArr = QFileDialog.getSaveFileName(self, 'Export task set', '', "Task set (*.xml)")
            print(fileNameArr)
            if len(fileNameArr)>0:
                fileName=fileNameArr[0]
                if len(fileName)>0:
                    exp = re.compile('.*\.xml$', re.IGNORECASE)
                    if not (exp.match(fileName)):
                        fileName += '.xml'
                    try:
                        SchedIo.exportFile(self.tasks, fileName)
                    except Exception as e:
                        self.error_dialog=ShowErrorBox("Writing error:\n" + str(e))
        else:
            self.error_dialog=ShowErrorBox("Add a task before exporting the task set")

    def appendActionListeners(self, window):
        window.addTask.triggered.connect(self.ShowNewDialog)
        window.removeTask.triggered.connect(self.removeTask)
        window.editTask.triggered.connect(self.ShowEditDialog)
        window.majorCycleCB.stateChanged.connect(self.majorCycleCBStatusChange)
        window.runBtn.clicked.connect(self.runScheduler)
        window.importSched.triggered.connect(self.importSchedule)
        window.exportSched.triggered.connect(self.exportSchedule)

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, self)
        ui_file.close()

        tb = self.addToolBar("Tasks")
        self.window.addTask = QAction(QIcon("add.bmp"), "Add", self)
        self.window.removeTask = QAction(QIcon("remove.bmp") ,"Remove", self)
        self.window.editTask = QAction(QIcon("edit.bmp"), "Edit", self)
        self.window.importSched = QAction(QIcon("import.bmp"), "Import", self)
        self.window.exportSched = QAction(QIcon("export.bmp"), "Export", self)

        tb.addAction(self.window.addTask)
        tb.addAction(self.window.removeTask)
        tb.addAction(self.window.editTask)
        tb.addAction(self.window.importSched)
        tb.addAction(self.window.exportSched)

        self.initSchedulerDropdown(self.window)
        self.appendActionListeners(self.window)
        self.window.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

if __name__ == "__main__":
    app = QApplication([])
    widget = SchedSim()
    widget.show()
    sys.exit(app.exec_())
