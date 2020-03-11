from nipype import Node, JoinNode, Workflow
from nipype import Node, JoinNode, Workflow
from nipype.interfaces import (ants, fsl)
from nipype.interfaces.utility import IdentityInterface

# make subjects with subject class
import Subject

#### TODO TODO TODO start
# get first feature working!!!
# need to get data pointing to first node which is ants or freesurfer (reconall)
# for this I need to define the identity interface first with the input scans from subject
### TODO TODO TODO end

out_path = "/home/evan/Filbey/Evan/BIDS"
print("making subject array")
subjectList = [Subject]  # Subject
print("array created")
print("adding test subject")
subjectList.append(("/home/evan/Filbey/common/Studies/MJXProcessing/examples/NL/sub-1126", out_path,
                    "/home/evan/Filbey/Evan"))
print("test subject created")

print("making workflow object")
wf = Workflow(name='preprocess')
print("workflow wf created")
# infospec is a node that makes a subject identity. identity matrix is what Subject.py was trying to accomplish
print("trying to add Subject to wf")
inputspec = Node(IdentityInterface(fields=['image']),
                 name='inputspec')
inputspec = Node(IdentityInterface(fields=[]))
# these look like the images that will be processed in this node. Subject.seq might work here
inputspec.iterables = [('image',
                        ['img1.nii', 'img2.nii', 'img3.nii'])]
# not sure what this is, applys img2flt (?) need to ask Ryan
img2flt = Node(fsl.ImageMaths(out_data_type='float'),
               name='img2flt')
# connects the first node with the second node
wf.connect(inputspec, 'image', img2flt, 'in_file')
# 3rd node
average = JoinNode(ants.AverageImages(), joinsource='inputspec',
                   joinfield='images', name='average')
# add new node to wf
wf.connect(img2flt, 'out_file', average, 'images')
# new node
realign = Node(fsl.FLIRT(), name='realign')
# add to wf after img2flt & after average
wf.connect(img2flt, 'out_file', realign, 'in_file')
wf.connect(average, 'output_average_image', realign, 'reference')

strip = Node(fsl.BET(), name='strip')
wf.connect(realign, 'out_file', strip, 'in_file')
