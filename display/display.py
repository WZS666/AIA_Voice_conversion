#!/usr/bin/env python
import librosa
import librosa.display
import sounddevice as sd
import numpy as np

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
                QWidget, QAction, QTabWidget,
                QVBoxLayout, QMessageBox, QHBoxLayout, QGroupBox, QLabel, QFileDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt, QCoreApplication

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon

import inspect

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class App(QMainWindow):

  def __init__(self):
    super().__init__()
    self.title = 'Display Sample'
    self.left = 0
    self.top = 0
    self.width = 800
    self.height = 800
    self.setWindowTitle(self.title)
    self.setGeometry(self.left, self.top, self.width, self.height)
    
    self.table_widget = SignalDisplayWidget(self, label="Just A Label")
    self.setCentralWidget(self.table_widget)

    self.show()
    
class SignalDisplayWidget(QWidget):

  def __init__(self, parent, label=""):
    super(QWidget, self).__init__(parent)
    self.layout = QVBoxLayout(self)
    self.buttom_widget = QWidget()
    self.buttom_layout = QHBoxLayout(self.buttom_widget)
    
    self.tabs = QTabWidget()
    (self.tab_waveform,
     self.plt_waveform) = self.add_tab("Wave",
                                     tip="Original Wave Form")
    (self.tab_rms,
     self.plt_rms)      = self.add_tab("RMS",
                                     tip="Root Mean Square")
    (self.tab_mel,
     self.plt_mel)      = self.add_tab("Mels",
                                     tip="Mel Spectral")
    (self.tab_mfcc,
     self.plt_mfcc)     = self.add_tab("MFCCs",
                                     tip="Mel-Frequency Cepstrum")

    self.play_button = QPushButton("Play", self)
    self.play_button.clicked.connect(self.play_audio)
    self.save_button = QPushButton("Save", self)
    self.save_button.clicked.connect(self.save_audio)

    if __name__ == "__main__":
      try:
        self.load_audio()
      except:
        pass

    self.total_time_label = QLabel("Total Time:")
    self.buttom_layout.addWidget(self.total_time_label)
    self.buttom_layout.addStretch(1)
    self.buttom_label = QLabel(label)
    self.buttom_layout.addWidget(self.buttom_label)

    self.buttom_layout.addStretch(1)
    self.buttom_layout.addWidget(self.save_button)
    self.buttom_layout.addWidget(self.play_button)


    self.layout.addWidget(self.tabs)
    self.layout.addWidget(self.buttom_widget)
    
    self.setLayout(self.layout)

  # ==========inner functions================================= 
  def add_tab(self, name, tip = None):
    tab = QWidget()
    self.tabs.addTab(tab, name)
    if tip:
      tab.setToolTip(tip)

    painter = PlotCanvas(tab)
    return tab, painter

  def set_audio(self, signal, sr):
    self.signal = signal
    self.sr = sr
    self.process_all()

  def load_audio(self, path=None):
    if path is None:
      options = QFileDialog.Options()
      options |= QFileDialog.DontUseNativeDialog
      path, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileNames()",
                                             "","wav Files (*.wav);;All Files (*)",
                                             options=options)
      print(path)
      if path:
        self.load_audio(path=path)
      else:
        print("you do not select anything")
      return
    self.signal, self.sr = librosa.core.load(path)
    self.process_all()
    return

  def record_audio(self,sr=44100):
    QMessageBox.about(self, "Record Audio", "Not Implement Yet") 
    pass

  def save_audio(self):
    file_name = self.buttom_label.text()+".wav"
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()",file_name,
                    "Wav Files (*.wav)", options=options)
    if fileName:
      print(fileName)
      librosa.output.write_wav(fileName, self.signal, self.sr)

  def process_all(self):
    self.process_sound()
    self.process_images()
    return

  def process_sound(self):
    try:
        self.rms = librosa.feature.rms(S=librosa.stft(self.signal)).reshape(-1)

        self.mels = librosa.feature.melspectrogram(self.signal, sr=self.sr)
        self.log_mels = librosa.power_to_db(self.mels, ref=np.max)

        self.mfccs = librosa.feature.mfcc(self.signal, sr=self.sr)
    except:
        print(f'function: "{inspect.currentframe().f_code.co_name}" fail')

  def process_images(self):
    canvas_list = [self.plt_waveform,
                   self.plt_rms,
                   self.plt_mel,
                   self.plt_mfcc]
    for c in canvas_list:
      c.axes.cla()
    
    self.plt_rms.axes.plot(self.rms)
    plt.setp(self.plt_rms.axes.get_xticklabels(), visible=False)
    self.plt_rms.axes.tick_params(axis='both', which='both', length=0)

    librosa.display.waveplot(self.signal, sr=self.sr,
                    ax=self.plt_waveform.axes)
    librosa.display.specshow(self.log_mels, x_axis='time',
                    y_axis='mel', ax=self.plt_mel.axes)
    librosa.display.specshow(self.mfccs, x_axis='time',
                    ax=self.plt_mfcc.axes)
    for c in canvas_list:
      c.draw()
  #====================funciton callbacks================
  @pyqtSlot()
  def play_audio(self):
    sd.play(self.signal, self.sr)

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

if __name__ == "__main__":
  audio_path = "./sample.wav"
  
  app = QApplication(sys.argv)
  ex = App()
  sys.exit(app.exec_())
