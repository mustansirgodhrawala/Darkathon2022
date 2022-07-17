import pickle
import time

import pandas as pd
import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices("GPU")
if gpus:
    # only use GPU memory that we need, not allocate all the GPU memory
    tf.config.experimental.set_memory_growth(gpus[0], enable=True)

import tqdm
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Embedding, LSTM, Dropout, Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.metrics import Recall, Precision

dataframe = pd.read_csv("dataset.csv")
dataframe = dataframe.drop_duplicates(keep="first")
print("Built df")
X = dataframe["Text"].values.astype("U")
y = dataframe["Label"].values.astype("U")


SEQUENCE_LENGTH = 100  # the length of all sequences (number of words per sample)
EMBEDDING_SIZE = 100  # Using 100-Dimensional GloVe embedding vectors
TEST_SIZE = 0.25  # ratio of testing set

BATCH_SIZE = 64
EPOCHS = 10  # number of epochs

label2int = {"notdrugs": 0, "drugs": 1}
int2label = {0: "notdrugs", 1: "drugs"}


# Text tokenization
# vectorizing text, turning each text into sequence of integers
tokenizer = Tokenizer()
tokenizer.fit_on_texts(X)
# lets dump it to a file, so we can use it in testing
pickle.dump(tokenizer, open("results/tokenizer.pickle", "wb"))
# convert to sequence of integers
X = tokenizer.texts_to_sequences(X)


# convert to numpy arrays
X = np.array(X)
y = np.array(y)
# pad sequences at the beginning of each sequence with 0's
# for example if SEQUENCE_LENGTH=4:
# [[5, 3, 2], [5, 1, 2, 3], [3, 4]]
# will be transformed to:
# [[0, 5, 3, 2], [5, 1, 2, 3], [0, 0, 3, 4]]
X = pad_sequences(X, maxlen=SEQUENCE_LENGTH)

y = [label2int[label] for label in y]
y = to_categorical(y)

# split and shuffle
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=7
)
# print our data shapes
print("X_train.shape:", X_train.shape)
print("X_test.shape:", X_test.shape)
print("y_train.shape:", y_train.shape)
print("y_test.shape:", y_test.shape)


def get_embedding_vectors(tokenizer, dim=100):
    embedding_index = {}
    with open(f"data/glove.6B.{dim}d.txt", encoding="utf8") as f:
        for line in tqdm.tqdm(f, "Reading GloVe"):
            values = line.split()
            word = values[0]
            vectors = np.asarray(values[1:], dtype="float32")
            embedding_index[word] = vectors

    word_index = tokenizer.word_index
    embedding_matrix = np.zeros((len(word_index) + 1, dim))
    for word, i in word_index.items():
        embedding_vector = embedding_index.get(word)
        if embedding_vector is not None:
            # words not found will be 0s
            embedding_matrix[i] = embedding_vector

    return embedding_matrix


def get_model(tokenizer, lstm_units):
    """
    Constructs the model,
    Embedding vectors => LSTM => 2 output Fully-Connected neurons with softmax activation
    """
    # get the GloVe embedding vectors
    embedding_matrix = get_embedding_vectors(tokenizer)
    model = Sequential()
    model.add(
        Embedding(
            len(tokenizer.word_index) + 1,
            EMBEDDING_SIZE,
            weights=[embedding_matrix],
            trainable=False,
            input_length=SEQUENCE_LENGTH,
        )
    )

    model.add(LSTM(lstm_units, recurrent_dropout=0.2))
    model.add(Dropout(0.3))
    model.add(Dense(2, activation="softmax"))
    # compile as rmsprop optimizer
    # aswell as with recall metric
    model.compile(
        optimizer="rmsprop",
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.Precision(), tf.keras.metrics.Recall()],
    )
    model.summary()
    return model


model = get_model(tokenizer=tokenizer, lstm_units=128)


# initialize our ModelCheckpoint and TensorBoard callbacks
# model checkpoint for saving best weights
model_checkpoint = ModelCheckpoint(
    "results/spam_classifier_{val_loss:.2f}.h5", save_best_only=True, verbose=1
)
# for better visualization
tensorboard = TensorBoard(f"logs/spam_classifier_{time.time()}")
# train the model
model.fit(
    X_train,
    y_train,
    validation_data=(X_test, y_test),
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    callbacks=[tensorboard, model_checkpoint],
    verbose=1,
)


# get the loss and metrics
result = model.evaluate(X_test, y_test)
# extract those
loss = result[0]
accuracy = result[1]
precision = result[2]
recall = result[3]

print(f"[+] Accuracy: {accuracy*100:.2f}%")
print(f"[+] Precision:   {precision*100:.2f}%")
print(f"[+] Recall:   {recall*100:.2f}%")
