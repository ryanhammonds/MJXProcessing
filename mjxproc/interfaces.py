#!/usr/bin/env python
'''
Created on Sun March 10 15:44:46 2020
@author: Ryan Hammonds (ryanhammonds)
'''
from nipype.interfaces.base import (
    CommandLine, CommandLineInputSpec,
    File, TraitedSpec, traits
)


class MriqcInfoInputSpec(CommandLineInputSpec):
    """ Command line arguments/options for mriqc
    """
    # singularity arguments
    mode = traits.Str(
        argstr="%s",
        desc="singularity mode",
        mandatory=True,
        position=0
    )
    env = traits.Str(
        argstr="%s",
        desc="clear host env variables",
        mandatory=True,
        position=1
    )
    bind_in = traits.Directory(
        argstr='-B %s:/BIDS',
        desc='parent directory to anatomical image',
        exists=True,
        mandatory=True,
        position=2
    )
    bind_out = traits.Directory(
        argstr='-B %s:/PROC',
        desc='parent direct to outputs',
        exists=True,
        mandatory=True,
        position=3
    )
    container = File(
        argstr='%s',
        desc='path to singularity image',
        exists=True,
        mandatory=True,
        position=4
    )
    # mriqc arguments
    io_partic = traits.Bool(
        argstr='/BIDS /PROC/mriqc participant',
        desc='required positional arguments',
        mandatory=True,
        position=5
    )
    partic_lab = traits.Str(
        argstr='--participant_label %s',
        desc='subject id/ursi',
        mandatory=True,
        position=6
    )
    ncpus = traits.Int(
        argstr='--n_cpus %i',
        desc='number of cpus',
        mandatory=True,
        position=7
    )
    ants_threads = traits.Int(
        argstr='--ants-nthreads %i',
        desc=f"cpus per ants: requires cpus/2 since ants threads typically\n"
             f"require 4GB per cpu and our cpus have 2GB per cpu.",
        mandatory=True,
        position=8
    )
    mem = traits.Int(
        argstr='--mem_gb %i',
        desc=f"memory required, based on cpus, for cases when all cpus on a\n"
             f"node are in use.",
        mandatory=True,
        position=9
    )


class MriqcInfoOutputSpec(TraitedSpec):
    qc_dir = traits.Directory(desc="mriqc directory", exists=False)


class Mriqc(CommandLine):
    """ Call mriqc from singularity container.
    """
    input_spec = MriqcInfoInputSpec
    output_spec = MriqcInfoOutputSpec
    _cmd = 'singularity'
    #_cmd = 'echo'

    def _list_outputs(self):
        outputs = {}
        outputs['qc_dir'] = f"{self.inputs.bind_out}/mriqc"
        return outputs


class AntsCorticalThicknessInfoInputSpec(CommandLineInputSpec):
    """ Command line arguments/options for antsCorticalThickness.sh
    """
    # singularity arguments
    mode = traits.Str(
        argstr="%s",
        desc="singularity mode",
        mandatory=True,
        position=0
    )
    env = traits.Str(
        argstr="%s",
        desc="clear host env variables",
        mandatory=True,
        position=1,
    )
    bind_in = traits.Directory(
        argstr='-B %s:/INPUT',
        desc='parent directory to anatomical image',
        exists=True,
        mandatory=True,
        position=2
    )
    bind_out = traits.Directory(
        argstr='-B %s:/OUTPUT',
        desc='parent directory to  write results',
        exists=True,
        mandatory=True,
        position=3,
    )
    container = File(
        argstr='%s',
        desc='path to singularity image',
        exists=True,
        mandatory=True,
        position=4
    )
    # ants arguments
    ants_cmd = traits.Str(
        argstr="%s",
        desc="ants command",
        mandatory=True,
        position=5
    )
    dims = traits.Int(
        argstr="-d %i",
        desc="dimensionality of data",
        mandatory=True,
        position=6
    )
    in_img = traits.Str(
        argstr="-a /INPUT/%s",
        desc='input image',
        mandatory=True,
        position=7,
    )
    out = traits.Str(
        argstr="-o /OUTPUT/%s",
        desc="output direcory with file prefix",
        exists=False,
        mandatory=True,
        position=8
    )
    # template aguments
    template_dir = '/opt/data/OASIS-30_Atropos_template'

    f_template = f'{template_dir}/T_template0.nii.gz'
    template = traits.Bool(
        argstr=f"-e {f_template}",
        desc="template image",
        default=True,
        position=9
    )

    f_ss_template = f'{template_dir}/T_template0_BrainCerebellum.nii.gz'
    ss_template = traits.Bool(
        argstr=f"-t {f_ss_template}",
        desc="skull-striped template image",
        mandatory=True,
        position=10
    )

    f_prob_mask = f'{template_dir}/T_template0_BrainCerebellumProbabilityMask.nii.gz'
    prob_mask = traits.Bool(
        argstr=f"-m {f_prob_mask}",
        desc="probability mask image",
        mandatory=True,
        position=11
    )

    f_extract_mask = f'{template_dir}/T_template0_BrainCerebellumExtractionMask.nii.gz'
    extract_mask = traits.Bool(
        argstr=f"-f {f_extract_mask}",
        desc="extraction mask",
        mandatory=True,
        position=12
    )

    f_priors = f"{template_dir}/Priors2/"
    priors = traits.Str(
        argstr=f"-p {f_priors}%s",
        desc="priors images specific with c syntax",
        mandatory=True,
        position=13,
    )
    # performance arguments
    seed = traits.Int(
        argstr="-u %i",
        desc="random seed",
        mandatory=True,
        position=14
    )
    precision = traits.Int(
        argstr="-j %i",
        desc="float precision, added for reduced memory usage",
        mandatory=True,
        position=15
    )


