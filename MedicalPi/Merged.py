#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pyaudio
import numpy as np
import wave
import os
import datetime


# In[ ]:


now = datetime.datetime.now()
filename = 'Wave_File_' + str(now)[:10] + now.strftime("_%H_%M_%S.wav")


# In[ ]:


#The following code comes from markjay4k as referenced below
chunk = 512
samp_rate = 44100

form_1 = pyaudio.paInt16
chans = 1

record_secs = 20     #record time
dev_index = 2
wav_output_filename = filename


# In[ ]:


p = pyaudio.PyAudio()


# In[ ]:


#setup audio input stream
stream = p.open(format = form_1,
                  rate=samp_rate,
                  channels=chans, 
                  input_device_index = dev_index, 
                  input=True, 
                  frames_per_buffer=chunk)

# the code below is from the pyAudio library documentation referenced below
#output stream setup
player = p.open(format = form_1,
                rate=samp_rate,
                channels=chans, 
                output=True, 
                frames_per_buffer=chunk)


# In[ ]:


print("Broadcasting & Recording")
frames = []

for ii in range(0,int((samp_rate/chunk)*record_secs)):
    data = stream.read(chunk,exception_on_overflow = False)
    frames.append(data)
    
    data_numpy = np.fromstring(data, dtype=np.int16)
    player.write(data_numpy, chunk)

print("Finished recording")


# In[ ]:


stream.stop_stream()
stream.close()
audio.terminate()


# In[ ]:


#creates wave file with audio read in
#Code is from the wave file audio tutorial as referenced below
wavefile = wave.open(wav_output_filename,'wb')
wavefile.setnchannels(chans)
wavefile.setsampwidth(audio.get_sample_size(form_1))
wavefile.setframerate(samp_rate)
wavefile.writeframes(b''.join(frames))
wavefile.close()


# In[ ]:


#plays the audio file
os.system("aplay " + filename)

