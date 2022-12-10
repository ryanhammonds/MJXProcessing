Nipype powered workflow for MJX study.

This workflow is designed to run on a HPC using singularity containers:
	
	singularity build mriqc0.15.2.simg docker://poldracklab/mriqc:0.15.2rc1
	singularity pull mindboggle.simg docker://nipy/mindboggle
	singularity pull freesurfer_v6.simg docker://freesurfer/freesurfer:6.0
	singularity build fmriprep-1.5.2.simg docker://poldracklab/fmriprep:1.5.2

sMRI Preprocessing:
	
	mriqc (mriqc container)
	ants (mindboggle containter)
	freesurfer (freesurfer container)
	mindboggle (mindboggle container)

fMRI Preprocessing:
	
	mriqc (mriqc container)
	fmriprep (fmriprep container)
