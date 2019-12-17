#!/usr/bin/env python
import argparse
import tempfile
import queue
import sys

import sounddevice as sd
import soundfile as sf
import numpy as np  

import threading
import time

class record:
  def __init__(self):
    self.q = queue.Queue()
    self.is_recording = False
    self.record_condition = threading.Condition()
    self.sr = 44100
    self.signal = np.array(2*np.pi*np.sin(range(self.sr)), dtype=np.float)

  def callback(self, indata, frames, time, status):
      if status:
        print(status)
      self.q.put(indata.copy())

  def change_status(self, flag=None):
    if flag is None:
      self.is_recording = not self.is_recording
    else:
      self.is_recording = flag
 
  def record_handle(self):
    self.change_status()
    if self.is_recording == True:
      print("start recording")
    elif self.is_recording == False:
      print("stop recording")
      return
    else:
      print("some error happend")
      exit(1)

    self.change_status(True)
    th = threading.Thread(target = self.record_thread)
    th.start()
    # waiting change flag

  def record_thread(self):
    self.data = []
    cond = self.record_condition
    with cond: # cond.acquire() at start, cond.relase() at end
      with sd.InputStream(samplerate=44100,
                          channels=1,
                          callback=self.callback):
        while self.is_recording:
          self.data.append(self.q.get())
      self.data = np.concatenate(self.data,axis=0)
      self.signal = self.data.reshape(-1)
      print("done")
  
  def get_signal(self):
    with self.record_condition:
      return self.signal, self.sr

  def play(self, wait=False):
    sd.play(*self.get_signal())
    if wait:
      sd.wait()

if __name__ == "__main__":
  r = record()
  r.record_handle()
  time.sleep(3)
  r.record_handle()
  r.play(wait=True)
