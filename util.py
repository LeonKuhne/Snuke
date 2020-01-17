import numpy as np
import json
import cv2
import pickle
from freenect import sync_get_depth as get_depth
from subprocess import check_output


def read_config():
    with open('config.json', 'r') as json_file:
        return json.load(json_file)

config = read_config()

def get_file(filename):
    print(f"reading from file: data/{filename}")
    with open(f"data/{filename}", 'rb') as f:
        return pickle.load(f)

def save_file(filename, npArr):
    print(f"saving to file: data/{filename}")
    with open(f"data/{filename}", 'wb') as f:
        pickle.dump(npArr, f)

def get_data(name):
    x = get_file(f"{name}.xdata")
    y = get_file(f"{name}.ydata")
    return x, y

def save_data(name, x, y):
    save_file(f"{name}.xdata", x)
    save_file(f"{name}.ydata", y)

def get_frame():
    frame_data = get_depth()
    frame = frame_data[0] # get current frame from connect
    timestamp = frame_data[1]

    frame = np.clip(frame, frame_clip_min, frame_clip_max)
    frame = frame - frame_clip_min
    frame = cv2.resize(frame, dsize=(frame_width, frame_height)) # resize the image to 28x28
    frame = frame/(frame_clip_max-frame_clip_min) # scale each depth between 0-1
    return frame

def get_display():
    jsonStr = check_output(['swaymsg', '-r', '-t', 'get_workspaces'])
    jsonDisplay = json.loads(jsonStr)
    for display in jsonDisplay:
        if(display['focused']):
            return display['output']

def frame_batch(timesteps):
    batch = []
    for i in range(timesteps):
        batch.append(get_frame())
    batch = np.asarray(batch)
    return batch

if __name__ == '__main__':
    print(get_display())
