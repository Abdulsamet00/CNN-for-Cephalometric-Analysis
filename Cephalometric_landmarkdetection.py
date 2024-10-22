# -*- coding: utf-8 -*-
"""Untitled5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mL0V21g3oYMmTFoy7-KNMczQ31qYsc_i
"""

from google.colab import drive 
drive.mount('/content/gdrive',force_remount=True)

!ls "/content/gdrive/My Drive/ceph/"

import keras
from keras.models import Sequential
from keras.layers import Input,Dense, Dropout, Flatten,Activation,GlobalMaxPooling2D
from keras.layers import Conv2D, MaxPooling2D,ZeroPadding2D,BatchNormalization,Convolution2D
from keras.utils import to_categorical
from keras.preprocessing import image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from keras.preprocessing.image import ImageDataGenerator
from keras_preprocessing.image import ImageDataGenerator,load_img,img_to_array
#courseradan
from keras.optimizers import SGD,Adam
import numpy as np
from keras import layers
from keras.layers import Input, Dense, Activation, ZeroPadding2D, BatchNormalization, Flatten, Conv2D
from keras.layers import AveragePooling2D, MaxPooling2D, Dropout, GlobalMaxPooling2D, GlobalAveragePooling2D
from keras.models import Model
from keras.preprocessing import image
from keras.utils import layer_utils
from keras.utils.data_utils import get_file
from keras.applications.imagenet_utils import preprocess_input
from IPython.display import SVG
from keras.utils.vis_utils import model_to_dot
from keras.utils import plot_model
from keras.layers.convolutional import Conv2D,MaxPooling2D
import keras.backend as K
K.set_image_data_format('channels_last')
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow

!pip install -U -q PyDrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
# Authenticate and create the PyDrive client.
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)


link='' # csv file link which includes x,y coordinates of cephalometric landmarks
fluff, id = link.split('=')

downloaded = drive.CreateFile({'id':id}) 
downloaded.GetContentFile('Filename.csv')  
df3 = pd.read_csv('Filename.csv')

LMs=pd.read_csv('Filename.csv')

LMpos=LMs.columns.tolist()
print(LMs.shape[0])

y=np.array(LMs.drop(['Id'],axis=1)) #bu bizim labeller
y.shape 
print(y.shape)

train_image = []
for i in tqdm(range(LMs.shape[0])):
    img = image.load_img('/content/gdrive/My Drive/ceph/datasetkoordinat/' + LMs['Id'][i]+'.bmp',target_size=(497,497),color_mode="grayscale")
    img = image.img_to_array(img)
    
    train_image.append(img)
Pface = np.array(train_image)
print(Pface.shape)

img=Pface
img2=np.squeeze(img)
print(img2.shape)

plt.imshow(img2[10], cmap="gray", vmin=0, vmax=255)
print(img2[190])
#print(img2.shape)

#list =LMs.B_x.notna()
list =LMs.S_x.notna()

 
# creating series 
series = pd.Series(list) 
  
# calling .nonzero() method 
iselect = series.to_numpy().nonzero()[0]

Spic=Pface.shape[1]
m=iselect.shape[0]

X=np.zeros((m,Spic,Spic,1))
Y=np.zeros((m,2))

X[:,:,:,0]=img2[iselect,:,:]/255.0
Y[:,0]=LMs.B_x[iselect]/Spic
Y[:,1]=LMs.B_y[iselect]/Spic


import matplotlib.pyplot as plt

n = 0
nrows = 2
ncols = 2
irand=np.random.choice(Y.shape[0],nrows*ncols)
print(irand)
fig, ax = plt.subplots(nrows,ncols,sharex=True,sharey=True,figsize=[ncols*5,nrows*5])
for row in range(nrows):
    for col in range(ncols):
        ax[row,col].imshow(X[irand[n],:,:,0], cmap='gray')
        ax[row,col].scatter(Y[irand[n],0::2]*Spic,Y[irand[n],1::2]*Spic,marker='o',c='r',s=50)
        ax[row,col].set_xticks(())
        ax[row,col].set_yticks(())
        ax[row,col].set_title('image index = %d' %(irand[n]),fontsize=10)
        n += 1

# Split the dataset
from sklearn.model_selection import train_test_split

random_seed=21
Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=0.2, random_state=random_seed,shuffle=True)

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D
from keras.optimizers import SGD,RMSprop

model = Sequential()
model.add(Conv2D(32, (3, 3), padding = 'same', activation='tanh', input_shape=(Spic, Spic, 1)))
model.add(MaxPool2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(64, activation='tanh'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='tanh'))
model.add(Dropout(0.5))
model.add(Dense(2, activation='sigmoid'))

sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)

model.compile(loss='mean_squared_error', optimizer=Adam(learning_rate=0.01),metrics=['accuracy'])

model.fit(Xtrain, Ytrain, batch_size=30, epochs=10, validation_data = (Xtest, Ytest), verbose = 1)

Ytrain_pred = model.predict(Xtrain)
Ytest_pred = model.predict(Xtest)

n = 0
nrows = 3
ncols = 3
irand=np.random.choice(Ytest.shape[0],nrows*ncols)
fig, ax = plt.subplots(nrows,ncols,sharex=True,sharey=True,figsize=[ncols*10,nrows*10])
for row in range(nrows):
    for col in range(ncols):
        ax[row,col].imshow(Xtest[irand[n],:,:,0], cmap='gray')
        ax[row,col].scatter(Ytest[irand[n],0::2]*Spic,Ytest[irand[n],1::2]*Spic,marker='o',c='r',s=100,label='Doğru Nokta')
        ax[row,col].scatter(Ytest_pred[irand[n],0::2]*Spic,Ytest_pred[irand[n],1::2]*Spic,marker='o',c='b',s=100,label='Tahmin Edilen Nokta')
        ax[row,col].set_xticks(())
        ax[row,col].set_yticks(())
        ax[row,col].set_title('image index = %d' %(irand[n]),fontsize=10)
        ax[row,col].legend()
        n += 1
plt.suptitle('x: Manual; +: CNN', fontsize=16)







