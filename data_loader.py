# Draw inspiration from C-MARL Framework: https://github.com/gml16/rl-medical
# Their DataLoader file: src/dataReader.py

import SimpleITK as sitk
import numpy as np
import warnings
import json

#warnings.simplefilter("ignore", category=ResourceWarning)
#__all__ = ['getLandmarksFromJSONFile', 'decodeNIFTIImage', 'ImageRecord', 'DataPancreas']

# TODO: Function to collect file paths for images and landmarks into .txt files
# TODO: Should the distance fields also be loaded, and in the same way as image_files and landmark_files?

def getLandmarksFromJSONFile(file):
    """
        Function for extracting landmarks from JSON file.

        Input: JSON file
        Output: Landmark coordinates as np.array of size (2,3)
    """

    F = open(file)
    data = json.load(F)
    t = data['markups'][0]['controlPoints']

    landmarks = []

    # Get (x,y,z)-coordinates of landmarks F-1 and F-2
    for landmark in t:
        position = landmark['position']
        x, y, z = position[0], position[1], position[2]
        landmarks.append([x, y, z])

    F.close()

    # Convert list to np.array of size (2,3)
    # Example: F-1 has coordinates [5, 10, 3] and F-2 has coordinates [2, 63, 12]
    # Then landmarks = [[5, 10, 3], [2, 63, 12]]
    landmarks = np.asarray(landmarks)
    return landmarks

# landmarks = getLandmarksFromJSONFile('../Data-Pancreas/landmarks/Pancreas0001_F.mrk.json')
# print(landmarks, np.shape(landmarks))

def decodeNIFTIImage(file):
    """
        Function for decoding a single NIFTI image.

        Input: NIFTI file
        Output: sitk_image, image
    """

    sitk_image = sitk.ReadImage(file)

    image = ImageRecord()
    image.name = file
    image.data = sitk.GetArrayFromImage(sitk_image).transpose(2, 1, 0) # Convert from (z, y, x) to (x, y, z)
    image.dims = np.shape(image.data)

    return sitk_image, image

class ImageRecord(object):
    """
        Class for image object to contain height,width, depth and name
    """
    pass

class DataPancreas(object):
    """
        Class for managing data files for Pancreas data set.

        Attributes:
            returnLandmarks: Boolean (default: True)
            agents: Number of agents
            num_files: Number of scans in data set
            image_files: List of all paths to images (from image_files.txt)
            landmark_files: List of all paths to landmarks (from landmark_files.txt)
    """

    def __init__(self, files_list = None, returnLandmarks = True, agents = 1):
        """
        Inputs:e
        :param files_list: List of four text files with all images, EDT and GDT distance fields, and landmarks
        Example: ['../Data-Pancreas/filenames/image_files.txt', '../Data-Pancreas/filenames/EDT_files.txt', '../Data-Pancreas/filenames/GDT_files.txt', '../Data-Pancreas/filenames/landmark_files.txt']

        :param returnLandmarks: Return landmarks if task is train or eval (default: True)
        :param agents: Number of agents
        """

        self.returnLandmarks = returnLandmarks
        self.agents = agents

        # Check if files_list exists
        assert files_list, 'There is no file given'

        # Read image filenames into list
        self.image_files = [line.split('\n')[0] for line in open(files_list[0])]
        self.num_files = len(self.image_files)

        if self.returnLandmarks:
            # Read EDT filenames into list
            self.EDT_files = [line.split('\n')[0] for line in open(files_list[1])]

            # Read GDT filenames into list
            self.GDT_files = [line.split('\n')[0] for line in open(files_list[2])]

            # Read landmark filenames into list
            self.landmark_files = [line.split('\n')[0] for line in open(files_list[3])]

            # Check if n_images and n_landmarks are the same
            assert len(self.image_files) == len(
                self.landmark_files), 'Number of image files is not equal to number of landmark files'

    def sample_circular(self, landmark_ids=None):
        """
            Method that returns a randomly sampled ImageRecord from the list of files.
        """

        indexes = np.arange(self.num_files)

        while True:
            for idx in indexes:
                # Get image
                sitk_image, image = decodeNIFTIImage(self.image_files[idx])

                if self.returnLandmarks:
                    # Get EDT image
                    _, EDT = decodeNIFTIImage(self.EDT_files[idx])

                    # Get GDT image
                    _, GDT = decodeNIFTIImage(self.GDT_files[idx])

                    # Get landmarks
                    landmark_file = self.landmark_files[idx]
                    all_landmarks = getLandmarksFromJSONFile(landmark_file)

                    # TODO: What does this piece of code do??? What are landmark_ids???
                    # TODO: Extracts as many landmarks as there are agents? But, even with only one agent we need both landmarks?
                    #landmarks = [np.round(all_landmarks[landmark_ids[i] % 2]) for i in range(self.agents)]
                    landmarks = all_landmarks # Array of size (2,3) containing landmarks F-1 and F-2 (MY CODE)

                else:
                    EDT = None
                    GDT = None
                    landmarks = None

                # Extract filename from path, remove .nii.gz extension
                image_filenames = [self.image_files[idx][:-7]] * self.agents
                images = [image] * self.agents

                # TODO: Also return the EDT and GDT images??
                # Yield instead of Return, in order to return one scan at a time instead of loading all into memory
                yield (images, EDT, GDT, landmarks, image_filenames, sitk_image.GetSpacing())

if __name__ == '__main__':
    files_list = ['../Data-Pancreas/filenames/image_files.txt', '../Data-Pancreas/filenames/EDT_files.txt', '../Data-Pancreas/filenames/GDT_files.txt', '../Data-Pancreas/filenames/landmark_files.txt']
    data = DataPancreas(files_list = files_list, returnLandmarks = True, agents = 1)
    sitk_image, image = decodeNIFTIImage(data.image_files[0])
    print(sitk_image, image)