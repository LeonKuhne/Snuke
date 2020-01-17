import util
import time
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Conv2D, BatchNormalization, Dense, MaxPooling2D, Flatten, LSTM, Embedding
from keras.layers.convolutional_recurrent import ConvLSTM2D
from keras.utils import to_categorical
from keras.optimizers import RMSprop, Adam
from keras.callbacks import EarlyStopping, TensorBoard
from keras.backend.tensorflow_backend import set_session
from sklearn.model_selection import train_test_split
from argparse import ArgumentParser

# args
parser = ArgumentParser(description="carl promises to be good boy")
parser.add_argument('-f', '--file', help="file to save to, otherwise uses recent")
parser.add_argument('-l', '--log', help="log comment, default is timestamp")
parser.add_argument('-e', '--epochs', help="specify num of epochs")
parser.add_argument('-lr', '--learning_rate', help="specify learning rate")
args = parser.parse_args()

# config
config = util.read_config()
nTimesteps = config['timesteps']
width = config['resize']['width']
height = config['resize']['height']
learning_rate = config['learning_rate']
BATCH_SIZE = 1

# parse args
name = "recent"
log_comment = int(time.time())
epochs = config['epochs']
if args.file:
    name = args.file
if args.log:
    log_comment = args.log
if args.epochs:
    epochs = int(args.epochs)
if args.learning_rate:
    learning_rate = float(args.learning_rate)

# logging
model_name = f"carl-{config['type']}:{config['version']}-{name}-{epochs}-{learning_rate}-{log_comment}"
tensorboard = TensorBoard(log_dir=f"logs/{model_name}")

# get the data
(x, y) = util.get_data(name)
print('Raw Data:')
print(x.shape)
print(y.shape)

# create validation and training set
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=7, test_size=0.2) #cnn
#x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=False) #rnn

# print some neat details
print('Training Data:')
print(x_train.shape)
print(y_train.shape)

print('Validation Data:')
print(x_test.shape)
print(y_test.shape)


# create the model
model = Sequential()
# filters is number of segments (of picture), kernal_size is the size of the filter
# input shape: num sequences, timesteps, data dimension
input_shape = (None, nTimesteps, width, height, 1)
model.add(ConvLSTM2D(filters=32, kernel_size=(3,3), activation='relu', batch_input_shape=input_shape, return_sequences=True))
for i in range(3):
    model.add(BatchNormalization())
    #model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(ConvLSTM2D(2**(i+6), (3, 3), activation='relu', return_sequences=True))
model.add(BatchNormalization())
model.add(Flatten())
#model.add(LSTM(128))
model.add(Dense(128, activation='relu'))
model.add(Dense(len(config['displays']), activation='softmax'))

# compile
optimizer = RMSprop(lr=learning_rate)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy']) #cnn
#model.compile(loss='categorical_crossentropy', optimizer='RMSprop', metrics=['accuracy']) #rnn


# train
#cbk_early_stopping = EarlyStopping(monitor='val_acc', mode='max')
#model.fit(x_train, y_train, epochs=100, validation_data=(x_test, y_test), callbacks=[cbk_early_stopping])
for i in range(epochs):
    history = model.fit(x_train, y_train, epochs=i, batch_size=BATCH_SIZE, validation_data=(x_test, y_test), callbacks=[tensorboard])
    model.save("backups/{model_name}.model")

# show loss
plt.plot(history.history['loss'])
plt.show()

model.save(f"models/{model_name}.model")
model.save(f"recent.model")

isDone = False
while not isDone:
    makeDefault = input('update carl (y,n)? ')
    if(makeDefault == 'y'):
        model.save("carl.model")
        isDone = True
    elif(makeDefault == 'n'):
        isDone = True