class AntsCorticalThicknessInfoOutputSpec(TraitedSpec):
    seg_file = traits.Directory(desc="ANTs segmentation file", exists=False)


class AntsCorticalThickness(CommandLine):
    """ Call antsCorticalThickness.sh from Mindboggle container.
    """
    input_spec = AntsCorticalThicknessInfoInputSpec
    output_spec = AntsCorticalThicknessInfoOutputSpec
    _cmd = 'singularity'
    #_cmd = 'echo'

    def _list_outputs(self):
        outputs = {}
        outputs['seg_file'] = f"{self.inputs.out}"
        return outputs


class FreesurferMBInfoInputSpec(CommandLineInputSpec):
    """ Command line arguments/options for recon-all
    """
    # singularity arguments
    mode = traits.Str(
        argstr="%s",
        desc="singularity mode",
        mandatory=True,
        position=0
    )
    env = traits.Str(
        argstr="%s",
        desc="clear host env variables",
        mandatory=True,
        position=1
    )
    bind_in = traits.Directory(
        argstr='-B %s:/BIDS',
        exists=True,
        desc='parent directory to anatomical image',
        mandatory=True,
        position=2
    )
    bind_out = traits.Directory(
        argstr='-B %s:/PROC',
        desc='parent directory to  write results',
        exists=True,
        mandatory=True,
        position=3
    )
    bind_fs_home = traits.Str(
        argstr='-B %s:/opt/freesurfer/',
        desc='allow access to fs license',
        mandatory=True,
        position=4
    )
    container = File(
        argstr='%s',
        desc='path to singularity image',
        exists=True,
        mandatory=True,
        position=5,
    )
    # freesurfer arguments
    fs_cmd = traits.Str(
        argstr="%s",
        desc="freesurfer command command",
        mandatory=True,
        position=6
    )
    in_img = traits.Str(
        argstr="-i /BIDS/%s",
        desc="anatomical image",
        mandatory=True,
        position=7
    )
    fs_id = traits.Str(
        argstr='-s %s',
        mandatroy=True,
        desc="subj id",
        position=8
    )
    fs_sd = traits.Str(
        argstr='-sd /PROC/%s',
        desc="output directory",
        mandatory=True,
        position=9
    )
    parallel = traits.Bool(
        argstr='-parallel',
        desc='parallel processing',
        mandatory=True,
        postiion=10
    )
    fs_mp = traits.Int(
        argstr="-openmp %i",
        desc='number of cpus',
        mandatory=True,
        position=11
    )


class FreesurferMBInfoOutputSpec(TraitedSpec):
    recon_dir = traits.Directory(desc="recon-all dir", exists=False)


class FreesurferMB(CommandLine):
    """ Run recon-all from mindboggle singularity image
    """
    input_spec = FreesurferMBInfoInputSpec
    output_spec = FreesurferMBInfoOutputSpec
    _cmd = 'singularity'
    #_cmd = 'echo'

    def _list_outputs(self):
        outputs = {}
        outputs['recon_dir'] = f"freesurfer/{self.inputs.fs_id}"
        return outputs


