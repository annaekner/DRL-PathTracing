import os.path
import SimpleITK as sitk
import numpy as np
from scipy.ndimage import distance_transform_edt
import json

# Function for reading landmarks F-1 and F-2
def read_landmarks(file_name):
    f = open(file_name)

    # https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html
    # returns JSON object as a dictionary
    data = json.load(f)
    t = data['markups'][0]['controlPoints']

    lms = []
    for lm in t:
        pos = lm['position']
        x = pos[0]
        y = pos[1]
        z = pos[2]
        lms.append([x, y, z])
    f.close()
    return lms

# Function for computing three EDT distance fields
def compute_distance_map_from_segmentation(slicer_scan_folder):
    in_seg_name = os.path.join(slicer_scan_folder, 'Segmentation-Segment_1-label.nii.gz')
    dist_out_name = os.path.join(slicer_scan_folder, 'Segmentation_distance_field.nii.gz')
    dist_negative_out_name = os.path.join(slicer_scan_folder, 'Segmentation_negative_distance_field.nii.gz')
    dist_signed_out_name = os.path.join(slicer_scan_folder, 'Segmentation_signed_distance_field.nii.gz')

    img_segm = sitk.ReadImage(in_seg_name)
    img_segm_np = sitk.GetArrayFromImage(img_segm)
    print(f"SITK segmentation image size: {img_segm.GetSize()}")
    segm_dist_image = distance_transform_edt(img_segm_np)
    img_sitk_out = sitk.GetImageFromArray(segm_dist_image)
    img_sitk_out.SetOrigin(img_segm.GetOrigin())
    img_sitk_out.SetSpacing(img_segm.GetSpacing())
    img_sitk_out.SetDirection(img_segm.GetDirection())
    sitk.WriteImage(img_sitk_out, dist_out_name)

    img_segm_inside = segm_dist_image.copy()

    img_segm_np = np.logical_not(img_segm_np)
    segm_dist_image = distance_transform_edt(img_segm_np)
    img_sitk_out = sitk.GetImageFromArray(-segm_dist_image)
    img_sitk_out.SetOrigin(img_segm.GetOrigin())
    img_sitk_out.SetSpacing(img_segm.GetSpacing())
    img_sitk_out.SetDirection(img_segm.GetDirection())
    sitk.WriteImage(img_sitk_out, dist_negative_out_name)

    img_signed_dist = img_segm_inside - segm_dist_image
    img_sitk_out = sitk.GetImageFromArray(img_signed_dist)
    img_sitk_out.SetOrigin(img_segm.GetOrigin())
    img_sitk_out.SetSpacing(img_segm.GetSpacing())
    img_sitk_out.SetDirection(img_segm.GetDirection())
    sitk.WriteImage(img_sitk_out, dist_signed_out_name)

# Function for computing GDT distance field
def compute_fast_marching_from_segmentation(slicer_scan_folder):
    in_seg_name = os.path.join(slicer_scan_folder, 'Segmentation-Segment_1-label.nii.gz')
    in_landmark_name = os.path.join(slicer_scan_folder, 'F.mrk.json')
    out_name = os.path.join(slicer_scan_folder, 'Segmentation_fast_marching.nii.gz')
    # out_name_2 = os.path.join(slicer_scan_folder, 'Segmentation_fast_marching_filled.nii.gz')

    lms = read_landmarks(in_landmark_name)

    img_segm = sitk.ReadImage(in_seg_name)
    print(f"SITK segmentation image size: {img_segm.GetSize()}")

    aorta_lm = img_segm.TransformPhysicalPointToIndex(lms[0])

    fast_marching = sitk.FastMarchingImageFilter()
    seed_value = 0
    trial_point = (aorta_lm[0], aorta_lm[1], aorta_lm[2], seed_value)

    stopping_time = 1000
    fast_marching.AddTrialPoint(trial_point)
    fast_marching.SetStoppingValue(stopping_time)

    fast_marching_output = fast_marching.Execute(img_segm)
    out_image = sitk.Threshold(fast_marching_output, lower=0.0, upper=stopping_time, outsideValue=-1)
    sitk.WriteImage(out_image, out_name)

if __name__ == '__main__':
    slicer_scan_dir = "C:/Users/annae/OneDrive - Danmarks Tekniske Universitet/Bachelorprojekt/Data/Pancreas-data-slicer/Pancreas_0009-001"
    crop_volume = "C:/Users/annae/OneDrive - Danmarks Tekniske Universitet/Bachelorprojekt/Data/Pancreas-data-slicer/Pancreas_0009-001/pancreas_0009-001_isotropic cropped.nii.gz"

    # read_landmarks(os.path.join(slicer_scan_dir, 'F.mrk.json'))
    # compute_distance_map_from_segmentation(slicer_scan_dir)
    # compute_fast_marching_from_segmentation(slicer_scan_dir)
