from cryptography.fernet import Fernet
import random  as rd
import string,os
import sounddevice as sd
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

source_file=""

def live_audio():
    global source_file
    # Recording duration
    freq = 44100
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
    source_file="C:\\Users\\vamsi\\Desktop\\Audio Encryption\\Test1\\live_recorded.wav"
    write(source_file, freq, recording)

    # Convert the NumPy array to audio file
    # wv.write("recording1.mp3", recording, freq, sampwidth=2)
    # print("File saved")

def plot_decrypted(file):
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True
    fs,data=wavfile.read(file)
    plt.plot(data)
    plt.title("Decrypted audio output")
    # data_1=np.asarray(data,dtype=np.int32)
    plt.ylabel("Amplitude")
    plt.xlabel("Time")
    plt.show()

#encryption 
def encrypt(original_audio_file_path ,encrypted_file_path , key):

    fernet=Fernet(key)
    print("Encrypting audio...")
    with open(original_audio_file_path,'rb') as file: #location of voice file to be encrypted
        originalaudio=file.read()

    encrypted=fernet.encrypt(originalaudio)

    with open(encrypted_file_path,'wb') as encrypted_file: #location of newly created voice file after encryption
        encrypted_file.write(encrypted)
    print("Encryption complete")
    #the encryption audio file is not playable , since all the audio content is encrypted , software apps cannot read the actual data 
    # plot_encrypted(encrypted_file_path)

#decryption
def decrypt(encrypted_file_path ,decrypted_file_path , key):
    print("Decrypting the ciphered file...")
    fernet=Fernet(key)

    with open(encrypted_file_path,'rb') as enc_file: #location of newly created voice file to be decrypted
        encrypted=enc_file.read()

    decrypted =fernet.decrypt(encrypted)

    with open(decrypted_file_path,'wb') as dec_file: #location of newly created voice file after decrypted
        dec_file.write(decrypted)
    plot_decrypted(decrypted_file_path)
    print("File Decrypted")
def generate_key():
    random_letters_list=[str(rd.randrange(0,9)) for i in range(32)]
    k="".join(random_letters_list)
    # print(type(k))
    return k.encode('UTF-8')
    alphabet_string = string.ascii_lowercase
    print(random_letters_list,os.urandom(32))

def plot_original(file):
    # print(file)
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True
    fs,data=wavfile.read(file)
    plt.plot(data)
    plt.title("Original audio input")
    plt.ylabel("Amplitude")
    plt.xlabel("Time")
    # data_1=np.asarray(data,dtype=np.int32)
    plt.show()

choice=int(input("Encrypt using\n1.Live Record\n2.Existing audio\n"))
key=Fernet.generate_key()
source_file='C:\\Users\\vamsi\\Desktop\\Audio Encryption\\Test1\\test.m4a'
if choice==1:
    live_audio()
plot_original(source_file)
encrypt(source_file,'C:\\Users\\vamsi\\Desktop\\Audio Encryption\\Test1\\encrypted.wav', key)
decrypt('C:\\Users\\vamsi\\Desktop\\Audio Encryption\\Test1\\encrypted.wav', 'C:\\Users\\vamsi\\Desktop\\Audio Encryption\\Test1\\decrypted.wav', key)


#Generating the key

