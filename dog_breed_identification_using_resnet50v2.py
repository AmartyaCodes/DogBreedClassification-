# -*- coding: utf-8 -*-
"""dog-breed-identification_using_ResNet50V2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hFFF2nVfQzfaH0s9gxXpI4o9xqkpmOsQ

# Importing Necessary Libraries
"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# import tensorflow as tf
# import pandas as pd
# import numpy as np 
# from keras_preprocessing.image import ImageDataGenerator
# from mpl_toolkits.axes_grid1 import ImageGrid
# import itertools 
# import matplotlib.pyplot as plt
# %matplotlib inline

# Commented out IPython magic to ensure Python compatibility.
# %%time
# #CREATING THE TRAINING AND TEST DIRECTORY 
# train_dir = '../input/dog-breed-identification/train'
# test_dir ='../input/dog-breed-identification/test'

#NOTICE THAT THE NAMES OF THE IMAGES LACK THE ".jpg" AND IN ORDER TO READ THE IMAGES WE NEED TO ADD IT, SINCE THE IMAGES ARE THERE IN jpg FORMAT
def append_ext(fn):
    return fn+".jpg"

# Commented out IPython magic to ensure Python compatibility.
# %%time
# # def append_ext(fn):
# #     return fn+".jpg"
# traindf = pd.read_csv('../input/dog-breed-identification/labels.csv',dtype=str)
# testdf = pd.read_csv('../input/dog-breed-identification/sample_submission.csv',dtype=str)
# 
#

traindf["id"] = traindf["id"].apply(append_ext)
testdf["id"] = testdf["id"].apply(append_ext)

included_breed = ['beagle', 'chihuahua', 'doberman',
'french_bulldog', 'golden_retriever', 'malamute', 'pug', 'saint_bernard', 'scottish_deerhound',
'tibetan_mastiff']
for index,breed in traindf.iterrows():
    if breed[1] not in included_breed:
        traindf= traindf.drop([index])
traindf.shape

"""# Training Labels"""

traindf.head()

"""# Test id or Sample Submission"""

testdf.head()

"""# Training Images"""

import os 
src_path = "../input/dog-breed-identification/train"
sub_class = os.listdir(src_path)

fig = plt.figure(figsize=(10,5))
for e in range(len(sub_class[:8])):
    plt.subplot(2,4,e+1)
    img = plt.imread(os.path.join(src_path,sub_class[e]))
    plt.imshow(img, cmap=plt.get_cmap('gray'))
    plt.axis('off')

"""# Data preprocessing"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# train_datagen=ImageDataGenerator( rescale=1./255.,
#                                   rotation_range = 20,
#                                   brightness_range=[0.2,1.0],
#                                   width_shift_range = 0.2,
#                                   height_shift_range = 0.2,
#                                   #shear_range = 0.2,
#                                   #zoom_range = [0.7,1],
#                                   horizontal_flip = True,
#                                   #Setting validation split to 2% 
#                                   validation_split=0.1
#                                   )

BATCH_SIZE = 32

image_size=(224,224)

train_generator=train_datagen.flow_from_dataframe(
dataframe=traindf,
directory=train_dir,
x_col="id",
y_col="breed",
subset="training",
batch_size=BATCH_SIZE,
seed=42,
shuffle=True,
class_mode="categorical",
target_size=image_size,
color_mode="rgb" 
)

"""# Plotting Augmented images"""

x,y = next(train_generator)

print(type(x))
print(x.shape)
print(y.shape)

def show_grid(image_list,nrows,ncols,figsize=(10,10),showaxis='off'):
    
    image_list = [image_list[i,:,:,:] for i in range(image_list.shape[0])]
    fig = plt.figure(None, figsize,frameon=False)
    grid = ImageGrid(fig, 111,  # similar to subplot(111)
                     nrows_ncols=(nrows, ncols),  # creates 2x2 grid of axes
                     axes_pad=0.3,  # pad between axes in inch.
                     share_all=True,
                     )
    for i in range(nrows*ncols):
        ax = grid[i]
        ax.imshow(image_list[i],cmap='Greys_r')  # The AxesGrid object work as a list of axes.
        ax.axis('off')

# Commented out IPython magic to ensure Python compatibility.
# %%time
# show_grid(x,8,3,figsize=(25,25))
#

"""# Validation Data"""

