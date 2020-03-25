#!/usr/bin/env python
'''
Created on Sun March 10 15:44:46 2020
@author: Ryan Hammonds (ryanhammonds)
'''
import os
import json
from nipype import Workflow
import nipype.pipeline.engine as pe
from nipype.interfaces import utility as niu
from interfaces import (
    AntsCorticalThickness, FreesurferMB, Mindboggle, Fmriprep, Mriqc
)


def create_workflow(
    subj_id,
    ses,
    bids_dir,
    proc_dir,
    qc_simg='/mnt/Filbey/common/Studies/MJXProcessing/singularity/mriqc0.15.2rc1.simg',
    mb_simg='/mnt/Filbey/common/Studies/MJXProcessing/singularity/mindboggle.simg',
    fs_simg='/mnt/Filbey/common/Studies/MJXProcessing/singularity/freesurfer_6.0.simg',
    fmri_simg='/mnt/Filbey/common/Studies/MJXProcessing/singularity/fmriprep-20.0.5.simg',
    ncpus=6,
    run_nodes=['mriqc', 'ants', 'freesurfer', 'mindboggle', 'fmriprep']
):
    """ Create sMRI and fMRI workflow:
        mriqc, ants, freesurfer, mindboggle, fmriprep

    Parameters
    ----------
    bids_dir : str
        path to bids directory
    subj_id : str
        subject's ursi/id as in bids_dir ex: sub-1234
    ses : string
        session number, either ses-01 or ses-02
    proc_dir : str
        path to write processed outputs
    mriqc_simg : str
        path to mriqc singularity image
    mb_simg : str
        path to minboggle singularity image
    fmri_simg : str
        path to fmriprep singularity image
    ncpus : int
        number of cpus for parallel processing
    run_nodes: list of strings
        specifies which nodes to run.
        'mindboggle' will requires 'ants' and 'freesurfer' to run.
        'fmriprep' will requires 'freesurfer' to run.

    Returns
    -------
    wf : nipype.pipeline.engine.workflows.Workflow
        nipype workflow
    """
    # Make output directories
    if not os.path.exists(proc_dir):
        os.mkdir(proc_dir)
    if not os.path.exists(f"{proc_dir}/workflows"):
        os.mkdir(f"{proc_dir}/workflows")

    # Ensure bids compliant
    if not os.path.exists(f"{bids_dir}/dataset_description.json"):
        desc = {"Name": "MJX Study", "BIDSVersion": "1.2.2"}
        with open(f'{bids_dir}/dataset_description.json', 'w') as f:
            json.dump(desc, f, indent='\t')

    wf = Workflow(name="wf_all", base_dir=f"{proc_dir}/workflows/{subj_id}")

    # Specify subject/session specific info
    input_node = pe.Node(niu.IdentityInterface(fields=['subj_id', 'ses',
                                                       'bids_dir', 'proc_dir',
                                                       'qc_simg', 'mb_simg',
                                                       'fs_simg', 'fmri_simg',
                                                       'ncpus']),
                         name='input_node')
    input_node.inputs.subj_id = subj_id
    input_node.inputs.ses = ses
    input_node.inputs.bids_dir = bids_dir
    input_node.inputs.proc_dir = proc_dir
    input_node.inputs.qc_simg = qc_simg
    input_node.inputs.mb_simg = mb_simg
    input_node.inputs.fs_simg = fs_simg
    input_node.inputs.fmri_simg = fmri_simg
    input_node.inputs.ncpus = ncpus

    # Lazy evaluation of run_nodes
    if 'mindboggle' in run_nodes and 'freesurfer' not in run_nodes:
        raise ValueError("Mindboggle requires freesurfer and ants.\n"
                         "If these pre-requistes have been ran:\n"
                         "1) run mindboggle manually\n"
                         "2) alter the code here and in interfaces\n" 
                         "   to be more flexible.")
    elif 'mindboggle' in run_nodes and 'ants' not in run_nodes:
        raise ValueError("Mindboggle requires freesurfer and ants.\n"
                         "If these pre-requistes have been ran:\n"
                         "1) run mindboggle manually\n"
                         "2) alter the code here and in interfaces\n" 
                         "   to be more flexible.")
    elif 'fmriprep' in run_nodes and 'freesurfer' not in run_nodes:
        raise ValueError("Fmriprep requires freesurfer to be ran.\n"
                         "If this pre-requiste has been ran:\n"
                         "1) run fmriprep manually\n"
                         "2) alter the code in workflow and\n"
                         "   interface to be more flexible.")

    # Mriqc
    if 'mriqc' in run_nodes:
        try:
            os.mkdir(f"{proc_dir}/mriqc")
        except FileExistsError:
            pass
        qc_node = pe.Node(Mriqc(), name='mriqc')
        qc_node.inputs.mode = 'run'
        qc_node.inputs.env = '--cleanenv'
        qc_node.inputs.io_partic = True
        # Connections into mriqc
        def half(ncpus): return int(ncpus/2)  # modern lamda replacement
        def mem_calc(ncpus): return int(ncpus*2)  # alters ncpus for other args
        def cut_sub(subj): return subj[4:]
        wf.connect([(input_node, qc_node, [('bids_dir', 'bind_in'),
                                           ('proc_dir', 'bind_out'),
                                           ('qc_simg', 'container'),
                                           (('subj_id', cut_sub), 'partic_lab'),
                                           ('ncpus', 'ncpus'),
                                           (('ncpus', half), 'ants_threads'),
                                           (('ncpus', mem_calc), 'mem')])])

    # ANTs segmentation
    if 'ants' in run_nodes:
        try:
            os.mkdir(f"{proc_dir}/ants")
        except FileExistsError:
            pass

        try:
            os.mkdir(f"{proc_dir}/ants/{subj_id}")
        except FileExistsError:
            pass

        ants_node = pe.Node(AntsCorticalThickness(), name='ants')
        ants_node.inputs.mode = 'run'
        ants_node.inputs.env = '--cleanenv'
        ants_node.inputs.ants_cmd = 'antsCorticalThickness.sh'
        ants_node.inputs.dims = 3
        ants_node.inputs.template = True
        ants_node.inputs.ss_template = True
        ants_node.inputs.prob_mask = True
        ants_node.inputs.extract_mask = True
        ants_node.inputs.priors = 'priors%d.nii.gz'
        ants_node.inputs.seed = 0
        ants_node.inputs.precision = 1
        ants_node.inputs.in_img = f"{subj_id}/{ses}/anat/{subj_id}_{ses}_T1w.nii"
        ants_node.inputs.out = f"ants/{subj_id}/ants"
        # Connections into ants
        wf.connect([(input_node, ants_node, [('bids_dir', 'bind_in'),
                                             ('proc_dir', 'bind_out'),
                                             ('mb_simg', 'container')])])

    # Freesurfer
    if 'freesurfer' in run_nodes:
        try:
            os.mkdir(f"{proc_dir}/freesurfer")
        except FileExistsError:
            pass

        fs_node = pe.Node(FreesurferMB(), name='freesurfer')
        fs_node.inputs.mode = 'run'
        fs_node.inputs.env = '--cleanenv'
        fs_node.inputs.bind_fs_home = '$FREESURFER_HOME'
        fs_node.inputs.fs_cmd = 'recon-all -all'
        fs_node.inputs.fs_sd = 'freesurfer'
        fs_node.inputs.in_img = f"{subj_id}/{ses}/anat/{subj_id}_{ses}_T1w.nii"
        fs_node.inputs.parallel = True
        # Connections into freesurfer
        wf.connect([(input_node, fs_node, [('bids_dir', 'bind_in'),
                                           ('proc_dir', 'bind_out'),
                                           ('fs_simg', 'container'),
                                           ('subj_id', 'fs_id'),
                                           ('ncpus', 'fs_mp')])])

    # Mindboggle
    if 'mindboggle' in run_nodes:
        try:
            os.mkdir(f"{proc_dir}/mindboggled")
        except FileExistsError:
            pass

        mb_node = pe.Node(Mindboggle(), name='mindboggle')
        mb_node.inputs.mode = 'run'
        mb_node.inputs.env = '--cleanenv'
        mb_node.inputs.mb_cmd = 'mindboggle'
        mb_node.inputs.out = 'mindboggled'
        mb_node.inputs.vis_color = True
        # Connections into mindboggle
        wf.connect([(input_node, mb_node, [('proc_dir', 'bind_in'),
                                           ('mb_simg', 'container'),
                                           ('ncpus', 'ncpus')])])
        wf.connect([(fs_node, mb_node, [('recon_dir', 'fs_dir')])])
        wf.connect([(ants_node, mb_node, [('seg_file', 'ants_seg')])])

    # Fmriprep
    if 'fmriprep' in run_nodes:
        fmri_node = pe.Node(Fmriprep(), name='fmriprep')
        fmri_node.inputs.mode = 'run'
        fmri_node.inputs.env = '--cleanenv'
        fmri_node.inputs.bind_fs_home = '$FREESURFER_HOME'
        fmri_node.inputs.skip_validation = True
        fmri_node.inputs.aroma = True
        fmri_node.inputs.out_space = 'MNI152NLin6Asym T1w'
        fmri_node.inputs.fs_license = True
        fmri_node.inputs.io_partic = True
        # Connections into fmriprep
        wf.connect([(input_node, fmri_node, [('bids_dir', 'bind_in'),
                                             ('proc_dir', 'bind_out'),
                                             ('fmri_simg', 'container'),
                                             ('subj_id', 'partic_lab'),
                                             ('ncpus', 'nthreads')])])

        def parent_dir(p): return p.split('/')[0]
        wf.connect(fs_node, ('recon_dir', parent_dir), fmri_node, 'recon_dir')

    return wf
