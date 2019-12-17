#!/usr/bin/env python
try:
  from . import record_tools
except:
  import record_tools

import librosa
import librosa.display
import sounddevice as sd
import numpy as np

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
                QWidget, QAction, QTabWidget,
                QVBoxLayout, QMessageBox, QHBoxLayout, QGroupBox, QLabel, QFileDialog,
                QDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt, QCoreApplication

import inspect

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class App(QMainWindow):

  def __init__(self):
    super().__init__()
    self.title = 'record'
    self.setWindowTitle(self.title)
    
    self.widget = record_widget(self) 
    self.setCentralWidget(self.widget)

    self.show()


def record_dialog():
  d = QDialog()
  w = record_widget(d)
  d.setLayout(w.layout)
  d.setWindowModality(Qt.ApplicationModal)
  d.exec_()
  return w.get_signal()
  
class record_widget(QWidget):

  def __init__(self, parent):
    super(QWidget, self).__init__(parent)
    self.title = 'record'
    self.recorder = record_tools.record()
    self.layout = QHBoxLayout(self)

    self.record_button = self.create_record_button()
    self.play_button = self.create_play_button()

    self.layout.addWidget(self.record_button)
    self.layout.addWidget(self.play_button)

  def create_record_button(self):
    record_button = QPushButton("record", self)
    record_button.clicked.connect(self.record_backend)
    return record_button
  
  def create_play_button(self):
    play_button = QPushButton("Play", self)
    play_button.clicked.connect(self.recorder.play)
    return play_button
  
  def record_backend(self):
    self.recorder.record_handle()
    button_string = "record" if self.recorder.is_recording == False\
                           else\
                    "recording"

    button_color = "black" if self.recorder.is_recording == False\
                           else\
                   "red"
    self.record_button.setText(button_string)
    self.record_button.setStyleSheet(f"color:{button_color}")

  def get_signal(self):
    signal, sr = self.recorder.get_signal()
    return signal, sr

if __name__ == "__main__":
  audio_path = "./sample.wav"
  
  app = QApplication(sys.argv)
#  ex = App()
#  x = app.exec_()
#  print(ex.widget.get_signal())
  print(record_dialog())
  sys.exit(0)
