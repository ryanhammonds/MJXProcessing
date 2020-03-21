#!/usr/bin/env python

import os
import re
from nipype.interfaces import utility as niu
from nipype import Workflow
import nipype.pipeline.engine as pe
from nipype.interfaces.base import (CommandLine, CommandLineInputSpec, File,
                                    TraitedSpec, traits)
from utils import bids_query


class AntsCorticalThicknessInfoInputSpec(CommandLineInputSpec):
    """ Command line arguments/options for antsCorticalThickness.sh
    """
    # singularity options
    mode = traits.Bool(desc="singularity mode", mandatory=True, argstr="run",
                       position=0)
    env = traits.Bool(desc="clear env", mandatory=True, argstr="--cleanenv",
                      position=1)
    bind_in = traits.Directory(exists=True, mandatory=True,
                               argstr='-B %s:/INPUT', position=2,
                               desc='parent directory to anatomical image')
    bind_out = traits.Directory(exists=True, mandatory=True,
                                argstr='-B %s:/OUTPUT', position=3,
                                desc='parent directory to  write results')
    container = File(exists=True, mandatory=True, argstr='%s', position=4,
                     desc='path to singularity image')
    # ants options
    ants_cmd = traits.Bool(desc="ants command", default=True,
                           argstr="antsCorticalThickness.sh", position=5)
    dims = traits.Int(desc="dimensions", default=True, argstr="-d %i",
                      position=6)
    in_img = traits.Str(desc='input image', mandatory=True,
                        argstr="-a /INPUT/%s", position=7)
    out_dir = traits.Str(desc="out dir + base name", exists=False,
                         mandatory=True, argstr="-o /OUTPUT/%s", position=8)
    # template options
    template_dir = '/opt/data/OASIS-30_Atropos_template'

    f_template = f'{template_dir}/T_template0.nii.gz'
    template = traits.Bool(desc="template", default=True,
                           argstr=f"-e {f_template}", position=9)

    f_ss_template = f'{template_dir}/T_template0_BrainCerebellum.nii.gz'
    ss_template = traits.Bool(desc="skull-striped template", mandatory=True,
                              argstr=f"-t {f_ss_template}", position=10)

    f_prob_mask = f'{template_dir}/T_template0_BrainCerebellumProbabilityMask.nii.gz'
    prob_mask = traits.Bool(desc="probability mask", mandatory=True,
                            argstr=f"-m {f_prob_mask}", position=11)

    f_extract_mask = f'{template_dir}/T_template0_BrainCerebellumExtractionMask.nii.gz'
    extract_mask = traits.Bool(desc="extraction mask", mandatory=True,
                               argstr=f"-f {f_extract_mask}", position=12)

    f_priors = f"{template_dir}/Priors2/"
    priors = traits.Str(desc="priors", mandatory=True,
                         argstr=f"-p {f_priors}%s",
                         position=13)

    seed = traits.Int(desc="random seeding", mandatory=True, argstr="-u %i",
                      position=14)
    precision = traits.Int(desc="float precision", mandatory=True,
                           argstr="-j %i", position=15)


class AntsCorticalThicknessInfoOutputSpec(TraitedSpec):
    output_file = File(desc="ANTs segmentation file", exists=True)


class AntsCorticalThickness(CommandLine):
    """ Call antsCorticalThickness.sh from container.
    """
    input_spec = AntsCorticalThicknessInfoInputSpec
    output_spec = AntsCorticalThicknessInfoOutputSpec
    _cmd = 'singularity'

    def _list_outputs(self):
        import os
        out_file = 'antsBrainSegmentation.nii.gz'
        outputs = self.output_spec().get()
        outputs['seg_file'] = os.path.abspath(f"{self.inputs.out_dir}/{out_file}")
        return outputs


def run_ants(bids_dir, subj, ses, proc_dir, simg):
    anat_d = f"{bids_dir}/{subj}/{ses}/anat"
    anat_f = f"{subj}_{ses}_T1w.nii"
    bind_out = f"{proc_dir}/ants/{subj}"

    if not os.path.isdir(proc_dir):
        os.mkdir(proc_dir)
    if not os.path.isdir(f"{proc_dir}/ants"):
        os.mkdir(f"{proc_dir}/ants")
    if not os.path.isdir(f"{proc_dir}/ants/{subj}"):
        os.mkdir(f"{proc_dir}/ants/{subj}")

    ants = AntsCorticalThickness(mode=True, env=True, bind_in=anat_d,
                                 bind_out=bind_out, container=simg,
                                 ants_cmd=True, dims=3, in_img=anat_f,
                                 out_dir='ants', template=True,
                                 ss_template=True, prob_mask=True,
                                 extract_mask=True, priors='priors%d.nii.gz', seed=0,
                                 precision=1
                                 )
    #print(ants.cmdline)
    ants.run()


bids_dir = '/mnt/Filbey/common/Studies/MJXProcessing/tests/examples/BIDS'
subj = 'sub-M75005160'
ses = 'ses-01'
proc_dir = '/mnt/Filbey/common/Studies/MJXProcessing/tests/examples/PROC'
simg = '/mnt/Filbey/Ryan/toolbox/mindboggle.simg'

run_ants(bids_dir, subj, ses, proc_dir, simg)



'''
def wf_smri(bids_dir, proc_dir, subj_id, ses):
    # Pass anat data in from bids_query
    ants_wf = Workflow(name=f"ants_{subj_id}")

    input_node = pe.Node(niu.IdentityInterface(fields=['bids_dir', 'subj_id',
                                                       'ses']),
                         name='input_node')
    input_node.inputs.bids_dir = bids_dir
    input_node.inputs.subj_id = subj_id
    input_node.inputs.ses = ses

    qbids_node = pe.Node(bids_query(bids_dir, subj_id, ses), name='qbids_node')

    ants_wf.add_nodes([input_node, qbids_node])
    ants_wf.connect = [(input_node, qbids_node, [('anat', 'anat')])]

    # Build ants command
    def _ants_segment(in_img, out_dir):
        import os.path as op
        in_dir = op.dirname(in_img)
        _, f_img = op.split(in_img)
        cmd = f"singularity run --cleanenv -B {in_dir}:/INPUT " \
              f"-B {out_dir}:/OUTPUT " \
              f"/mnt/Filbey/Ryan/toolbox/mindboggle.simg " \
              f"antsCorticalThickness.sh -d 3 -a /DOCK/data/$ID/T1w.nii " \
              f"-o $OUTPUT/ants_subjects/$ID/ants " \
              f"-e $TEMPLATE/T_template0.nii.gz " \
              f"-t $TEMPLATE/T_template0_BrainCerebellum.nii.gz " \
              f"-m $TEMPLATE/T_template0_BrainCerebellumProbabilityMask.nii.gz " \
              f"-f $TEMPLATE/T_template0_BrainCerebellumExtractionMask.nii.gz " \
              f"-p $TEMPLATE/Priors2/priors%d.nii.gz " \
              f"-u 0 " \
              f"-j 1"

    input_node = pe.Node(niu.Function(inputs_names=['bids_dir', 'subj_id', 'ses']
                                      output_names=['anat', 'func', 'dwi', 'fmap']
                                      function=bids_query)
                         name='bids_query')
    '''
