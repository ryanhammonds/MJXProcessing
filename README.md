Nipype powered workflow for MJX study.

This workflow is designed to run on a HPC using singularity containers:
	singularity pull mindboggle.simg docker://nipy/mindboggle
	singularity build fmriprep-1.5.2.simg docker://poldracklab/fmriprep:1.5.2

sMRI Preprocessing:
	ANTs
	Freesurfer
	Mindboggle

fMRI Preprocessing:
	Fmriprep

dMRI Preprocessing:
	FSL

Eprime and Presentation Parsing.
