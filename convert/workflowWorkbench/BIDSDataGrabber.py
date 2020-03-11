"""
BIDSDataGrabber.py
Evan Kersey
03/11/2020

practice bids data grabber and layout
"""
print("init bidsGrabber")
from nipype.interfaces.io import BIDSDataGrabber
from nipype.pipeline import Node

bg = Node(BIDSDataGrabber(), name='bids-grabber')
bg.inputs.base_dir = "/mnt/Filbey/Evan/MJXProcessing/examples/examples/BIDS"

bg.inputs.subject = 'sub-M7500516'
res = bg.run()
res.outputs
print("done")
