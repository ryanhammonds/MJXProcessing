#!/usr/bin/env python3

import sys
import os
import re
import glob
import warnings
import subprocess


class Subject:
    """
    Subject class for setting up BIDS, conversion to nifti and preprocessing.
    ...
    Attributes
    ----------
    dir_path : str
        top level subject raw data directory
    bids_path : str
        bids directory to convert raw data to
    prep_path : str
        output directory for processed data
    subj_id : str
        ursi of participant run based on dir_path
    site : str
        expected format of raw data (NL or UTD)
    bids_complete : list
        list of sessions that have been previously ran and marks
        to skip conversion and preprocessing
    seqs : dict
        anat, task and dwi keys paired with raw image paths
    """

    def __init__(self, dir_path, bids_path, prep_path):
        self.dir_path = dir_path
        if self.dir_path.endswith('/'):
            self.dir_path = self.dir_path[:-1]

        self.bids_path = bids_path
        if self.bids_path.endswith('/'):
            self.bids_path = self.bids_path[:-1]

        self.prep_path = prep_path
        if self.prep_path.endswith('/'):
            self.prep_path = self.prep_path[:-1]

        # Determine if NL or UTD data
        self.subj_id = re.sub(".*/", '', self.dir_path)
        if self.subj_id.startswith("sub"):
            self.site = 'NL'
        else:
            self.site = 'UTD'
            self.subj_id = 'sub-' + self.subj_id

        # Determine sessions that have already been converted
        self.bids_complete = []
        for ses in glob.glob(f'{self.bids_path}/{self.subj_id}/*'):
            if "ses-01" in ses:
                self.bids_complete.append("ses-01")
            elif "ses-02" in ses:
                self.bids_complete.append("ses-02")

        self.seqs = {'anat': [], 'func': [], 'dwi': [], 'fmap': []}

    def _seq_glob(self, seq, topup):
        """
        Arguments
        ---------
        seq_name : str
            name of sequence to match
        topup : bool
            is seq a field map

        Returns
        -------
        seq_match : list of strings
            globbed paths to raw images
        """
        if self.site == 'UTD':
            pattern = f'{self.dir_path}/*/*{seq}*/*'
        elif self.site == 'NL':
            pattern = f'{self.dir_path}/*/*{seq}*.PAR'

        if self.site == 'UTD' and not topup:
            seq_match = [img for img in glob.glob(pattern) if "TOP_UP" not in
                         img]
        elif self.site == 'UTD' and topup:
            seq_match = [img for img in glob.glob(pattern) if "TOP_UP" in img]
        elif self.site == "NL" and not topup:
            seq_match = [img for img in glob.glob(pattern) if "topup" not in
                         img]
        elif self.site == "NL" and topup:
            seq_match = [img for img in glob.glob(pattern) if "topup" in img]

        seq_match.sort()

        try:
            seq_match = seq_match[0]
        except IndexError:
            if topup:
                warnings.warn(f"Missing \"{seq}\" fmap for {self.subj_id}.")
            else:
                warnings.warn(f"Missing \"{seq}\" image for {self.subj_id}.")

        return seq_match

    def to_nii(self):
        """ Converts all raw sequences to nifti.
        """
        if self.site == 'UTD':
            # Get T1w and diffusions sequences
            self.seqs['anat'] = self._seq_glob('MPR', topup=False)
            self.seqs['dwi'] = self._seq_glob('DTI', topup=False)

            # Get all funcational sequences
            seq_match = ['CAAT', 'CUE_RUN1', 'CUE_RUN2', 'NBACK', 'REST']
            self.seqs['func'] = [self._seq_glob(seq, topup=False) for seq in
                                 seq_match]

            # Get all topup sequences
            seq_match.append('DTI')
            self.seqs['fmap'] = [self._seq_glob(seq, topup=True) for seq in
                                 seq_match]
        elif self.site == 'NL':
            self.seqs['anat'] = self._seq_glob('T1w', topup=False)
            self.seqs['dwi'] = self._seq_glob('dwi', topup=False)
            seq_match = ['CAAT', 'cue*run-1', 'cue*run-2', 'nback', 'rest']
            self.seqs['func'] = [self._seq_glob(seq, topup=False) for seq in
                                 seq_match]
            seq_match.append('dwi')
            self.seqs['fmap'] = [self._seq_glob(seq, topup=True) for seq in
                                 seq_match]

        # Skip conversion if pre-existing BIDS directory exists.
        if os.path.isdir(self.dir_path + '/' + self.subj_id):
            warnings.warn(f"BIDS directory for {self.subj_id} exists.\n"
                          f"Skipping dicom to nifti conversion")
            return

        # Expression to search that specifies session
        if self.site == 'UTD':
            sess_regex = glob.glob(f'{self.dir_path}/*')
            dates = [int(re.sub("at.*", "", re.sub(".*Study", "", sess))) for
                     sess in sess_regex]
            # Session paths keys and date pairs, sorted by date
            sess_regex = dict(zip(sess_regex, dates))
            sess_regex = {k: v for k, v in sorted(sess_regex.items(),
                          key=lambda x: x[1], reverse=True)}
            sess_regex = list(sess_regex.values())
        elif self.site == 'NL':
            sess_regex = ['ses-01', 'ses-02']
        # Make subject-level BIDS directory
        base_out = f'{self.bids_path}/{self.subj_id}'
        if not os.path.isdir(base_out):
            os.mkdir(base_out)

        # Select correct conversion binary
        pwd = os.path.dirname(__file__)
        if self.site == 'NL':
            dcm2niix = f'{pwd}/dcm2niix/dcm2niix_NL'
        else:
            dcm2niix = f'{pwd}/dcm2niix/dcm2niix'

        func_seqs = ['CAAT', 'CUE-RUN-01', 'CUE-RUN-02', 'NBACK', 'REST']
        for session in ['ses-01', 'ses-02']:
            if session not in self.bids_complete:
                # Setup BIDS sub-directories
                sess_out = f'{base_out}/{session}'
                os.mkdir(sess_out)
                os.mkdir(f'{sess_out}/anat')
                os.mkdir(f'{sess_out}/func')
                os.mkdir(f'{sess_out}/dwi')
                os.mkdir(f'{sess_out}/fmap')

                # Create dcm2niix commands in list of strings
                for img_type in self.seqs.keys():
                    if session == 'ses-01':
                        images = [seq for seq in self.seqs[img_type] if
                                  str(sess_regex[0]) in seq]
                    elif session == 'ses-02':
                        images = [seq for seq in self.seqs[img_type] if
                                  str(sess_regex[1]) in seq]
                    if img_type == 'anat':
                        cmd = [f'{dcm2niix} -o {sess_out}/anat -f '
                               f'{self.subj_id}_ses-01_T1w {img}' for img in images]
                    elif img_type == 'func':
                        cmd = [f'{dcm2niix} -o {sess_out}/func -f '
                               f'{self.subj_id}_ses-01_task-{func_seqs[idx]}_bold '
                               f'{img}' for idx, img in enumerate(images)]
                    elif img_type == 'dwi':
                        cmd = [f'{dcm2niix} -o {sess_out}/dwi -f '
                               f'{self.subj_id}_ses-01_dwi {img}' for img in images]
                    elif img_type == 'fmap':
                        cmd = [f'{dcm2niix} -o {sess_out}/func -f '
                               f'{self.subj_id}_ses-01_task-{func_seqs[idx]}_epi '
                               f'{img}' for idx, img in enumerate(images)]

                    # Exexcute conversion commands
                    for conv in cmd:
                        subprocess.run(conv, shell=True)
