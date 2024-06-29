# import required libraries
import sounddevice as sd
from scipy.io.wavfile import write
# import wavio as wv

#Temp

# Sampling frequency
freq = 44100

# Recording duration

duration = int(input("Enter the required duration to record the audio   "))

# Start recorder with the given values
# of duration and sample frequency
print("Recording audio....")
recording = sd.rec(int(duration * freq),samplerate=freq, channels=2)

# Record audio for the given number of seconds
sd.wait()

# This will convert the NumPy array to an audio
# file with the given sampling frequency
# print(recording[0],len(recording))
print("Saving the recorded audio in a file")
write("recording0.mp3", freq, recording)

# Convert the NumPy array to audio file
# wv.write("recording1.mp3", recording, freq, sampwidth=2)
# print("File saved")
