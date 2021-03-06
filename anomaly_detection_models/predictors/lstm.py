import numpy as np
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import os
import aiohttp


def load_data(ts_series, seq_len, ratio=0.9):
    sequence_length = seq_len + 1
    total_len = len(ts_series)
    ts_seqs = []
    for i in range(total_len - sequence_length):
        ts_seqs.append(ts_series[i: i + sequence_length])
    ts_seqs = np.array(ts_seqs)
    N = int(round(ratio * ts_seqs.shape[0]))
    train_set = ts_seqs[:N, :]
    test_set = ts_seqs[N, :]
    # Let's shuffle training set...
    np.random.shuffle(train_set)

    x_train = train_set[:, :-1]
    y_train = train_set[:, -1]

    x_test = train_set[:, :-1]
    y_test = train_set[:, -1]

    # reshap input to be [samples, time step, features]
    x_train = np.reshape(x_train, (x_train.shape[0], 1, x_train.shape[1]))
    y_train = np.reshape(y_train, (y_train.shape[0], 1, y_train.shape[1]))

    return (x_train, y_train, x_test, y_test)


def build_model(layers, seq_len=1, dropout=0.2, activation="linear", loss="mse", optimizer="rmsprop"):
    model = Sequential()

    # First Layer LSTM
    model.add(
        LSTM(layers[0], input_shape=(1, seq_len), return_sequences=True)
    )
    model.add(Dropout(dropout))

    # Second Layer LSTM
    model.add(
        LSTM(layers[1], return_sequences=False)
    )
    model.add(Dropout(dropout))

    # Feeds to fully connected normal layer
    model.add(Dense(1, activation=activation))

    # Compile model
    model.compile(loss=loss, optimizer=optimizer)

    return model


def normalize(dataset):
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    return dataset


def fetch_remote(graphite_host, graphite_port, metric, frm):
    url = "http://{host}:{port}/render?target={metric}&frm={frm}&format=json".format(
            host=graphite_host,
            port=graphite_port,
            metric=metric,
            frm=frm,
        )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()


def predict_single(model, ts_data):
    return model.predict(ts_data)


# TODO...
def predict_multiple(model, data, window_size):
    curr_frame = data[0]
    predicted = []
    for i in range(len(data)):
        predicted.append(model.predict(curr_frame[newaxis,:,:])[0,0])
        curr_frame = curr_frame[1:]
        curr_frame = np.insert(curr_frame, [window_size-1], predicted[-1], axis=0)
    return predicted



def plot_results(true_data, predict_data):
    pass