class MindboggleInfoInputSpec(CommandLineInputSpec):
    """ Command line arguments/options for mindboggle
    """
    # singularity arguments
    mode = traits.Str(
        argstr="%s",
        desc="singularity mode",
        mandatory=True,
        position=0
    )
    env = traits.Str(
        argstr="%s",
        desc="clear host env variables",
        mandatory=True,
        position=1
    )
    bind_in = traits.Directory(
        argstr='-B %s:/PROC',
        desc='parent directory to anatomical image',
        exists=True,
        mandatory=True,
        position=2
    )
    container = File(
        argstr='%s',
        desc='path to singularity image',
        exists=True,
        mandatory=True,
        position=3
    )

    # mindboggle arguments
    mb_cmd = traits.Str(
        argstr='%s',
        desc='call mindboggle',
        mandatory=True,
        position=4
    )
    fs_dir = traits.Str(
        argstr='/PROC/%s',
        desc='recon-all directory',
        mandatory=True,
        position=5
    )
    out = traits.Str(
        argstr="--out /PROC/%s",
        desc='ouput directory',
        mandatory=True,
        position=6
    )
    vis_color = traits.Bool(
        argstr='--roygbiv',
        desc='visualize vtk outputs with color',
        mandatory=True,
        position=7
    )
    ants_seg = traits.Str(
        argstr='--ants /PROC/%sBrainSegmentation.nii.gz',
        desc='ants brain segmentation file',
        mandatory=True,
        position=8
    )
    ncpus = traits.Int(
        argstr='--cpus %i',
        desc='number of cpus',
        mandatory=True,
        position=9
    )


class MindboggleInfoOutputSpec(TraitedSpec):
    mb_dir = traits.Directory(desc="mindboggle dir", exists=False)


class Mindboggle(CommandLine):
    """ Run mindboggle from singularity image
    """
    input_spec = MindboggleInfoInputSpec
    output_spec = MindboggleInfoOutputSpec
    _cmd = 'singularity'
    #_cmd = 'echo'

    def _list_outputs(self):
        outputs = {}
        outputs['mb_dir'] = f"{self.inputs.out}/{self.inputs.fs_dir}"
        return outputs


class FmriprepInfoInputSpec(CommandLineInputSpec):
    """ Command line arguments/options for fmriprep
    """
    # singularity arguments
    mode = traits.Str(
        argstr="%s",
        desc="singularity mode",
        mandatory=True,
        position=0
    )
    env = traits.Str(
        argstr="%s",
        desc="clear host env variables",
        mandatory=True,
        position=1
    )
    bind_in = traits.Directory(
        argstr='-B %s:/BIDS',
        desc='parent directory to anatomical image',
        exists=True,
        mandatory=True,
        position=2
    )
    bind_out = traits.Directory(
        argstr='-B %s:/PROC',
        desc='parent direct to outputs',
        exists=True,
        mandatory=True,
        position=3
    )
    bind_fs_home = traits.Str(
        argstr='-B %s:/FREESURFER_HOME',
        desc='allow access to fs license',
        mandatory=True,
        position=4
    )
    container = File(
        argstr='%s',
        desc='path to singularity image',
        exists=True,
        mandatory=True,
        position=5
    )
    # fmriprep arguments
    io_partic = traits.Bool(
        argstr='/BIDS /PROC participant',
        mandatory=True,
        position=6
    )
    skip_validation = traits.Bool(
        argstr='--skip_bids_validation',
        desc='skip bids validation',
        mandatory=True,
        position=7
    )
    partic_lab = traits.Str(
        argstr='--participant_label %s',
        desc='subject id',
        mandatory=True,
        position=8
    )
    nthreads = traits.Int(
        argstr='--omp-nthreads %i',
        desc='number of cpus',
        mandatory=True,
        position=9
    )
    aroma = traits.Bool(
        argstr='--use-aroma',
        dec='ICA motion artifact denoising',
        mandatory=True,
        position=10
    )
    out_space = traits.Str(
        argstr='--output-spaces %s',
        desc='define output space(s) of results, space separated',
        mandatory=True,
        position=11
    )
    recon_dir = traits.Str(
        argstr='--fs-subjects-dir /PROC/%s',
        desc='path to recon-all parent directory',
        exists=True,
        mandatory=True,
        position=12
    )
    fs_license = traits.Bool(
        argstr='--fs-license-file /FREESURFER_HOME/license.txt',
        desc='path to freesurfer license',
        mandatory=True,
        position=13
    )


class FmriprepInfoOutputSpec(TraitedSpec):
    fmri_dir = traits.Str(desc="freesurfer dir")


class Fmriprep(CommandLine):
    """ Run fmriprep from singularity image
    """
    input_spec = FmriprepInfoInputSpec
    output_spec = FmriprepInfoOutputSpec
    _cmd = 'singularity'
    #_cmd = 'echo'

    def _list_outputs(self):
        outputs = {}
        outputs['fmri_dir'] = f"fmriprep/{self.inputs.partic_lab}"
        return outputs
