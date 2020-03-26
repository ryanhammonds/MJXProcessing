#!/usr/bin/env python
'''
Created on Sun March 10 15:44:46 2020
@author: Ryan Hammonds (ryanhammonds)
'''
from workflow import create_workflow
from utils import Subject
import warnings
warnings.filterwarnings("ignore")


def get_parser():
    import argparse
    desc = 'An Automated Workflow MJX Data Processing.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('subject',
                        default=None,
                        nargs=1,
                        type=str,
                        help='Subject ID (i.e. sub-1234)\n')
    parser.add_argument('session',
                        default=None,
                        nargs=1,
                        type=str,
                        help='Subject session, either ses-01 or ses-01.\n')
    parser.add_argument('raw_dir',
                        default=None,
                        nargs=1,
                        type=str,
                        help='Path to single subject raw data folder.\n')
    parser.add_argument('bids_dir',
                        default=None,
                        nargs=1,
                        type=str,
                        help='Path to BIDS parent folder.\n')
    parser.add_argument('proc_dir',
                        default=None,
                        nargs=1,
                        type=str,
                        help='Path to write process outputs.\n')
    parser.add_argument('-qc_simg',
                        default='/mnt/Filbey/common/Studies/MJXProcessing/singularity/mriqc0.15.2rc1.simg',
                        nargs=1,
                        required=False,
                        help='Path to mriqc singularity image.\n')
    parser.add_argument('-mb_simg',
                        default='/mnt/Filbey/common/Studies/MJXProcessing/singularity/mindboggle.simg',
                        nargs=1,
                        required=False,
                        help='Path to mindboggle singularity image.\n')
    parser.add_argument('-fs_simg',
                        default='/mnt/Filbey/common/Studies/MJXProcessing/singularity/mindboggle.simg',
                        nargs=1,
                        required=False,
                        help='Path to freesurfer singularity image.\n')
    parser.add_argument('-fmri_simg',
                        default='/mnt/Filbey/common/Studies/MJXProcessing/singularity/fmriprep-20.0.5.simg',
                        nargs=1,
                        required=False,
                        help='Path to fmriprep singularity image.\n')
    parser.add_argument('-ncpus',
                        default=6,
                        nargs=1,
                        type=int,
                        required=False,
                        help='Number of cpus for parallel processing.\n')
    parser.add_argument('-run_nodes',
                        default=['mriqc', 'ants', 'freesurfer', 'mindboggle', 'fmriprep'],
                        nargs='+',
                        required=False,
                        help=f"List of nodes to run: \n" \
                             f"mriqc, ants, freesurfer, mindboggle, and/or fmriprep")
    return parser


def main():
    # Get arguments
    args = get_parser().parse_args()
    args = vars(args)

    args['subject'] = args['subject'][0]
    args['session'] = args['session'][0]
    args['raw_dir'] = args['raw_dir'][0]
    args['bids_dir'] = args['bids_dir'][0]
    args['proc_dir'] = args['proc_dir'][0]

    # Convert to BIDS
    raw_dir = args['raw_dir']
    bids_dir = args['bids_dir']
    subject = Subject(raw_dir, bids_dir)
    subject.to_bids()

    # Run entire preprocessing worflow.
    subj_id = args['subject']
    ses = args['session']
    bids_dir = args['bids_dir']
    proc_dir = args['proc_dir']
    qc_simg = args['qc_simg']
    mb_simg = args['mb_simg']
    fs_simg = args['fs_simg']
    fmri_simg = args['fmri_simg']
    ncpus = args['ncpus'][0]
    run_nodes = args['run_nodes']
    wf = create_workflow(subj_id, ses, bids_dir, proc_dir, qc_simg, mb_simg,
                         fs_simg, fmri_simg, ncpus, run_nodes)
    wf.run()


if __name__ == '__main__':
    import warnings
    warnings.filterwarnings("ignore")
    main()