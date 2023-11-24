# Style_transfer

# Neural Style Transfer Model for Artist's Style


## Method 1:

In first method VGG19 trained model is used to compute content loss, styled loss, and gram matrix from the input content image, styled image is selected, further the combined loss is optimised for 50 itertions to produce a combined image.

## Method 2:

## Introduction

Neural Style Transfer (NST) is an innovative technique that combines the content of one image with the artistic style of another, resulting in visually striking and unique artworks. This project focuses on building a model capable of learning an artist's style using a dataset of artistic images.

## Dataset

The dataset utilized for training the model is obtained from Kaggle: [Art by AI - Neural Style Transfer](https://www.kaggle.com/datasets/vbookshelf/art-by-ai-neural-style-transfer/data). To access the dataset, a Kaggle API token is necessary. The dataset comprises source images and their corresponding target images, providing pairs for the model to learn the desired artistic styles.

## Model Architecture

The neural network architecture employed in this project is based on the U-Net model. U-Net architectures are commonly used for image-to-image translation tasks due to their ability to capture both high and low-level features. The model takes a source image as input and generates an image with the desired artistic style.

### Layers and Structure
- **Convolutional Layers:** Responsible for extracting features from the input images.
- **Skip Connections:** Connect encoder and decoder layers to preserve spatial information and enhance feature reconstruction.
- **Transpose Convolutional Layers:** Used for upsampling and generating high-resolution images.

## Loss Functions

During the training process, three crucial loss functions are employed to guide the model in learning the desired style:

1. **Content Loss:** Measures the difference between the features extracted from the base image and the generated image. It ensures that the generated image retains the content of the source image.

2. **Style Loss:** This loss captures color and texture information from a style reference image at various spatial scales. It is computed using Gram matrices of feature maps from different layers of a convolutional neural network.

3. **Total Variation Loss:** Ensures local spatial continuity in the generated image, enhancing visual coherence.

## Training

The model is trained using the Adam optimizer and Mean Squared Error as the loss function. The training dataset is split into training and validation sets to monitor the model's performance. Checkpointing and early stopping callbacks are employed to save the best model and prevent overfitting.

## Evaluation

The model's performance is evaluated on a separate test set. The loss curves are visualized to understand the training progress and assess the model's generalization capabilities.

## Results

The trained model demonstrates its ability to transfer the style of a given artist to a source image. Qualitative assessments are provided through visualizations of ground truth, predicted, and source images.

## Usage

To utilize the trained model for style transfer, load the saved model (`model_for_nuclei.h5`). Input a source image, and the model will generate an image with the learned artistic style. This can be a fascinating tool for artists and creators to experiment with different datasets and artist styles.

## Dependencies

- TensorFlow: Used for model training and inference.
- Keras: Employed for building and compiling the neural network.
- Matplotlib: Utilized for visualization purposes.

## Acknowledgments

This project is grounded in the principles outlined in the paper [A Neural Algorithm of Artistic Style](http://arxiv.org/abs/1508.06576), providing a solid foundation for the application of neural style transfer techniques.
