import SimpleITK as sitk
import dicom2nifti as d2n

# Convert a DICOM series (one scan) into a single nifti (.nii.gz) file
def convert_dicom_to_nifti(dicom_directory, output_file):
    # https://github.com/icometrix/dicom2nifti/issues/11
    # Download latest GDCM and install it: https://github.com/malaterre/GDCM/releases
    # d2n.settings.set_gdcmconv_path('C:/Program Files/GDCM 3.0/bin/gdcmconv.exe')
    d2n.dicom_series_to_nifti(dicom_directory, output_file, reorient_nifti=True)

# Resample an image to have isotropic voxel sizes
def resample_image(in_file, out_file):
    image = sitk.ReadImage(in_file)

    # Desired iso-tropic voxel side length
    desired_spacing = 0.5

    # In slice size and spacing
    current_n_vox = image.GetWidth()
    current_spacing = image.GetSpacing()
    new_n_vox_in_slice = int(current_n_vox * current_spacing[0] / desired_spacing)

    # voxel size and number of voxels in the direction of the patient
    depth_spacing = current_spacing[2]
    n_vox_depth = image.GetDepth()

    new_n_vox_depth = int(n_vox_depth * depth_spacing / desired_spacing)

    new_volume_size = [new_n_vox_in_slice, new_n_vox_in_slice, new_n_vox_depth]
    print(f"New volume size: {new_volume_size}")

    # Create new image with desired properties
    new_image = sitk.Image(new_volume_size, image.GetPixelIDValue())
    new_image.SetOrigin(image.GetOrigin())
    new_image.SetSpacing([desired_spacing, desired_spacing, desired_spacing])
    new_image.SetDirection(image.GetDirection())

    # Make translation with no offset, since sitk.Resample needs this arg.
    translation = sitk.TranslationTransform(3)
    translation.SetOffset((0, 0, 0))

    interpolator = sitk.sitkLinear

    # Create final resampled image
    resampled_image = sitk.Resample(image, new_image, translation, interpolator)

    sitk.WriteImage(resampled_image, out_file)

if __name__ == '__main__':
    dicom_directory = "C:/Users/annae/OneDrive - Danmarks Tekniske Universitet/Bachelorprojekt/Data/Pancreas-data/PANCREAS_0009/11-24-2015-PANCREAS0009-Pancreas-12471/Pancreas-31748"

    nifti_file = "C:/Users/annae/OneDrive - Danmarks Tekniske Universitet/Bachelorprojekt/Data/Pancreas-data-slicer/Pancreas_0009-001/pancreas_0009-001.nii.gz"
    nifti_isotropic_file = "C:/Users/annae/OneDrive - Danmarks Tekniske Universitet/Bachelorprojekt/Data/Pancreas-data-slicer/Pancreas_0009-001/pancreas_0009-001_isotropic.nii.gz"
    slicer_scan_dir = "C:/Users/annae/OneDrive - Danmarks Tekniske Universitet/Bachelorprojekt/Data/Pancreas-data-slicer/Pancreas_0009-001"
    crop_volume = "C:/Users/annae/OneDrive - Danmarks Tekniske Universitet/Bachelorprojekt/Data/Pancreas-data-slicer/Pancreas_0009-001/pancreas_0009-001_isotropic_cropped.nii.gz"

    # Choose what to do:
    convert_dicom_to_nifti(dicom_directory, nifti_file)
    print('Nifti file created!')
    resample_image(nifti_file, nifti_isotropic_file)
    print('Isotropic file created!')