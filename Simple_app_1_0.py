#########
#Simple json testdata Edit/View/Export application
#A code test by Andy Wedell March 2023
#########
import sys
import re
import pandas as pd
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QValidator
from PyQt6.uic import loadUi



class Main(QMainWindow):
    
    #Constructs GUI imported from Qt Designer file
    def __init__(self):
        super(Main, self).__init__()
        loadUi("app_gui.ui", self)
        
        #set column delegates
        self.d0 = stringDelegate()
        self.d1 = ageDelegate()
        self.d2 = sizeDelegate()
        self.d3 = shoeDelegate()
        self.d4 = availDelegate()
        self.tableView.setItemDelegateForColumn(0, self.d0)
        self.tableView.setItemDelegateForColumn(1, self.d1)
        self.tableView.setItemDelegateForColumn(2, self.d0)
        self.tableView.setItemDelegateForColumn(3, self.d2)
        self.tableView.setItemDelegateForColumn(4, self.d2)
        self.tableView.setItemDelegateForColumn(5, self.d3)
        self.tableView.setItemDelegateForColumn(6, self.d4)
        self.tableView.setItemDelegateForColumn(7, self.d0)

        #Title, lineedit, and button action pointers
        self.setWindowTitle('Actor Data Editor')
        self.fileSource.clear()
        self.openFile.clicked.connect(self.open_File)
        self.openFile.clicked.connect(self.getData)
        self.actionSave.triggered.connect(self.saveData)

#To do status bar

#To do dark mode

    #Opens file from application directory
    def open_File(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'JSON files (*.json)')
        self.fileSource.setText(file_name)
        if file_name == '':
            return 0

    #Points data from file to pandas dataframe simultaneously setting table model
    def getData(self):
        if self.fileSource.text():
            urlSource = self.fileSource.text()
            with open(urlSource, "r") as f:
                data = f.read()
                if not data:
                    #no data
                    self.statusbar.showMessage("Error: File contains no data.")
                    return
                if data:
                    self.Tdf = pd.read_json(urlSource)
                if 'actors' in self.Tdf:
                    #parses temporary dataframe pointer to pandasModel
                    self.df = pd.DataFrame(self.Tdf['actors'].tolist())
                    # print(self.df)
                    # PandasModel to tableView
                    self.model = PandasModel(self.df)
                    self.tableView.setModel(self.model)
                    self.tableView.resizeColumnsToContents()
                else:
                    #missing key
                    self.statusBar().showMessage('Error: File missing expected data structure')
        else:
            #no file
            self.statusbar.showMessage("Open a file")
            return
    
    def saveData(self):
        data = {"actors": self.df.to_dict(orient='records')}

        file_path, _ = QFileDialog.getSaveFileName(None, 'Save file', '', 'JSON Files (*.json)')
    
        if file_path != '':
            with open(file_path, 'w') as f:
                f.write(pd.DataFrame.from_dict(data).to_json(indent=4))



#Delegates for tableView and Model
#column delegate for editing string values
class stringDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._block_set_editor_data = False

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        if self._block_set_editor_data:
            return
        value = index.data(Qt.ItemDataRole.EditRole)
        editor.setText(str(value))

    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def block_set_editor_data(self, block):
        self._block_set_editor_data = block

    def validate(self, value, index):
        if not value:
            return (QValidator.State.Invalid, "Value cannot be empty")
        else:
            return (QValidator.State.Acceptable, "")


#column delegate for editing age values
class ageDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setMinimum(1)
        editor.setMaximum(100)
        return editor
    
    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        spinBox = editor
        if value is not None:
            spinBox.setValue(int(value))
     
    def setModelData(self, editor, model, index):
        value = editor.value()
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def validate(self, value, index):
        if not value.isValid():
            return (QValidator.State.Invalid, "Value is not valid")
        elif value.toInt()[0] < 1 or value.toInt()[0] > 100:
            return (QValidator.State.Invalid, "Value should be between 1 and 100")
        else:
            return (QValidator.State.Acceptable, "")


#column delegate for editing size values
class sizeDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(["XL", "L", "M", "S", "XS"])
        return editor

    def validate(self, text):
        pattern = re.compile("[XSLM]{1,2}")
        return bool(pattern.match(text))

    def setEditorData(self, editor, index):
        comboBox = editor
        text = index.model().data(index, Qt.ItemDataRole.EditRole)
        tindex = comboBox.findText(text)
        comboBox.setCurrentIndex(tindex)

    def setModelData(self, editor, model, index):
        comboBox = editor
        text = comboBox.currentText()
        if self.validate(text):
            model.setData(index, text, Qt.ItemDataRole.EditRole)
        else:
            pass


#column delegate for editing shoe size
class shoeDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        shoe_size = pd.concat([pd.Series([i, i+0.5]) for i in range(7, 16)])
        for size in shoe_size:
            editor.addItem(str(size))
        return editor
    
    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        comboBox = editor
        shindex = comboBox.findText(str(value))
        comboBox.setCurrentIndex(shindex) 
    
    def setModelData(self, editor, model, index):
        comboBox = editor
        text = comboBox.currentText()
        model.setData(index, float(text), Qt.ItemDataRole.EditRole)

    def validate(self, value, index):
        if not value.isValid():
            return (QValidator.State.Invalid, "Value is not valid")
        elif value.tofloat()[0] < 7 or value.tofloat()[0] > 16:
            return (QValidator.State.Invalid, "Value should be between 7 and 16")
        else:
            return (QValidator.State.Acceptable, "")


class availDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QCheckBox(parent)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        print(value)
        if value is None:
            value = False
        else:
            value = value.lower() == 'true'
        editor.setChecked(value)

    def setModelData(self, editor, model, index):
        if editor.isChecked():
            model.setData(index, 'True', Qt.ItemDataRole.EditRole)
        else:
            model.setData(index, 'False', Qt.ItemDataRole.EditRole)


#Pandas model through QAbstractTableModel
class PandasModel(QAbstractTableModel):
    
    #model constructor for a tableView with pandas dataframe
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df

    #return rows from dataframe
    def rowCount(self, parent=QModelIndex):
        return self._df.shape[0]

    #returns columns from dataframe
    def columnCount(self, parent=QModelIndex):
        return self._df.shape[1]

    #defines data in table cells    
    def data(self, index, role):
       if role == Qt.ItemDataRole.DisplayRole or role ==Qt.ItemDataRole.EditRole:
            try: value = self._df.iloc[index.row(), index.column()]
            except IndexError:
                #print(f"Invalid index: ({index.row()}, {index.column()})")
                return "" 
            if value is not None:
                print(value)
                #for int, float, bool data types temp 
                return str(value)
       return None
       
    #returns dataframe index into horizontal and vertical header data
    def headerData(self, col, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return str(self._df.columns[col])
        return None
    
    #Edits cell data
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            #print('Edit Role:', index.row(), index.column())
            #view selected cell index coordinates in terminal.

            if not value:
                return False
        
        #add data validation here.
            self._df.iloc[index.row(), index.column()] = value
            #print(value)
            #view new value in terminal
            self.dataChanged.emit(index, index)
        return True

    #flags for editing all cells
    def flags(self, index):
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    
    sys.exit(app.exec())