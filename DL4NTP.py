import tensorflow as tf
from tensorflow import keras
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import datetime as dt
import time
import csv
import seaborn as sns
from datetime import datetime, date
import keras.backend as K
from tensorflow.keras.layers import Bidirectional
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import TimeDistributed
from tensorflow.keras.models import Sequential
from keras.preprocessing.sequence import TimeseriesGenerator
from numpy import array
from numpy import cumsum
from pandas.tseries.holiday import USFederalHolidayCalendar
from random import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import GridSearchCV
from keras.wrappers.scikit_learn import KerasClassifier


def readData(filename):
    print('Reading dataset...')
    with open(filename) as f:
        SANReN = f.readlines()
    return SANReN


def loadData(filename1, filename2):
    filenames = [filename1, filename2]
    with open('SANREN.txt', 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                outfile.write(infile.read(30000)+"\n")


def preprocess(data, inputs):
    '''
    Preprocesses the data.
    '''
    headings_line = data[0].split()
    # Merge 'Src', 'IP', and 'Addr:Port'
    headings_line[4:7] = [''.join(headings_line[4:7])]
    # Merge 'Dst', 'IP', and 'Addr:Port'
    headings_line[5:8] = [''.join(headings_line[5:8])]
    # Remove 'Flags', 'Tos', and 'Flows'.
    headings_line = headings_line[0:6] + headings_line[8:13]

    # Clean time-series data points.
    framedata = []
    print('Preprocessing data...')
    for i in range(1, inputs):
        data_line = data[i].split()
        #print(data_line)
        #print(i)

        if (data_line[0] == 'Summary:') or (data_line[0] == 'Time') or (data_line[0] == 'Total') or (data_line[0] == 'Date') or (data_line[0] == 'Sys:') or (len(data_line) < 15):
            pass

        else:
            if ((data_line[11] == "M" or data_line[11] == 'G') and (data_line[13] == 'M' or data_line[13] == 'G') and (data_line[15] == 'M' or data_line[15] == 'G')):
                if (data_line[11] == 'G'):
                    data_line[10] = float(data_line[10])*100000000
                else:
                    data_line[10] = float(data_line[10])*1000000
                if (data_line[13] == 'G'):
                    data_line[12] = float(data_line[12])*100000000
                else:
                    data_line[12] = float(data_line[12])*1000000
                if (data_line[15] == 'G'):
                    data_line[14] = float(data_line[14])*100000000
                else:
                    data_line[14] = float(data_line[14])*1000000

                data_line = data_line[0:5] + data_line[6:7] + data_line[9:11] + \
                    data_line[12:13] + data_line[14:15] + data_line[16:17]

            # Bytes and BPS in megabytes\n"
            elif ((data_line[11] == "M" or data_line[11] == 'G') and (data_line[14] == 'M' or data_line[14] == 'G')):
                if (data_line[11] == 'G'):
                    data_line[10] = float(data_line[10])*100000000
                else:
                    data_line[10] = float(data_line[10])*1000000
                if (data_line[14] == 'G'):
                    data_line[13] = float(data_line[13])*100000000
                else:
                    data_line[13] = float(data_line[13])*1000000

                data_line = data_line[0:5] + data_line[6:7] + \
                    data_line[9:11] + data_line[12:14] + data_line[15:16]

            # Bytes and BPS in megabytes\n"
            elif ((data_line[12] == "M" or data_line[12] == 'G') and (data_line[12] == 'M' or data_line[12] == 'G')):
                if (data_line[12] == 'G'):
                    data_line[11] = float(data_line[11])*100000000
                else:
                    data_line[11] = float(data_line[11])*1000000
                if (data_line[14] == 'G'):
                    data_line[13] = float(data_line[13])*100000000
                else:
                    data_line[13] = float(data_line[13])*1000000

                data_line = data_line[0:5] + data_line[6:7] + \
                    data_line[9:12] + data_line[13:14] + data_line[15:16]

            elif (data_line[13] == 'M' or data_line[13] == 'G'):  # BPS measured in megabytes
                if (data_line[13] == 'G'):
                    data_line[12] = float(data_line[12])*100000000
                else:
                    data_line[12] = float(data_line[12])*1000000

                data_line = data_line[0:5] + data_line[6:7] + \
                    data_line[9:13] + data_line[14:15]

            elif data_line[11] == 'M':  # Bytes measured in megabytes
                data_line = data_line[0:5] + data_line[6:7] + \
                    data_line[9:11] + data_line[12:15]
                # Change M bytes into byte measurement.
                data_line[7] = float(data_line[7])*1000000

            else:  # No megabyte metrics
                data_line = data_line[0:5] + data_line[6:7] + data_line[9:14]

            framedata.append(data_line)  # append each line to 'mother' array.
    # Convert Numpy array into Pandas dataframe.
    df = pd.DataFrame(np.array(framedata), columns=headings_line).copy()
    print('Data converted to Pandas dataframe.')
    return df


def format(df):
    '''
    Formats the dataframe column correctly. 
    '''
    print('Formatting dataframe columns...')
    df['Datetimetemp'] = df['Date'] + ' ' + \
        df['first-seen']  # Combine Date and first-seen
    df = df.astype({'Date': 'datetime64[ns]'})
    df = df.astype({'first-seen': 'datetime64[ns]'})

    df["Day"] = df['Date'].dt.dayofweek  # Created Day variable.
    df = df.astype({'Date': str})
    #df = df.astype({'first-seen': np.datetime64})
    df = df.astype({'Duration': np.float64})
    df = df.astype({"SrcIPAddr:Port": str})
    df = df.astype({"DstIPAddr:Port": str})
    df = df.astype({"Packets": np.float64})
    df = df.astype({"Bytes": np.float64})
    df = df.astype({"pps": np.float64})
    df = df.astype({"bps": np.float64})
    df = df.astype({"Bpp": np.float64})

    print('Defining new variables...')
    # Create binary Weekend variable.
    df['Weekend'] = 0
    df.loc[df['Day'] == 5, 'Weekend'] = 1
    df.loc[df['Day'] == 6, 'Weekend'] = 1

    # Insert combined Datetime at front of dataframe.
    df.insert(0, 'Datetime', df['Datetimetemp'])
    df['Datetime'] = df.Datetime.astype('datetime64[ns]')
    # Convert Datetime into an integer representation. This is a deprecated method.
    df['Datetime'] = df.Datetime.astype('int64')

    # Define university holiday calender
    holidays = pd.date_range(start='2020-1-1', end='2020-3-14', freq='1D')
    holidays = holidays.append(pd.date_range(
        start='2020-5-1', end='2020-5-9', freq='1D'))
    holidays = holidays.append(pd.date_range(
        start='2020-07-08', end='2020-08-02', freq='1D'))
    holidays = holidays.append(pd.date_range(
        start='2020-09-18', end='2020-09-27', freq='1D'))
    holidays = holidays.append(pd.date_range(
        start='2020-11-24', end='2020-12-31', freq='1D'))
    holidays = holidays.strftime("%Y-%m-%d").tolist()
    df['Holiday'] = 0

    for date in holidays:
        df.loc[df['Date'] == date, 'Holiday'] = 1
    # Delete unused columns.
    del df['Date']
    #del df['first-seen']
    return df


def viewDistributions(df):
    '''
    Visualises the distributions of the explanatory variables. 
    '''
    # Explore individual categories
    groups = [1, 5, 6, 7, 8, 9, 12, 13]
    values = df.values
    i = 1
    # plot each column
    plt.figure()
    for group in groups:
        plt.subplot(len(groups), 1, i)

        plt.plot(values[:, group])
        plt.title(df.columns[group], y=0.5, loc='right')
        i += 1
    plt.show()


def split(df):
    '''
    Splits the data into test and train, as well as the respective x and y sections of both subsets. 
    '''
    del df['first-seen']
    train, test = train_test_split(
        df, test_size=0.2, shuffle=True, random_state = 42)
    # Drop target variable from training data.
    x_train = train.drop(
        ['Datetimetemp', 'Bytes', 'SrcIPAddr:Port', 'DstIPAddr:Port', 'Proto'], axis=1).copy()
    # The double brackets are to keep Bytes in a pandas dataframe format, otherwise it will be pandas Series.
    y_train = train[['Bytes']].copy()
    x_test = test.drop(['Datetimetemp', 'Bytes', 'SrcIPAddr:Port',
                        'DstIPAddr:Port', 'Proto'], axis=1).copy()
    # The double brackets are to keep Bytes in a pandas dataframe format, otherwise it will be pandas Series.
    y_test = test[['Bytes']].copy()
    #print('X train shape', x_train.shape)
    # print(y_train.shape)
    view = input("View the split of training and test data? [Y/N]\n")
    if (view == 'Y'):
        m, b = np.polyfit(df['Datetime'], df['Bytes'], 1)
        plt.figure(figsize=(40, 10))
        plt.title("Split of Test and Train Set using Bytes as Target Variable")
        plt.scatter(train['Datetime'], train['Bytes'], label='Training set')
        plt.scatter(test['Datetime'], test['Bytes'], label='Test set')
        plt.ylabel("Bytes")
        plt.xlabel("int64 Datetime")
        plt.plot(df['Datetime'], m*df['Datetime']+b, color='red')
        plt.legend()
        plt.show()

    return x_train, y_train, x_test, y_test


def scale(data):
    '''
    Scales data to the range 0 - 1, but this can be passed in as a parameter if we want. 
    '''
    # Scale training dating
    # scikit MinMixScaler allows all variables to be normalised between 0 and 1.
    scaler = MinMaxScaler(feature_range=(0, 1))
    # Compute the minimum and maximum to be used for later scaling
    scaler.fit(data)
    # Scale features of X according to feature_range.
    scaled_data = scaler.transform(data)
    return scaled_data


def simpleLSTM(x_train, y_train, x_test, y_test, batch_size, epochs, neurons):
    '''
    Builds and trains the baseline LSTM model. We have to edit the dataframe to remove entries so that the lag/timesteps can be > 1. This 
    then affects how we will reshape the X_train into the correct 3D format for the model. @Ant currently working on ot. 
    '''
    # We need to figure out how to reshape effectively. This is linked to the comment below. If the middle parameter here is 1 then batch_size is 1.
    x_train, x_valid, y_train, y_valid = train_test_split(
        x_train, y_train, test_size=0.2, shuffle = True, random_state = 42)
    X_train = x_train.reshape((x_train.shape[0], 1, x_train.shape[1]))
    X_test = x_test.reshape((x_test.shape[0], 1, x_test.shape[1]))
    X_valid = x_valid.reshape((x_valid.shape[0], 1, x_valid.shape[1]))
    Y_valid = y_valid.reshape((y_valid.shape[0], 1, y_valid.shape[1]))

    n_features = X_train.shape[2]
    model = Sequential()
    # The 1 parameter here is the number of timesteps - essentially the lag. It is linked to the comment above.
    model.add(LSTM(neurons, activation='sigmoid',
                   input_shape=(batch_size, n_features)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    print("Training Baseline LSTM...")
    tic = time.perf_counter()  # Time at start of training
    model.fit(X_train, y_train, epochs=epochs, verbose=1,
              validation_data=(X_valid, Y_valid), shuffle = True)
    val_loss = model.history.history['val_loss']
    toc = time.perf_counter()  # Time at end of training
    loss_per_epoch = model.history.history['loss']
    train_yhat = model.predict(X_train, verbose=0)
    tic2 = time.perf_counter()
    test_yhat = model.predict(X_test, verbose=0)
    toc2 = time.perf_counter()

    val_yhat = model.predict(X_valid, verbose=0)

    simple_train_mae = mean_absolute_error(y_train, train_yhat)
    simple_test_mae = mean_absolute_error(y_test, test_yhat)
    simple_val_mae = mean_absolute_error(y_valid, val_yhat)
    simple_train_mse = mean_squared_error(y_train, train_yhat)
    simple_test_mse = mean_squared_error(y_test, test_yhat)
    simple_val_mse = mean_squared_error(y_valid, val_yhat)

    simple_lstm_train_time = toc - tic
    simple_lstm_prediction_time = toc2 - tic2

    print('Validation R2: ', r2_score(y_valid, val_yhat))
    print('Test R2: ', r2_score(y_test, test_yhat))
    simple_r2 = r2_score(y_test, test_yhat)

    return loss_per_epoch, val_loss, train_yhat, test_yhat, val_yhat, simple_lstm_train_time, simple_lstm_prediction_time, simple_train_mae, simple_test_mae, simple_val_mae, simple_train_mse, simple_test_mse, simple_val_mse, simple_r2


def bidirectionalLSTM(x_train, y_train, x_test, y_test, batch_size, epochs, neurons):
    '''
    Builds and trains a bidirectional LSTM. 
    '''

    x_train, x_valid, y_train, y_valid = train_test_split(
        x_train, y_train, test_size=0.2, random_state = 42, shuffle = True)
    X_train = x_train.reshape((x_train.shape[0], 1, x_train.shape[1]))
    X_test = x_test.reshape((x_test.shape[0], 1, x_test.shape[1]))
    X_valid = x_valid.reshape((x_valid.shape[0], 1, x_valid.shape[1]))
    Y_valid = y_valid.reshape((y_valid.shape[0], 1, y_valid.shape[1]))
    n_features = X_train.shape[2]
    model = Sequential()
    model.add(Bidirectional(LSTM(neurons, return_sequences=False,
                                 activation="sigmoid"), input_shape=(batch_size, n_features)))
    model.add(Dense(1))
    model.compile(loss='mse', optimizer='adam')

    print("Training Bidirectional LSTM...")
    tic = time.perf_counter()
    model.fit(X_train, y_train, epochs=epochs, verbose=1,
              validation_data=(X_valid, Y_valid), shuffle = True)
    val_loss = model.history.history['val_loss']

    toc = time.perf_counter()

    loss_per_epoch = model.history.history['loss']
    train_yhat = model.predict(X_train, verbose=0)
    tic2 = time.perf_counter()
    test_yhat = model.predict(X_test, verbose=0)
    toc2 = time.perf_counter()

    val_yhat = model.predict(X_valid, verbose=0)

    bidirectional_lstm_train_time = toc - tic
    bidirectional_lstm_prediction_time = toc2 - tic2

    bidirectional_train_mae = mean_absolute_error(y_train, train_yhat)
    bidirectional_test_mae = mean_absolute_error(y_test, test_yhat)
    bidirectional_val_mae = mean_absolute_error(y_valid, val_yhat)
    bidirectional_train_mse = mean_squared_error(y_train, train_yhat)
    bidirectional_test_mse = mean_squared_error(y_test, test_yhat)
    bidirectional_val_mse = mean_squared_error(y_valid, val_yhat)

    print('Validation R2: ', r2_score(y_valid, val_yhat))
    print('Test R2: ', r2_score(y_test, test_yhat))
    bidirectional_r2 = r2_score(y_test, test_yhat)

    return loss_per_epoch, val_loss, train_yhat, test_yhat, val_yhat, bidirectional_lstm_train_time, bidirectional_lstm_prediction_time, bidirectional_train_mae, bidirectional_test_mae, bidirectional_val_mae, bidirectional_train_mse, bidirectional_test_mse, bidirectional_val_mse, bidirectional_r2


def stackedLSTM(x_train, y_train, x_test, y_test, batch_size, epochs, neurons):
    '''
    Builds and trains a stacked LSTM. We could break this down into a method that creates the model and then a method that does
    the prediction. @Justin
    '''
    x_train, x_valid, y_train, y_valid = train_test_split(
        x_train, y_train, test_size=0.2, random_state = 42, shuffle = True)
    X_train = x_train.reshape((x_train.shape[0], 1, x_train.shape[1]))
    X_test = x_test.reshape((x_test.shape[0], 1, x_test.shape[1]))
    X_valid = x_valid.reshape((x_valid.shape[0], 1, x_valid.shape[1]))
    Y_valid = y_valid.reshape((y_valid.shape[0], 1, y_valid.shape[1]))

    n_features = X_train.shape[2]
    model = Sequential()
    model.add(LSTM(neurons, return_sequences=True, activation="sigmoid",
                   input_shape=(batch_size, n_features)))
    model.add(LSTM(neurons, return_sequences=True))
    model.add(LSTM(neurons))
    model.add(Dense(1))
    model.compile(loss='mse', optimizer='adam')

    print("Training Stacked LSTM...")
    tic = time.perf_counter()
    model.fit(X_train, y_train, epochs=epochs, verbose=1,
              validation_data=(X_valid, Y_valid), shuffle = True)
    val_loss = model.history.history['val_loss']

    toc = time.perf_counter()
    loss_per_epoch = model.history.history['loss']

    train_yhat = model.predict(X_train, verbose=0)

    tic2 = time.perf_counter()
    test_yhat = model.predict(X_test, verbose=0)
    toc2 = time.perf_counter()

    val_yhat = model.predict(X_valid, verbose=0)

    stacked_lstm_training_time = toc - tic
    stacked_lstm_prediction_time = toc2 - tic2

    stacked_train_mae = mean_absolute_error(y_train, train_yhat)
    stacked_test_mae = mean_absolute_error(y_test, test_yhat)
    stacked_val_mae = mean_absolute_error(y_valid, val_yhat)
    stacked_train_mse = mean_squared_error(y_train, train_yhat)
    stacked_test_mse = mean_squared_error(y_test, test_yhat)
    stacked_val_mse = mean_squared_error(y_valid, val_yhat)

    print('Validation R2: ', r2_score(y_valid, val_yhat))
    print('Test R2: ', r2_score(y_test, test_yhat))
    stacked_r2 = r2_score(y_test, test_yhat)

    return loss_per_epoch, val_loss, train_yhat, test_yhat, val_yhat, stacked_lstm_training_time, stacked_lstm_prediction_time, stacked_train_mae, stacked_test_mae, stacked_val_mae, stacked_train_mse, stacked_test_mse, stacked_val_mse, stacked_r2


def view_yhat(y_train, yhat_train, y_test, yhat_test, name):
    '''
    Constructs a scatter plot of obs vs pred for training and test data.
    '''
    plt.scatter(y_train/1000000, y_unscale(y_train, yhat_train) /
                1000000, alpha=0.5, marker='.', label='Training set')
    plt.scatter(y_test/1000000, y_unscale(y_train, yhat_test) /
                1000000, alpha=0.5, marker='.', label='Test set')
    plt.plot([0, 600], [0, 600])
    plt.xlabel('True Value')
    plt.ylabel('Predicted Value')
    plt.legend()
    plt.title(name)


def plotLoss(loss):
    '''
    Plots the loss graph of an LSTM based off model.history.history['loss']
    '''
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.plot(range(len(loss)), loss)
    plt.show()


def y_unscale(y, yhat):
    '''
    Unscales a predicted y observation.
    '''
    Yscaler = MinMaxScaler(feature_range=(
        0, 1))  # apply same normalisation to response.
    Yscaler.fit(y)
    y_pred = Yscaler.inverse_transform(yhat)
    return y_pred


def scatter3A(x, y, z):

    plt.scatter(x, y, c=z, s=100, cmap='gray')
    plt.xlabel('Datetime')
    plt.ylabel('Day of Week')
    plt.yticks(np.arange(0.0, 6.0, step=1))  # Set label locations.
    # Set text labels.
    plt.yticks(np.arange(7), ['Mon', 'Tue', 'Wed',
               'Thurs', 'Fri', 'Sat', 'Sun'])
    plt.title('Bytes as a function of Time and Day of Week')
    plt.show()


def scatter3B(x, y, z):

    plt.scatter(x, y, c=z, s=100, cmap='gray')
    plt.xlabel('Datetime')
    plt.ylabel('Holiday')
    plt.yticks(np.arange(0.0, 1.0, step=1))  # Set label locations.
    plt.yticks(np.arange(2), ['Not holiday', 'holiday'])  # Set text labels.
    plt.title('Bytes as a function of Time and Holiday')
    plt.show()


def heatmap(data):
    corr = data.corr()
    sns.heatmap(corr, annot=True, cmap='CMRmap')
    plt.show()


if __name__ == "__main__":

    #loadData('SANREN_large.txt', 'SANREN2.txt')
    SANREN = readData('SANREN_large.txt')
    df = preprocess(SANREN, 20000)
    df = format(df)

    #Preprocessing
    #scatter3A(df['first-seen'], df['Day'], df['Bytes'])
    #scatter3B(df['first-seen'], df['Holiday'], df['Bytes'])

    #heatmap_df = df.drop(['Datetimetemp', 'SrcIPAddr:Port', 'DstIPAddr:Port', 'Proto', 'Day', 'Weekend', 'Holiday'], axis=1).copy()
    #heatmap(heatmap_df)

    #sns.kdeplot(df['Bytes'])
    #plt.title("Density of Byte Values")
    #plt.show()

    q0 = min(df['Bytes'])
    q1 = np.percentile(df['Bytes'], 25)
    q2 = np.percentile(df['Bytes'], 50)
    q3 = np.percentile(df['Bytes'], 75)
    q4 = max(df['Bytes'])

    print('Min: %.2f' % q0)
    print('Q1: %.2f' % q1)
    print('Median: %.2f' % q2)
    print('Q3: %.2f' % q3)
    print('Max: %.2f' % q4)

    # view = input("View the distribution of the explanatory features? [Y/N]\n")
    # if (view == 'Y'):
    #     viewDistributions(df)

    x_train, y_train, x_test, y_test = split(df)

    x_train_scaled = scale(x_train)
    y_train_scaled = scale(y_train)
    x_test_scaled = scale(x_test)
    y_test_scaled = scale(y_test)

    epochs = int(
        input("How many epochs would you like to train the models on? [n >= 1]\n"))
    while (epochs < 0):
        try:
            epochs = int(
                input("How many epochs would you like to train the models on? [n >= 1]\n"))
        except:
            print("Please enter a number.\n")

    neurons = int(
        input("How many neurons would you like each LSTM layer to have? [n >= 1]\n"))
    while (neurons < 0):
        try:
            neurons = int(
                input("How many neurons would you like each LSTM layer to have? [n >= 1]\n"))
        except:
            print("Please enter a number.\n")

    loss_simple, val_simple, yhat_train_simple, yhat_test_simple, yhat_val_simple, simple_lstm_train_time, simple_lstm_prediction_time,  simple_train_mae, simple_test_mae, simple_val_mae, simple_train_mse, simple_test_mse, simple_val_mse, simple_r2 = simpleLSTM(
        x_train_scaled, y_train_scaled, x_test_scaled, y_test_scaled, 1, epochs, neurons)  # timesteps (lag), epochs, neurons

    loss_bidirectional, val_bi, yhat_train_bi, yhat_test_bi, yhat_val_bi, bidirectional_lstm_train_time, bidirectional_lstm_prediction_time, bidirectional_train_mae, bidirectional_test_mae, bidirectional_val_mae, bidirectional_train_mse, bidirectional_test_mse, bidirectional_val_mse, bidirectional_r2 = bidirectionalLSTM(
        x_train_scaled, y_train_scaled, x_test_scaled, y_test_scaled, 1, epochs, neurons)

    loss_stacked, val_stacked, yhat_train_stacked, yhat_test_stacked, yhat_val_stacked, stacked_lstm_training_time, stacked_lstm_prediction_time, stacked_train_mae, stacked_test_mae, stacked_val_mae, stacked_train_mse, stacked_test_mse, stacked_val_mse, stacked_r2 = stackedLSTM(
        x_train_scaled, y_train_scaled, x_test_scaled, y_test_scaled, 1, epochs, neurons)

    data = [len(df), epochs, neurons, simple_lstm_train_time, simple_lstm_prediction_time, bidirectional_lstm_train_time, bidirectional_lstm_prediction_time,
            stacked_lstm_training_time, stacked_lstm_prediction_time, simple_train_mae, simple_test_mae, simple_val_mae, bidirectional_train_mae, bidirectional_test_mae, bidirectional_val_mae, stacked_train_mae, stacked_test_mae, stacked_val_mae, simple_train_mse, simple_test_mse, simple_val_mse, bidirectional_train_mse, bidirectional_test_mse, bidirectional_val_mse, stacked_train_mse, stacked_test_mse, stacked_val_mse, simple_r2, bidirectional_r2, stacked_r2]
    with open('data.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

    #print(simple_r2)
    #print(bidirectional_r2)
    #print(stacked_r2)

    # view = input("View the predicted yhat values for the test and training sets? [Y/N]\n")
    # if (view == 'Y'):
    #     plt.subplot(1, 3, 1)
    #     view_yhat(y_train, yhat_train_simple,y_test, yhat_test_simple, "Simple")
    #     plt.subplot(1, 3, 2)
    #     view_yhat(y_train, yhat_train_bi, y_test, yhat_test_bi, "Bidirectional")
    #     plt.subplot(1, 3, 3)
    #     view_yhat(y_train, yhat_train_stacked,y_test, yhat_test_stacked, "Stacked")
    #     plt.show()

    # view = input("View the loss graph of the LSTM\'s training process? [Y/N]\n")
    # if view == 'Y':
    #     lstm = input("View Simple, Stacked or Bidirectional?\n")  # Enter
    #     if lstm == 'Simple': plotLoss(loss_simple)
    #     elif lstm == 'Stacked': plotLoss(loss_stacked)
    #     elif lstm == 'Bidirectional': plotLoss(loss_bidirectional)

    # Computational cost metrics to determine difference in changing paramaters
