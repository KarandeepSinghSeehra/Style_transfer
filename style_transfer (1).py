# -*- coding: utf-8 -*-
"""Style_Transfer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ecrGMo7wGO0gT1mqMnZInvbhqUOzsvXR

# Defining Style Transfer

### Steps to perform

#### Import libraries
"""

import tensorflow as tf
from keras.applications import VGG19
from keras.preprocessing.image import load_img, img_to_array
from keras.applications.vgg19 import preprocess_input
import numpy as np
from skimage.transform import resize
import matplotlib.pyplot as plt

"""#### Load images"""

content_image_path = '/content/Albert-Einstein-Birthday-1200x834.jpg'
style_image_path = '/content/painting5.jpeg'

# Load content and style images
content_image = load_img(content_image_path, target_size=(224, 224))
style_image = load_img(style_image_path, target_size=(224, 224))

# Convert images to arrays
content_array = img_to_array(content_image)
style_array = img_to_array(style_image)

# Preprocess input for VGG19 model
content_array = preprocess_input(np.expand_dims(content_array, axis=0))
style_array = preprocess_input(np.expand_dims(style_array, axis=0))

"""#### Load VGG19 Model and Define Layers"""

# Load VGG19 model
vgg19 = VGG19(weights='imagenet',input_shape = (224,224,3), include_top=False)

# Define content and style layers for feature extraction
content_layers = ['block5_conv2']
style_layers = [
    'block1_conv1',
    'block2_conv1',
    'block3_conv1',
    'block4_conv1',
]

vgg19.summary()

from keras.models import Model

def get_model(model, content_layers, style_layers):
    outputs = [model.get_layer(layer).output for layer in (content_layers + style_layers)]
    return Model(inputs=model.input, outputs=outputs)

content_model = get_model(vgg19, content_layers, style_layers)

# Extract content and style features
content_outputs = content_model.predict(content_array)

content_target = content_outputs[0]  # Assuming the content target is in the first layer specified
style_targets = content_outputs[1:]  # Style targets are in the subsequent layers

content_target.shape

for style_target in style_targets:
  print(style_target.shape)

style_targets[1][0,:,:,0].shape

feature_maps = np.squeeze(content_target, axis=0)

# Assuming you want to visualize all the feature maps (512 in this case)
num_feature_maps = feature_maps.shape[-1]

# Setting up the subplot grid
rows = int(np.ceil(np.sqrt(num_feature_maps)))
cols = int(np.ceil(num_feature_maps / rows))

# Plotting each feature map
plt.figure(figsize=(100,100))
for i in range(50):
    plt.subplot(rows, cols, i + 1)
    plt.imshow(feature_maps[:, :, i], cmap='viridis')  # Displaying each feature map as an image
    plt.axis('off')

plt.tight_layout()
plt.show()

image_features = content_model(content_array)
image_features[3].shape

style_target.shape[3]

"""#### Define loss functions"""

def content_loss(content, target):
    content = tf.cast(content, tf.float64)  # Cast to float32 if needed
    target = tf.cast(target, tf.float64)
    return tf.reduce_mean(tf.square(content - target))

def gram_matrix(style_targets):
    cor_all = []
    for i, style_feature in enumerate(style_targets):

        style_feature = tf.Variable(style_feature, dtype=tf.float32)
        style_feature = style_feature.numpy()

        mat = np.zeros((style_feature.shape[3], len(style_feature[0,:,:,i].flatten())))
        row = 0
        channels = style_feature.shape[-1]
        size = style_feature.shape[1] * style_feature.shape[2]
        for j in range(style_feature.shape[3]):
            flattened_feature = style_feature[0, :, :, j].flatten()
            mat[row, :] = flattened_feature # Assign the flattened feature to the row
            row += 1  # Move to the next row
        cor = np.corrcoef(mat, rowvar = True)
        cor_mod = cor/(4. * (channels ** 2) * (size ** 2))
        # Ensure that the shape is as expected
        #print(f"Shape of mat:{mat.shape}\nshape of correlation matrix:  {cor.shape}")
        #corr_mat_resized = resize(cor, (64, 64), mode='constant')
        #cor_all.append(corr_mat_resized)
        #result = np.add.reduce(cor_all)
    return cor

