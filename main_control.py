#!/usr/bin/env python
import librosa
import librosa.display
import sounddevice as sd
import numpy as np
import os

import display.display as display
import record
import record.record_tools
import record.ui

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
                QWidget, QAction, QTabWidget,
                QVBoxLayout, QMessageBox, QHBoxLayout, QGroupBox, QLabel
                ,QWidget,QFormLayout,QInputDialog,QFileDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt, QUrl,QFileInfo

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QDesktopWidget
from PyQt5.QtGui import QIcon

import inspect

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class App(QMainWindow):
  def __init__(self):
    super().__init__()
    self.title = "Voice Conversion App"
    self.left = 0
    self.top = 0
    self.width = 1300
    self.height = 700
    self.filename = ''
    self.setWindowTitle(self.title)
    self.setGeometry(self.left, self.top, self.width, self.height)
    self.center()
    
    self.central_widget = QWidget()
    self.layout = QHBoxLayout(self.central_widget)

    self.speaker_widget = display.SignalDisplayWidget(self, "Speaker")
    self.convert_widget = display.SignalDisplayWidget(self, "Convert")

    self.control_panel  = QGroupBox("Control Panel")
    self.build_control_widget() # will create self.control_widget
   
    self.left_group = QGroupBox("Speaker")
    self.left_group_layout = QHBoxLayout(self.left_group)

    self.left_group_layout.addWidget(self.speaker_widget)
    self.left_group_layout.addWidget(self.convert_widget)
    self.left_group_layout.addWidget(self.control_widget)
    self.layout.addWidget(self.left_group)
    self.layout.addWidget(self.convert_widget)
    
    self.control_items["Load"].clicked.connect(lambda: self.load_callback())
    self.control_items["Record"].clicked.connect(lambda: self.record_callback())
    self.control_items["Convert"].clicked.connect(lambda: self.convert_callback())
    # self.control_items["test"].clicked.connect(lambda: self.load_callback())

    self.setCentralWidget(self.central_widget)
    self.show()

  def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
        (screen.height() - size.height()) / 2)
    
  def build_control_widget(self):
    self.control_widget = QWidget()
    self.control_layout = QVBoxLayout()
    self.control_items = dict()
    CI = self.control_items
    # Label
    CI["Label"] = QLabel("==Sound==")
    # Push Buttons
    button_names = ["Load", "Record", "Convert"]
    # button_names = ["Load", "Record", "Convert","test"]
    for _name in button_names:
      CI[_name] = QPushButton(_name, self)
    
    for _, item in CI.items():
       self.control_layout.addWidget(item)
    self.control_layout.addStretch(1)
    self.control_widget.setLayout(self.control_layout)

  def load_callback(self):
    song, _ = QFileDialog.getOpenFileName(self, "Open Song", "~", "Sound Files (*.mp3 *.ogg *.wav *.m4a)")
    url = QUrl.fromLocalFile(song)
    self.filename = QFileInfo(song).fileName()
    self.speaker_widget.load_audio(QFileInfo(song).fileName())
  
  def record_callback(self):
    signal, sr = record.ui.record_dialog()
    self.speaker_widget.set_audio(signal, sr)
    self.filename = 'record.wav'
    librosa.output.write_wav(self.filename, signal, sr)

  def convert_callback(self):
    source = self.filename
    print (source)
    # hps, ok = QInputDialog.getText(self, 'convert detail',
    #     'hps:')
    model, _ = QFileDialog.getOpenFileName(self, "Open Model", "model.pkl", "Model Files (*.pkl)")
    model = QFileInfo(model).fileName()
    # source, ok = QInputDialog.getText(self, 'convert detail',
    #     'source:')
    target, ok = QInputDialog.getText(self, 'target',
        'target(1-150):')
    # output, ok = QInputDialog.getText(self, 'output',
    #     'output:')

    open_convert = "python test.py -m ",model," -s ",source," -t ",target,' -o ','result.wav'
    def converTuple(tup):
        str_ = ''.join(tup)
        return str_
    str_ = converTuple(open_convert)
    os.system(str_)
    self.convert_widget.load_audio('result.wav')

    if self.filename == 'record.wav':
        os.remove('record.wav')
        print('removed record')
    else:
        os.remove('result.wav')
        print('removed result')
    

if __name__ == "__main__":
  app = QApplication(sys.argv)
  ex = App()
  sys.exit(app.exec_())
