import util
import numpy as np
import pickle
from argparse import ArgumentParser
from keras.utils import to_categorical
from threading import Thread
import os.path
import math

# config
config = util.read_config()
saveName = 'recent'
DISPLAYS = config['displays']

# args
parser = ArgumentParser(description="carl loves you")
parser.add_argument('-a', "--append", help="data file to append to")
args = parser.parse_args()

# globals
running = True
paused = False

def listen_to_input():
    global paused
    global running

    print("type 'quit' to exit")
    while running:
        command = input("")
        if(command == "quit"):
            print("exiting...")
            running = False
        else:
            print(f"unknown command '{command}'")

def record_observation(start_frames, start_displays, nTimesteps):
    # record the user while he uses the displays
    print("\trecording...")

    videos = start_frames.tolist()
    displays = start_displays.tolist()
    video = []

    for i in range(nTimesteps):
        frame = util.get_frame()
        video.append(frame)

    while running:
        frame = util.get_frame()
        display = util.get_display()
        
        video.insert(0, frame)
        video = video[:-1] # pop
        videos.append(np.asarray(video))
        
        displayId = DISPLAYS.index(display)
        displays.append(displayId)

    videos = np.asarray(videos)
    displays = np.asarray(displays)

    print("\tdone")
    return videos, displays

def collect_data(start_x, start_y):
    nTimesteps = config['timesteps']
    width = config['resize']['width']
    height = config['resize']['height']

    # collect data of the user looking at the monitor
    waiting = Thread(target=listen_to_input)
    waiting.daemon = True
    waiting.start()
    
    (x_train, y_train) = record_observation(start_x, start_y, nTimesteps)

    # reshape
    x_train = np.reshape(x_train, [-1, nTimesteps, width, height, 1]) # box last item
    y_train = to_categorical(y_train, num_classes=len(DISPLAYS)) # one-hot encoding (turn into matrix)

    return (x_train, y_train)

if __name__ == '__main__':
    # setup - disable printing extra details
    np.set_printoptions(threshold=np.inf, linewidth=np.inf)

    # import
    print("loading data..")
    start_x = np.empty(0)
    start_y = np.empty(0)
    if args.append:
        saveName = args.append
        if os.path.isfile(f"data/{saveName}.xdata"): # file exists
            (start_x, start_y) = util.get_data(saveName)
    print("\tdone")
    
    # collect
    (x, y) = collect_data(start_x, start_y)

    print('shapes')
    print(x.shape)
    print(y.shape)

    # save
    util.save_data(saveName, x, y)