def style_loss(style, target):
    S = gram_matrix(style)
    C = gram_matrix(target)
    print(S.dtype, C.dtype)
    return content_weight

def total_variation_loss(image):
    x_deltas = image[:, :-1, :, :] - image[:, 1:, :, :]
    y_deltas = image[:, :, :-1, :] - image[:, :, 1:, :]
    return tf.reduce_mean(tf.square(x_deltas)) + tf.reduce_mean(tf.square(y_deltas))

"""#### Optimization loop"""

# Assuming content_loss_val, style_loss_val, and tv_loss_val are TensorFlow tensors
content_weight = tf.constant(1e3, dtype=tf.float64)
style_weight = tf.constant(1e-2, dtype=tf.float64)
total_variation_weight = tf.constant(30, dtype=tf.float64)

#defining the generated image
generated_image = tf.Variable(content_array)

#defining the optimizer that will be used
optimizer = tf.optimizers.Adam(learning_rate=2.0, beta_1=0.99, epsilon=1e-1)

def train_step(image):
    #using GradientTape() for calculating gradient
    with tf.GradientTape() as tape:
        tape.watch(image)
        image_features = content_model(image) #all features content as well as style features
        content_features = image_features[0] #seperating content features
        style_features = image_features[1:] #seperating style features

        content_loss_val = content_loss(content_features, content_target)
        #style_loss_val = tf.add_n([style_loss(style_feat, style_target) for style_feat, style_target in zip(style_features, style_targets)])
        #[print(style_feat.shape, style_target.shape) for style_feat, style_target in zip(style_features, style_targets)]
        style_loss_val = style_loss(style_features, style_targets)
        style_loss_val = tf.constant(style_loss_val, dtype=tf.float64)
        total_loss = content_weight * content_loss_val + style_weight * style_loss_val #+ total_variation_weight * tv_loss_val

    grad = tape.gradient(total_loss, image)
    optimizer.apply_gradients([(grad, image)])
    image.assign(tf.clip_by_value(image, clip_value_min=0.0, clip_value_max=255.0))

    return total_loss


num_iterations = 50
total_loss = []
for i in (range(num_iterations)):
    loss = train_step(generated_image)
    total_loss.append(loss)
    print(f"Iteration: {i}, Total loss: {loss}")

plt.plot(total_loss)

"""#### Generated Styled images"""

styled_image = generated_image.numpy().squeeze()
styled_image = np.clip(styled_image, 0, 255).astype('uint8')

"""Display or Save the Result"""

import matplotlib.pyplot as plt

plt.figure(figsize = (15,15))
plt.subplot(131)
plt.title('Combined_image')
plt.imshow(styled_image)
plt.subplot(132)
plt.title('Content_image')
plt.imshow(content_image)
plt.subplot(133)
plt.title('style_image')
plt.imshow(style_image)
plt.axis('off')
plt.show()

# Save the styled image
plt.imsave('styled_image.jpg', styled_image)

del styled_image



"""## Loading the Dataset"""

import os
import cv2
from PIL import Image
import numpy as np
from keras.utils import normalize
import matplotlib.pyplot as plt

"""### Preprocessing"""

input_dataset=[]
for i,image_path in enumerate(input_img_paths):
  if i == 4000:
    break
  image=Image.open(image_path)
  # image=Image.fromarray(image)
  image=image.resize((256,256))
  input_dataset.append(np.array(image))

print(len(input_dataset))
print(input_dataset[0].shape)

plt.imshow(input_dataset[0])

target_dataset=[]
for i,image_path in enumerate(target_img_paths):
  if i == 4000:
    break
  image=Image.open(image_path)
  image=image.resize((256,256))
  target_dataset.append(np.array(image))

print(len(target_dataset))
print(target_dataset[0].shape)

plt.imshow(target_dataset[0])

