import sys

sys.path.append("..")
print(sys.path)

import time
import threading 
import simpleaudio as sa

#misha: im adding this due to path issues 
import sys
sys.path.append('/home/real-timegratitude/Desktop/openai-realtime-console/blossom-public')
from blossompy import Blossom

import random

# import server stuff
from flask import Flask, request
import threading

import sseclient
import requests
from server_class import FlaskServerWrapper

movements = {	"exhale": [40, 1],
    			"inhale": [100,1]}
IDLE_SEQUENCES = ["exhale", "inhale"]

bl = Blossom(sequence_dir = "../blossompy/src/sequences")
bl.connect()
bl.load_sequences

start_time = -1
audio_length = 0

current_state = -1
state_lock = threading.Lock()  # Ensures thread-safe access

last_state = None # this stores the last state to check if there has been an update

def play_sequence_idle(sequence_name):
    print("Playing sequence:", sequence_name)
    bl.motor_goto("all",movements[sequence_name][0],movements[sequence_name][1])
    time.sleep(0.5)

def breathe():
    time1 = time.perf_counter()     # Start time of idle sequence
    test_seq = 0
    while True:
        time2 = time.perf_counter()
        
        # If 5 seconds have passed, play next idle sequence
        if time2 - time1 > 2:
            play_sequence_idle(IDLE_SEQUENCES[test_seq])
            test_seq = (test_seq + 1) % len(IDLE_SEQUENCES)
            time1 = time.perf_counter()

def demo():
    filename = "../blossompy/media/amazon_demo/Breathing_Exercise_1.wav"
    wave_obj = sa.WaveObject.from_wave_file(filename)
    # wave_obj.play()
    bl.do_sequence("amazon_demo/Breathing_Exercise_1")
    print("breathing 1")


listening = False

listen_seq = [
    lambda: (bl.motor_goto('tower_1',60, 1), bl.motor_goto('tower_2', 60, 1), bl.motor_goto('tower_3', 60, 1), time.sleep(1)),
    lambda: (bl.motor_goto('tower_1',5, 1), time.sleep(1)),
    lambda: (bl.motor_goto('tower_1',60, 1), time.sleep(1)),
    lambda: (bl.motor_goto('tower_1',5, 1), time.sleep(1))
]


# sequences written in this format so they can be looped by the code in the main function
idle = True

idle_seq = [
    lambda: (bl.motor_goto('all', 75, 2), time.sleep(2)),
    lambda: (bl.motor_goto('all', -5, 2), time.sleep(2))
]

speak_seq = [
    lambda: (bl.motor_goto('tower_1',60, 1), bl.motor_goto('tower_2',60, 1), bl.motor_goto('tower_3',60, 1), time.sleep(1)),
    lambda: (bl.motor_goto('tower_3',20,1), time.sleep(1)),
    lambda: (bl.motor_goto('tower_1',60, 1), bl.motor_goto('tower_2',60, 1), bl.motor_goto('tower_3',60, 1), time.sleep(1)),
    lambda: (bl.motor_goto('tower_2',20,1), time.sleep(1))
]


# this function does pulls the next movement from the idle_seq sequence or speak_seq sequence
# this will loop the sequence depending on the current listening/speaking state
def listen_speak():
    i = 0
    j = 0
    k = 0
    while True:
        current_time = time.perf_counter()
        print(listening)
        # incorporate idle breathing sequence when a certain time elapses with no state listening after speaking
        
        
       
        if idle: 
            print("idle")
            # active listening nodding
            idle_seq[i]()
            i = (i+1) % 2
        elif listening:
            print("listening")
            # active listening nodding
            listen_seq[i]()
            i = (i+1) % 4
        else:
            print("speaking")
            if audio_length != -1 and current_time - start_time >= audio_length:
                listening = True
                i = 0
                audio_length = -1
            # head tilts for speaking
            speak_seq[j]()
            j = (j+1) % 4
        
        
def calculateAudioLength(tokens):
    SECONDS_PER_TOKEN = 0.04896
    return tokens * SECONDS_PER_TOKEN


if __name__ == "__main__":
    server_obj = FlaskServerWrapper()
    server_obj.run() # this runs the Flask server wrapper that contains the information in a queue

    i = 0
    j = 0
    k = 0
    while True:
        print(current_state)
        print(type(current_state))
        current_state = server_obj.current_state # get the current state from the server object
        current_time = time.perf_counter()
        if current_state != last_state:
            last_state = current_state
            
            if type(current_state) == dict:
                if current_state["type"] == 'start':                    
                    start_time = time.perf_counter() # updates start time of speaking
                    audio_length = -1 
                    idle = False
                    listening = False
                elif current_state["type"] == 'tokens':
                    audio_length = calculateAudioLength(current_state['data'])
                #new edit
                elif current_state['type'] == 'listen':
                    listening = True 
                    idle = False
                #new edit 
                else: 
                    print("bad request")
            
                
        
        print(listening, "audio_length:", audio_length, "start_time:", start_time)
        # incorporate idle breathing sequence when a certain time elapses with no state listening after speaking
        
        #misha edit
        
        # if idle: 
        #     print("idle")
        #     # active listening nodding
        #     idle_seq[i]()
        #     i = (i+1) % 2
        # elif listening: 
        #     print("listening")
        #     # active listening nodding
        #     listen_seq[i]()
        #     i = (i+1) % 4
        # else:
        #     print("speaking")
        #     if audio_length != -1 and current_time - start_time >= audio_length:
        #         listening = False
        #         idle = True
        #         audio_length = -1
        #     # head tilts for speaking
        #     speak_seq[j]()
        #     j = (j+1) % 4

        if idle:
            if len(idle_seq) > 0:
                i = i % len(idle_seq)  # Ensure `i` is within range BEFORE using it
                print("idle")
                idle_seq[i]()
                i = (i+1) % len(idle_seq)  # Move to the next sequence safely
            else:
                print("Error: idle_seq is empty!")  # Debugging in case it happens


        elif listening and len(listen_seq) > 0:
            print("listening")
            listen_seq[i]()
            i = (i+1) % len(listen_seq)  # Ensure `i` does not exceed valid range

        else:
            print("speaking")
            if audio_length != -1 and current_time - start_time >= audio_length:
                listening = False
                idle = True
                audio_length = -1

            if len(speak_seq) > 0:  # Ensure valid index range
                speak_seq[j]()
                j = (j+1) % len(speak_seq)  # Ensure `j` does not exceed valid range
            else:
                print("Error: speak_seq is empty!")

