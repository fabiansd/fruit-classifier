import argparse
import cv2
import numpy as np
from pathlib import Path
from fruit_classifier.predict.predict_utils import draw_class_on_image
from fruit_classifier.predict.predict_utils import classify
from fruit_classifier.predict.predict_utils import load_classifier
from fruit_classifier.utils.image_utils import open_image
from fruit_classifier.preprocessing.preprocessing_utils import \
    preprocess_image
import random
from pathlib import Path


def main(image_path=''):
    """
    Predict the class of an image

    Parameters
    ----------
    image_path : str
        The image path as a string
    """

    if image_path == '':
        generated_data_dir = \
            Path(__file__).absolute().parents[2].joinpath(
                'generated_data')
        cleaned_dir = generated_data_dir.joinpath('cleaned_data')
        p = Path(cleaned_dir)
        random_folder = random.choice(
            [x for x in p.iterdir() if x.is_dir()])
        sub_dir = cleaned_dir.joinpath(random_folder)

        f = Path(sub_dir)
        random_image = random.choice(
            [x for x in f.iterdir()])
        image_path = random_image



    # Load the image
    image = open_image(Path(image_path))
    orig = image.copy()

    # Pre-process the image for classification
    image = preprocess_image(image)
    # Expand the dimension (i.e. make the batch size = 1)
    image = np.expand_dims(image, axis=0)

    # Load the trained convolutional neural network
    model = load_classifier()

    # Classify the input image
    labels, probabilities = classify(model, image)
    label = labels[0]
    probability = np.max(probabilities[0])

    probability_text = '{}: {:.2f}%'.format(label, probability * 100)

    # Draw the label on the image
    output = draw_class_on_image(orig, probability_text)

    # Show the output image
    cv2.imshow('Output', output)
    cv2.waitKey(0)


if __name__ == '__main__':
    # Construct the argument parse and parse the arguments
    #parser = argparse.ArgumentParser(description='Predict the class '
    #                                             'of an image')
    #parser.add_argument('-i',
    #                    '--image',
    #                    required=True,
    #                    help='Path to input image')
    #args = parser.parse_args()

    #main(args.image)
    main()
