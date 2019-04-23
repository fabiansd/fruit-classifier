import random
from pathlib import Path
import cv2
import numpy as np
from keras.optimizers import Adam
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import to_categorical
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from fruit_classifier.models.models import get_lenet


def get_image_paths(path):
    """
    Returns a list of random shuffled image paths

    Parameters
    ----------
    path : Path
        Path to the training images

    Returns
    -------
    image_paths : list
        Random shuffled image paths
    """

    print('[INFO] loading images...')

    image_paths = sorted(path.glob('**/*'))
    image_paths = [p for p in image_paths if p.is_file()]
    random.seed(42)
    random.shuffle(image_paths)

    return image_paths


def get_data_and_labels(image_paths):
    """
    Returns the data and the labels from the input paths

    Parameters
    ----------
    image_paths : list
        List of Paths of the image paths

    Returns
    -------
    data : np.array, shape (len(image_paths), channels, width, height)
        The images as numpy array
    labels : np.array, shape (len(image_paths,)
        The corresponding labels
    """

    data = list()
    labels = list()
    # Loop over the input images
    for image_path in image_paths:
        # Load the image, pre-process it, and store it in the data list
        image = cv2.imread(str(image_path))
        image = cv2.resize(image, (28, 28))
        image = img_to_array(image)
        data.append(image)

        # Extract the class label from the image path and update the
        # labels list
        label = image_path.parts[-2]
        labels.append(label)
    # Scale the raw pixel intensities to the range [0, 1]
    data = np.array(data, dtype='float') / 255.0
    labels = np.array(labels)

    return data, labels


def get_model_input(data, labels):
    """
    Returns the input to the model

    Parameters
    ----------
    data : np.array, shape (n_images, channels, width, height)
        The images as numpy array
    labels : np.array, shape (n_images,)
        The corresponding labels

    Returns
    -------
    x_train : np.array, shape (n_train, channels, width, height)
        The training data
    x_val : np.array, shape (n_val, channels, width, height)
        The validation data
    y_train : np.array, shape (n_train,)
        The training labels
    y_val : np.array, shape (n_val,)
        The validation labels
    image_generator : ImageDataGenerator
        Generator used for batches
    """

    encoded_labels = LabelEncoder().fit_transform(labels)
    num_classes = len(set(labels))

    # Partition the data into training and testing splits using 75% of
    # the data for training and the remaining 25% for testing
    (x_train, x_val, y_train, y_val) = train_test_split(data,
                                                        encoded_labels,
                                                        test_size=0.25,
                                                        random_state=42)

    # Convert the labels from integers to vectors
    y_train = to_categorical(y_train, num_classes=num_classes)
    y_val = to_categorical(y_val, num_classes=num_classes)
    # Construct the image generator for data augmentation
    image_generator = ImageDataGenerator(rotation_range=30,
                                         width_shift_range=0.1,
                                         height_shift_range=0.1,
                                         shear_range=0.2,
                                         zoom_range=0.2,
                                         horizontal_flip=True,
                                         fill_mode='nearest')

    return x_train, x_val, y_train, y_val, image_generator


def get_model(n_classes,
              width=28,
              height=28,
              channels=3,
              initial_learning_rate=1e-3,
              epochs=25):
    """
    Returns a compiled model

    Parameters
    ----------
    n_classes : int
        Number of classes to use in the model
    width : int
        The pixel width of the images
    height : int
        The pixel height of the images
    channels : int
        The number of channels in the image
    initial_learning_rate : float
        The initial learning rate for the optimizer
    epochs : int
        The number of epochs

    Returns
    -------
    model : Sequential
        The compiled model
    """

    print('[INFO] compiling model...')

    model = get_lenet(width=width,
                      height=height,
                      depth=channels,
                      classes=n_classes)

    opt = Adam(lr=initial_learning_rate,
               decay=initial_learning_rate / epochs)

    model.compile(loss='categorical_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy'])

    return model


def train_model(model,
                image_generator,
                x_train,
                y_train,
                x_val,
                y_val,
                batch_size=32,
                epochs=25):

    print('[INFO] training network...')

    history = \
        model.fit_generator(image_generator.flow(x_train,
                                                 y_train,
                                                 batch_size=batch_size),
                            validation_data=(x_val, y_val),
                            steps_per_epoch=len(x_train) // batch_size,
                            epochs=epochs,
                            verbose=1)
    # Save the model to disk
    print('[INFO] serializing network...')

    model_dir = \
        Path(__file__).absolute().parent.joinpath('generated_data',
                                                  'models')
    model_path = model_dir.joinpath('model.h5')

    if not model_dir.is_dir():
        model_dir.mkdir(parents=True, exist_ok=True)

    model.save(str(model_path))

    return history


def plot_training(history):
    """
    Plots the training loss and accuracy

    The plot is saved in the 'plot' directory

    Parameters
    ----------
    history : History
        History object containing
        - loss
        - val_loss
        - acc
        - val_acc
    """

    plt.style.use('ggplot')
    plt.figure()
    n_epochs = np.arange(0, len(history.history['loss']))
    plt.plot(n_epochs, history.history['loss'], label='Training '
                                                      'loss')
    plt.plot(n_epochs, history.history['val_loss'], label='Validation '
                                                          'loss')
    plt.plot(n_epochs, history.history['acc'],
             label='Training accuracy')
    plt.plot(n_epochs, history.history['val_acc'], label='Validation '
                                                         'accuracy')
    plt.title('Training Loss and Accuracy for fruit classifier')
    plt.xlabel('Epoch #')
    plt.ylabel('Loss/Accuracy')
    plt.legend(loc='lower left')

    plot_dir = \
        Path(__file__).absolute().parent.joinpath('generated_data',
                                                  'plots')

    if not plot_dir.is_dir():
        plot_dir.mkdir(parents=True, exist_ok=True)

    plot_path = plot_dir.joinpath('training_history.png')

    plt.savefig(str(plot_path))
