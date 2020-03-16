from bids.layout import BIDSLayout
layout = BIDSLayout("examples/examples/BIDS")
print(layout.get_subjects)
print(layout.get_modalities())
print(layout.get(subject='M75005160', extensions=['.nii'], return_type='file'))