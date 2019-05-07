import cv2
from keras.preprocessing.image import ImageDataGenerator
from tqdm import tqdm
from skimage.transform import resize
from pathlib import Path
from fruit_classifier.utils.file_utils import copytree
import win32api


def truncate_file_names(raw_dir, max_file_name_length):
    for filename in os.listdir(raw_dir):
        if len(filename) < max_file_name_length:
            continue
        cut = max_file_name_length-4
        dot_positions = filename.split(".")

        # Get last element in list of dots found in file name
        if len(dot_positions) == 0:
            ext_start_pos = max_file_name_length-4
        else:
            ext_start_pos = dot_positions[-1]

        extension = filename[ext_start_pos: -1]
        print(extension)
        #new_filename = filename[0:cut] + extension


def remove_non_images(raw_dir, clean_dir):
    """
    Removes images which are not readable

    Parameters
    ----------
    raw_dir : Path
        Path to the raw dataset
    clean_dir : Path
        Path for the cleaned dataset
    """

    copytree(raw_dir, clean_dir)

    # Find all image_paths
    image_paths = sorted(clean_dir.glob('**/*'))
    image_paths = [image_path for image_path in image_paths if
                   image_path.is_file()]

    for image_path in tqdm(image_paths, desc='Checking images'):
        image = cv2.imread(str(image_path))

        if image is None:
            print('Un-linking {}'.format(image_path))
            image_path.unlink()

    raw_dirs = sorted(raw_dir.glob('*'))
    raw_dirs = [d for d in raw_dirs if d.is_dir()]

    clean_dirs = sorted(clean_dir.glob('*'))
    clean_dirs = [d for d in clean_dirs if d.is_dir()]

    print('\nResult of cleaning:')
    for r, c in zip(raw_dirs, clean_dirs):
        n_raw = len(list(r.glob('*')))
        n_clean = len(list(c.glob('*')))
        print('    {}/{} remaining in {}'.format(n_clean, n_raw, c))


def preprocess_image(image):
    """
    Pre-processes a single image

    Parameters
    ----------
    image : np.array, shape (height, width, channels)
        The image to resize

    Returns
    -------
    preprocessed_image : np.array, shape (new_h, new_w, new_c)
        The preprocessed image
    """

    preprocessed_image = resize(image,
                                output_shape=(28, 28),
                                mode='reflect',
                                anti_aliasing=True)
    preprocessed_image = preprocessed_image / 255.0

    return preprocessed_image


def get_image_generator():
    """
    Returns the image generator

    Returns
    -------
    image_generator : ImageDataGenerator
        Generator used for batches
    """

    image_generator = ImageDataGenerator(rotation_range=30,
                                         width_shift_range=0.1,
                                         height_shift_range=0.1,
                                         shear_range=0.2,
                                         zoom_range=0.2,
                                         horizontal_flip=True,
                                         fill_mode='nearest')

    return image_generator
