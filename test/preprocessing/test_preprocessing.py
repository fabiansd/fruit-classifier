import unittest
import cv2
from pathlib import Path
import numpy as np
import shutil
from fruit_classifier.preprocessing.preprocessing_utils \
    import truncate_filenames
from fruit_classifier.preprocessing.preprocessing_utils \
    import preprocess_image


class TestPreprocessingUtils(unittest.TestCase):

    def setUp(self):

        self.test_dir = Path(__file__).absolute().parents[1]
        self.jpg_image_file_name = self.test_dir.joinpath(
            "test_data", "original_test_image.jpg")

        # Correct dimensions
        self.test_raw_shape = [115, 73, 3]
        self.test_comp_shape = [28, 28, 3]

        # Read test image from file
        self.raw = cv2.imread(str(self.jpg_image_file_name))

        # Create a compressed version
        self.comp = preprocess_image(self.raw)

    def test_assert_dimensions(self):
        # Assert that dimensions on original image are correct
        self.assertEqual(self.raw.shape, tuple(self.test_raw_shape))

        # Assert that dimensions on original image are correct
        self.assertEqual(self.comp.shape, tuple(self.test_comp_shape))

    def test_verify_legal_max_min(self):
        self.assertLessEqual(np.amax(self.raw), 255)
        self.assertGreaterEqual(np.amin(self.raw), 0)

        self.assertLessEqual(np.amax(self.comp), 1.)
        self.assertGreaterEqual(np.amin(self.comp), 0.)

    def test_verify_pixel_variation(self):
        self.assertGreater(np.amax(self.raw), np.amin(self.raw))
        self.assertGreater(np.amax(self.comp), np.amin(self.comp))

    def test_truncate_filenames(self):
        """
        Test that truncate_filenames does not crash

        This test creates a directory structure with an image in it,
        truncates filenames inside it, and basically checks that it
        does not crash.
        """

        # Select a unique directory name for a new directory
        outer_dir_name = 'temp_dir'

        # Make a dir of this name
        duplicate_dir_path = self.test_dir.joinpath(outer_dir_name)
        duplicate_dir_path.mkdir(parents=True, exist_ok=True)

        # Try duplicating this dir, forcing a the addition of a '_' in
        # the new directory's name
        outer_dir_path = self.create_new_directory(outer_dir_name)

        # Create an inner directory, to  mimic the directory structure
        # that truncate_filenames() requires.
        inner_dir_path = outer_dir_path.joinpath('inner_dir')
        inner_dir_path.mkdir(parents=True, exist_ok=True)

        # Copy an image into this directory
        short_image_dest_filename = inner_dir_path.\
            joinpath("short_image_name.jpg")
        shutil.copy(self.jpg_image_file_name, short_image_dest_filename)

        # Run the function to be tested
        # No files should be truncated, unless this directory's path is
        # long in terms of characters (windows API allows max 260)
        truncate_filenames(outer_dir_path)

        # Extract list of files present in directory
        file_list = list(Path(inner_dir_path).glob('*'))

        # Make sure the right number of files exist in that directory
        self.assertEqual(len(file_list), 1)

        # Make sure no path name is longer than 255 characters
        for filepath in file_list:
            self.assertLessEqual(len(str(filepath)), 255)

        # Delete the temporary directory and its contents
        shutil.rmtree(outer_dir_path)
        shutil.rmtree(duplicate_dir_path)

    def create_new_directory(self, outer_dir_name):
        """
        Creates a directory with a unique name based on outer_dir_name

        If outer_dir_name exists, it adds underscores untill
        the directory name is unique

        Parameters
        ----------
        outer_dir_name: Base for name of new directory

        Returns
        -------
        outer_dir_path: The final directory path

        """
        outer_dir_path = self.test_dir.joinpath(outer_dir_name)
        while outer_dir_path.is_dir():
            outer_dir_name = outer_dir_name + '_'
            outer_dir_path = self.test_dir.joinpath(outer_dir_name)
        outer_dir_path.mkdir(parents=True, exist_ok=True)
        return outer_dir_path


if __name__ == '__main__':
    unittest.main()


