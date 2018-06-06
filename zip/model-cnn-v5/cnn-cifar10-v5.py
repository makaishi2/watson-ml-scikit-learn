# Choose the underlying compiler - tensorflow or theano
import json
import os 

with open(os.path.expanduser('~') + "/.keras/keras.json","r") as f:
    compiler_data = json.load(f)
compiler_data["backend"] = "tensorflow"
compiler_data["image_data_format"] = "channels_last"  
with open(os.path.expanduser('~') + '/.keras/keras.json', 'w') as outfile:
    json.dump(compiler_data, outfile)

# Global variable intilization
defined_metrics = []
defined_loss = ""

# pickle データの読み込み
# 読み出し元プログラムの下記コーディングにより、当プログラム呼出し時に
# カレントディレクトリは「入力用バケット」になっている 
#
# os.chdir(DATA_DIR)
# model_script = run_path(model_script_path, { "model_result_path": model_result_path })

import pickle
from keras.utils import np_utils

with open('cifar-10-tf-train.pkl', 'rb') as f:
    train_data, train_label = pickle.load(f)
    train_data = train_data.astype('float32') / 255   
    class_labels_count = len(set(train_label.flatten()))
    train_label = np_utils.to_categorical(train_label, class_labels_count)

with open('cifar-10-tf-valid.pkl', 'rb') as f:
    val_data, val_label = pickle.load(f)
    val_data = val_data.astype('float32') / 255   
    val_label = np_utils.to_categorical(val_label, class_labels_count)

with open('cifar-10-tf-test.pkl', 'rb') as f:
    test_data, test_label = pickle.load(f)
    test_data = test_data.astype('float32') / 255   
    test_label = np_utils.to_categorical(test_label, class_labels_count)

# 学習繰り返し回数
nb_epoch = 50
# 1回の学習で何枚の画像を使うか
batch_size = 128

# TessorBloard初期化

import os
from os import environ
from keras.callbacks import TensorBoard
#writing metrics
if environ.get('JOB_STATE_DIR') is not None:
    tb_directory = os.path.join(os.environ["JOB_STATE_DIR"], "logs", "tb", "test")
else:
    tb_directory = os.path.join("logs", "tb", "test")
os.makedirs(tb_directory, exist_ok=True)
tensorboard = TensorBoard(log_dir=tb_directory)

# CNNモデル生成

# 必要ライブラリのロード
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, Activation

def cnn_model(X_train, class_labels_count):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding="same", input_shape=X_train.shape[1:]))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3))) 
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(class_labels_count))
    model.add(Activation('softmax'))

    model.compile(
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )
    return model

# モデル生成

model = cnn_model(train_data, class_labels_count)

# 学習
# コールバック関数にTensorboardを指定する

history = model.fit(
    train_data, train_label, batch_size=batch_size, epochs=nb_epoch, verbose=1,
    validation_data=(val_data, val_label), shuffle=True, callbacks=[tensorboard]
)

# テストデータで認識率計算

test_scores = model.evaluate(test_data, test_label, verbose=1)
print(test_scores)

# モデルの保存
# 
# 呼出し元プログラムによりmodel_result_pathが設定されている
# 設定されていない場合は"./keras_model.hdf5"に保存
# 

print('Saving the model...')
if 'model_result_path' not in locals() and 'model_result_path' not in globals():
    model_result_path = "./keras_model.hdf5"
model.save(model_result_path)
print("Model saved in file: %s" % model_result_path)
