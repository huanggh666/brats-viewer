import zipfile
import os
import win32clipboard
import win32con
from PyQt5 import QtCore, QtGui, QtWidgets
from glob import glob

from textviewer_ui import Ui_Form


class W1(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
    
        self.pushButton_1.released.connect(self.file_open_on_botton)

        self.setAcceptDrops(True)
        self.filename = ''
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
             event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            self.filename = event.mimeData().urls()[0].toLocalFile()
            self.open_file(self.filename)

    def file_open_on_botton(self):
        file_dir = "F:\Xvalidation\\a3"
        if self.filename:
            (file_dir, file_name) = os.path.split(self.filename)
            
        open_filename = QtWidgets.QFileDialog.getOpenFileName(
                    self, "打开", file_dir, 'zip和txt(*.zip *.txt)')
        if open_filename[0] != '':
            self.filename = open_filename[0].replace('\\', '/')
            self.open_file(self.filename)

    def open_file(self, filename):
        if filename.endswith('.zip'):
            self.text, self.num = get_mean_dice_from_zip(filename)
            self.show_text_of_zip()
            self.textBrowser.append(f'file: {filename}')
        elif filename.endswith('.txt'):
            self.text_ls = get_mean_dice_from_txt(filename)
            self.show_text_of_txt()
            self.textBrowser.append(f'file: {filename}')
        elif os.path.isdir(filename):
            filenames = glob(f'{filename}/Results*.zip')
            if len(filenames):
                self.open_file(filenames[0])
            else:
                self.textBrowser.setText(
                            f"No zip file is found in the {filename}!!!")

    def show_text_of_zip(self):
        if self.text is None:
            self.textBrowser.setText("No dice value is found !!!")
        else:
            self.text = "#---ET\tWT\tTC\n" + self.text
            self.textBrowser.setText(self.text)
            self.textBrowser.append('\n')
            self.textBrowser.append(f'The total samples is {self.num}.')
            self.textBrowser.append('\n')
            self.textBrowser.append('The info had been copied !')

    def show_text_of_txt(self):
        if len(self.text_ls) < 1:
            self.textBrowser.setText("No dice value is found !!!")
        else:
            text_ls = []
            for x in self.text_ls:
                if x not in text_ls:
                    text_ls.append(x)
            self.textBrowser.setText(''.join(text_ls))

def set_text_to_clipboard(info):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, info)
    win32clipboard.CloseClipboard()

def get_mean_dice_from_zip(zip_name):
    if not os.path.isfile(zip_name):
        return None
    myzip = zipfile.ZipFile(zip_name)
    # fcsv = myzip.open('Stats_Validation_final.csv')
    fcsv = [x for x in myzip.namelist() if x.endswith('.csv')]
    if len(fcsv) < 1: 
        return None
    if len(fcsv) >= 2:
        fcsv = [x for x in fcsv if 'validation' in x.lower()]
    lines = myzip.read(fcsv[0]).splitlines()
    
    num = 0
    for line in lines:
        line = line.decode('utf-8')
        if 'Mean' in line[:5]:
            line_ls = line.split(',')[1:]
            line_text = '\t'.join(line_ls)
            set_text_to_clipboard(line_text)
        if 'Brats1' == line[:6]:
            num += 1
    return line_text, num

def get_mean_dice_from_txt(txt_name):
    with open(txt_name, 'r') as ftxt:
        lines = [x for x in ftxt.readlines() if ('mean' in x or 'model' in x)]
    return lines