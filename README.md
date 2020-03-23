Nipype powered workflow for MJX study.

This workflow is designed to run on a HPC using singularity containers:
	
	singularity build mriqc0.15.2.simg docker://poldracklab/mriqc:0.15.2rc1
	singularity pull mindboggle.simg docker://nipy/mindboggle
	singularity build fmriprep-1.5.2.simg docker://poldracklab/fmriprep:1.5.2

sMRI Preprocessing:
	
	mriqc (mriqc container)
	ants (mindboggle containter)
	freesurfer (mindboggle container)
	mindboggle (mindboggle container)

fMRI Preprocessing:
	
	mriqc (mriqc container)
	fmriprep (fmriprep container)

dMRI Preprocessing:
	
	fsl

Eprime and Presentation Parsing.

	Custom python scripts.