source_data = np.array(input_dataset)
target_data = np.array(target_dataset)

print(source_data.shape)
print(target_data.shape)

source_data = source_data / 255
target_data = target_data / 255

source_data

del input_dataset
del target_dataset

from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test=train_test_split(source_data,target_data,test_size=0.2,random_state=2)

import tensorflow as tf

"""### U-Net model"""

ht=256
wt=256
ch=3

inputs=tf.keras.layers.Input((ht,wt,ch))

c1=tf.keras.layers.Conv2D(16,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(inputs)
c1=tf.keras.layers.Dropout(0.1)(c1)
c1=tf.keras.layers.Conv2D(16,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(c1)
p1=tf.keras.layers.MaxPooling2D((2,2))(c1)


c2=tf.keras.layers.Conv2D(32,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(p1)
c2=tf.keras.layers.Dropout(0.1)(c2)
c2=tf.keras.layers.Conv2D(32,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(c2)
p2=tf.keras.layers.MaxPooling2D((2,2))(c2)

c3=tf.keras.layers.Conv2D(64,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(p2)
c3=tf.keras.layers.Dropout(0.1)(c3)
c3=tf.keras.layers.Conv2D(64,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(c3)
p3=tf.keras.layers.MaxPooling2D((2,2))(c3)

c4=tf.keras.layers.Conv2D(128,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(p3)
c4=tf.keras.layers.Dropout(0.1)(c4)
c4=tf.keras.layers.Conv2D(128,(3,3),activation='relu',kernel_initializer='he_normal',padding='same', name='c4_2')(c4)
p4=tf.keras.layers.MaxPooling2D((2,2))(c4)

c5=tf.keras.layers.Conv2D(256,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(p4)
c5=tf.keras.layers.Dropout(0.1)(c5)
c5=tf.keras.layers.Conv2D(256,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(c5)

#upsampling
v6=tf.keras.layers.Conv2DTranspose(128,(2,2),strides=(2,2),padding='same')(c5)
v6=tf.keras.layers.concatenate([v6,c4])
c6=tf.keras.layers.Conv2D(128,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(v6)
c6=tf.keras.layers.Dropout(0.2)(c6)
c6=tf.keras.layers.Conv2D(128,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(c6)

v7=tf.keras.layers.Conv2DTranspose(64,(2,2),strides=(2,2),padding='same')(c6)
v7=tf.keras.layers.concatenate([v7,c3])
c7=tf.keras.layers.Conv2D(64,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(v7)
c7=tf.keras.layers.Dropout(0.2)(c7)
c7=tf.keras.layers.Conv2D(64,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(c7)

v8=tf.keras.layers.Conv2DTranspose(32,(2,2),strides=(2,2),padding='same')(c7)
v8=tf.keras.layers.concatenate([v8,c2])
c8=tf.keras.layers.Conv2D(32,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(v8)
c8=tf.keras.layers.Dropout(0.2)(c8)
c8=tf.keras.layers.Conv2D(32,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(c8)

v9=tf.keras.layers.Conv2DTranspose(16,(2,2),strides=(2,2),padding='same')(c8)
v9=tf.keras.layers.concatenate([v9,c1],axis=3)
c9=tf.keras.layers.Conv2D(16,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(v9)
c9=tf.keras.layers.Dropout(0.2)(c9)
c9=tf.keras.layers.Conv2D(16,(3,3),activation='relu',kernel_initializer='he_normal',padding='same')(c9)

outputs=tf.keras.layers.Conv2DTranspose(channels,(2,2),padding='same')(c9)

model=tf.keras.Model(inputs=[inputs],outputs=[outputs])

model.summary()

from tensorflow import keras
keras.utils.plot_model(model)

# The gram matrix of an image tensor (feature-wise outer product)


def gram_matrix(x):
    x = tf.transpose(x, (0, 3, 1, 2))
    features = tf.reshape(x, (tf.shape(x)[0], tf.shape(x)[1], -1))
    gram = tf.matmul(features, tf.transpose(features))
    return gram


# The "style loss" is designed to maintain
# the style of the reference image in the generated image.
# It is based on the gram matrices (which capture style) of
# feature maps from the style reference image
# and from the generated image


def style_loss(style, combination):
    S = gram_matrix(style)
    C = gram_matrix(combination)
    channels = 3
    size = 256 * 256
    return tf.reduce_sum(tf.square(S - C)) / (4.0 * (channels**2) * (size**2))


# An auxiliary loss function
# designed to maintain the "content" of the
# base image in the generated image


def content_loss(base, combination):
    return tf.reduce_sum(tf.square(combination - base))


# The 3rd loss function, total variation loss,
# designed to keep the generated image locally coherent


def total_variation_loss(x):
    a = tf.square(
        x[:, : img_nrows - 1, : img_ncols - 1, :] - x[:, 1:, : img_ncols - 1, :]
    )
    b = tf.square(
        x[:, : img_nrows - 1, : img_ncols - 1, :] - x[:, : img_nrows - 1, 1:, :]
    )
    return tf.reduce_sum(tf.pow(a + b, 1.25))

def compute_loss(combination_image, base_image, style_reference_image):
    input_tensor = tf.concat(
        [base_image, style_reference_image, combination_image], axis=0
    )
    features = feature_extractor(input_tensor)

    # Initialize the loss
    loss = tf.zeros(shape=())

    # Add content loss
    layer_features = features[content_layer_name]
    base_image_features = layer_features[0, :, :, :]
    combination_features = layer_features[2, :, :, :]
    loss = loss + content_weight * content_loss(
        base_image_features, combination_features
    )
    # Add style loss
    for layer_name in style_layer_names:
        layer_features = features[layer_name]
        style_reference_features = layer_features[1, :, :, :]
        combination_features = layer_features[2, :, :, :]
        sl = style_loss(style_reference_features, combination_features)
        loss += (style_weight / len(style_layer_names)) * sl

    # Add total variation loss
    loss += total_variation_weight * total_variation_loss(combination_image)
    return loss

model.compile(optimizer='adam',loss='mean_squared_error')

del source_data
del target_data

checkpointer=tf.keras.callbacks.ModelCheckpoint('model_for_nuclei.h5',verbose=1,save_best_only=True)
early=tf.keras.callbacks.EarlyStopping(patience=5,monitor='val_loss')
callback=[checkpointer,early]
results=model.fit(x_train,y_train,validation_split=0.2,batch_size=8,epochs=50,callbacks=callback)

loss=results.history['loss']
val_loss=results.history['val_loss']
epochs=range(1,len(loss)+1)
plt.figure()
plt.plot(epochs,loss,label='Loss')
plt.plot(epochs,val_loss,label='Val_ loss')
plt.title('loss and validation loss')
plt.legend()
plt.show()

acc=model.evaluate(x_test,y_test)
print(acc)

import random

import torch, gc
gc.collect()
torch.cuda.empty_cache()

"""### Output display"""

test_img_number=random.randint(0,len(x_test))
test_img=x_test[test_img_number]
ground_truth=y_test[test_img_number]
# test_img_norm=test_img[:,:,0][:,:,None]
test_img_input=np.expand_dims(test_img,0)
prediction=(model.predict(test_img_input)[0] * 255).astype(np.uint8)

plt.figure(figsize=(15,15))
plt.subplot(131)
plt.title('Source Image')
plt.imshow((test_img * 255).astype(np.uint8))
plt.subplot(132)
plt.title('Target Image')
plt.imshow((ground_truth * 255).astype(np.uint8))
plt.subplot(133)
plt.title('Generated Image')
plt.imshow(prediction)
plt.show()
test_img_number=random.randint(0,len(x_test))
test_img=x_test[test_img_number]
ground_truth=y_test[test_img_number]
# test_img_norm=test_img[:,:,0][:,:,None]
test_img_input=np.expand_dims(test_img,0)
prediction=(model.predict(test_img_input)[0] * 255).astype(np.uint8)