valid_generator=train_datagen.flow_from_dataframe(
dataframe=traindf,
directory=train_dir,
x_col="id",
y_col="breed",
subset="validation",
batch_size=BATCH_SIZE,
seed=42,
shuffle=True,
class_mode="categorical",
target_size=image_size,
color_mode="rgb")

"""# Test Data"""

test_datagen=ImageDataGenerator(rescale=1./255.)

test_generator=test_datagen.flow_from_dataframe(
dataframe=testdf,
directory=test_dir,
x_col="id",
y_col=None,
batch_size=BATCH_SIZE,
seed=42,
shuffle=False,
class_mode=None,
target_size=image_size,
color_mode="rgb")

"""# Pretrained model ResNet 50V2"""

shape=(224,224,3)

classes = len(included_breed)
classes

pretrained_model = tf.keras.applications.ResNet50V2(
        weights='imagenet',
        include_top=False ,
        input_shape=shape
    )
# pretrained_model.trainable = False
    
model = tf.keras.Sequential([ 
        pretrained_model,  
        tf.keras.layers.Flatten(),
#         tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(2048, activation='relu'),
        tf.keras.layers.Dropout(0.5),
#         tf.keras.layers.Dense(512, activation='relu'),
#         tf.keras.layers.Dropout(0.5),
#         tf.keras.layers.Dense(128, activation='relu'),
#         tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.2),
    
        tf.keras.layers.Dense(10, activation='softmax')
    ])

"""# CREATING OUR CUSTOM METRICS TO CALCULATE THE F1 SCORES"""

from keras import backend as K

def recall_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def precision_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def f1_m(y_true, y_pred): 
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))

# compile the model

# fit the model
# history = model.fit(Xtrain, ytrain, validation_split=0.3, epochs=10, verbose=0)

"""# CREATING THE MODEL"""

#opt = tf.keras.optimizers.Adam(learning_rate=0.001)
opt=tf.keras.optimizers.Adam(lr=1e-4)
model.compile(optimizer= opt , loss='categorical_crossentropy', metrics=['acc',f1_m,precision_m, recall_m])

# model.compile(optimizer = opt ,
#               loss="categorical_crossentropy",
#               metrics=["accuracy"])
model.summary()

"""# Early stopping"""

# reduce = tf.keras.callbacks.ReduceLROnPlateau( monitor='val_loss',factor=0.2,patience=5, min_lr=0.001 )

# early = tf.keras.callbacks.EarlyStopping( patience=2,
#                                           min_delta=0.001,
#                                           restore_best_weights=True)

"""
# Fitting the Model:"""

STEP_SIZE_TRAIN = train_generator.n//train_generator.batch_size
STEP_SIZE_VALID = valid_generator.n//valid_generator.batch_size
history = model.fit(train_generator,
                    steps_per_epoch=STEP_SIZE_TRAIN,
                    validation_data=valid_generator,
                    validation_steps=STEP_SIZE_VALID,
                    epochs=10,
#                     callbacks=[early],
                   )

"""# Loss and Accuracy Curves"""

def display_training_curves(training, validation, title, subplot):
    if subplot%10==1: # set up the subplots on the first call
        plt.subplots(figsize=(10,10), facecolor='#F0F0F0')
        plt.tight_layout()
    ax = plt.subplot(subplot)
    ax.set_facecolor('#F8F8F8')
    ax.plot(training)
    ax.plot(validation)
    ax.set_title('MODEL '+ title)
    ax.set_ylabel(title)
    ax.set_xlabel('epoch')
    ax.legend(['train', 'valid.'])

display_training_curves(
    history.history['loss'],
    history.history['val_loss'],
    'LOSS',
    211,
)

display_training_curves(
    history.history['acc'],
    history.history['val_acc'],
    'ACCURACY',
    212,
)

"""# Accuracy"""

loss, accuracy, f1_score, precision, recall = model.evaluate(valid_generator,batch_size=32)
# score = model.evaluate(valid_generator,batch_size=32)
# print("Accuracy: {:.2f}%".format(score[1] * 100)) 
# print("Loss: ",score[0])

print("Loss:", loss)
print("Accuracy:", accuracy)
print("F1 Score:", f1_score)

# model.save("DogClassification.h5")

"""# Predicting Test Images"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# pred=model.predict(test_generator)

df_submission = pd.read_csv('/kaggle/input/dog-breed-identification/sample_submission.csv', usecols= included_breed+['id'])
df_submission.head()

df_submission.iloc[:,1:] = pred
df_submission.head()

"""# Submission"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# df_submission.to_csv('Submission.csv')
