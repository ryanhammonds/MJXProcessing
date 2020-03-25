#!/usr/bin/env python3
'''
Created on Sun March 10 15:44:46 2020
@author: Ryan Hammonds (ryanhammonds)
'''
import os
import re
import glob
import warnings
import subprocess
import json


class Subject:
    """
    Subject class for setting up BIDS, conversion to nifti and preprocessing.
    ...

    Parameters
    ----------
    dir_path : str
        top level subject raw data directory
    bids_path : str
        bids directory to convert raw data to

    Attributes
    ----------
    dir_path : str
        top level subject raw data directory
    bids_path : str
        bids directory to convert raw data to
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

    def __init__(self, dir_path, bids_path):
        self.dir_path = dir_path
        if self.dir_path.endswith('/'):
            self.dir_path = self.dir_path[:-1]

        self.bids_path = bids_path
        if self.bids_path.endswith('/'):
            self.bids_path = self.bids_path[:-1]

        # Check arguments
        if not os.path.isdir(self.dir_path):
            raise IOError(f'Raw data directory missing: {self.dir_path}')
        if not os.path.isdir(self.bids_path):
            os.mkdir(self.bids_path)

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

        self.raw_sess = len(glob.glob(f'{dir_path}/*'))
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

    def to_bids(self):
        """ Converts all raw sequences to nifti.
        """

        # Skip conversion if pre-existing BIDS directory exists.
        base_out = f"{self.bids_path}/{self.subj_id}"
        if os.path.isdir(base_out):
            warnings.warn(f"BIDS directory for {self.subj_id} exists.\n"
                          f"Skipping dicom to nifti conversion.")
            return
        else:
            os.mkdir(base_out)

        pwd = os.path.dirname(__file__)
        if self.site == 'UTD':
            # Get T1w and diffusions sequences
            self.seqs['anat'] = [self._seq_glob('MPR', topup=False)]
            self.seqs['dwi'] = [self._seq_glob('DTI', topup=False)]
            # Get all funcational sequences
            seq_match = ['CAAT', 'CUE_RUN1', 'CUE_RUN2', 'NBACK', 'REST']
            self.seqs['func'] = [self._seq_glob(seq, topup=False) for seq in
                                 seq_match]
            # Get all topup sequences
            seq_match.append('DTI')
            self.seqs['fmap'] = [self._seq_glob(seq, topup=True) for seq in
                                 seq_match]
            # Expression to search that specifies session
            sess_regex = glob.glob(f'{self.dir_path}/*')
            dates = [int(re.sub("at.*", "", re.sub(".*Study", "", sess))) for
                     sess in sess_regex]
            # Session paths keys and date pairs, sorted by date
            sess_regex = dict(zip(sess_regex, dates))
            sess_regex = {k: v for k, v in sorted(sess_regex.items(),
                                                  key=lambda x: x[1],
                                                  reverse=True)}
            sess_regex = list(sess_regex.values())
            # Which dcm2niix to use
            dcm2niix = f'{pwd}/dcm2niix/dcm2niix'
        elif self.site == 'NL':
            self.seqs['anat'] = [self._seq_glob('T1w', topup=False)]
            self.seqs['dwi'] = [self._seq_glob('dwi', topup=False)]
            seq_match = ['CAAT', 'cue*run-1', 'cue*run-2', 'nback', 'rest']
            self.seqs['func'] = [self._seq_glob(seq, topup=False) for seq in
                                 seq_match]
            seq_match.append('dwi')
            self.seqs['fmap'] = [self._seq_glob(seq, topup=True) for seq in
                                 seq_match]
            sess_regex = ['ses-01', 'ses-02']
            dcm2niix = f'{pwd}/dcm2niix/dcm2niix_NL'

        # Create convert cmd strings and execute
        func_seqs = ['CAAT', 'CUE-RUN-01', 'CUE-RUN-02', 'NBACK', 'REST']
        print('Converting to nifti...')
        for idx, session in enumerate(['ses-01', 'ses-02']):
            if session not in self.bids_complete and idx+1 <= self.raw_sess:
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
                               f'{self.subj_id}_ses-01_T1w {img}' for img in
                               images]
                    elif img_type == 'func':
                        cmd = [f'{dcm2niix} -o {sess_out}/func -f '
                               f'{self.subj_id}_ses-01_task-{func_seqs[idx]}_bold '
                               f'{img}' for idx, img in enumerate(images)]
                    elif img_type == 'dwi':
                        cmd = [f'{dcm2niix} -o {sess_out}/dwi -f '
                               f'{self.subj_id}_ses-01_dwi {img}' for img in
                               images]
                    elif img_type == 'fmap':
                        cmd = []
                        for idx, img in enumerate(images):
                            if 'DTI' not in img and'dwi' not in img:
                                cmd.append(f'{dcm2niix} -o {sess_out}/fmap -f '
                                           f'{self.subj_id}_ses-01_acq-'
                                           f'{func_seqs[idx]}_dir-AP_epi {img}')
                            else:
                                cmd.append(f'{dcm2niix} -o {sess_out}/fmap -f '
                                           f'{self.subj_id}_ses-01_acq-dwi_'
                                           f'dir-AP_epi {img}')

                    # Execute conversion commands
                    for conv in cmd:
                        output = subprocess.run(conv, shell=True,
                                                stdout=subprocess.DEVNULL,
                                                stderr=subprocess.DEVNULL)
                        output.check_returncode()

                        # Edit fmap jsons to pair with image
                        if img_type == 'fmap':
                            # file name and dir path from cmd
                            f_out = re.sub(" .*", '', re.sub(".*-f ", '', conv))
                            d_out = re.sub(" .*", '', re.sub(".*-o ", '', conv))

                            img_regex = re.sub("_.*", '', re.sub(".*acq-", '',
                                                                 f_out))
                            img_match = glob.glob(f'{self.bids_path}/'
                                                  f'{self.subj_id}/'
                                                  f'{session}/*/'
                                                  f'*{img_regex}*.nii*')
                            img_match = [img for img in img_match if 'fmap'
                                         not in img][0]

                            # Load img json into dictionary
                            with open(f"{d_out}/{f_out}.json", 'r') as f:
                                img_json = json.load(f)

                            # Clear prexisting key, if one exists
                            if 'IntendedFor' in list(img_json.keys()):
                                del img_json['IntendedFor']

                            # Write
                            img_json['IntendedFor'] = img_match.split('/')[-1]
                            with open(f'{d_out}/{f_out}.json', 'w') as f:
                                json.dump(img_json, f, indent='\t')

        print('Conversion complete')


def bids_query(bids_dir, subj_id, ses):
    """Find nifti images in a BIDS structure.
    Arguments
    ---------
    bids_dir : str
        path to bids directory
    subj_id : str
        subject id
    ses : str
        session number

    Returns
    -------
    anat : list
        list of anatomical images
    func : list
        list of functional images
    dwi : list
        list of diffusion images
    fmap : list
        list of field map images
    """
    base_dir = f'{bids_dir}/{subj_id}/{ses}'
    anat = glob.glob(f'{base_dir}/anat/*nii*')
    anat.sort()
    func = glob.glob(f'{base_dir}/func/*nii*')
    func.sort()
    dwi = glob.glob(f'{base_dir}/dwi/*nii*')
    dwi.sort()
    fmap = glob.glob(f'{base_dir}/fmap/*nii*')
    fmap.sort()

    # Warn if image not found
    if len(anat) > 1:
        warnings.warn("Multiple anat images found.")
    if len(dwi) > 1:
        warnings.warn("Multiple dwi images found.")

    def _check_seqs(seqs, images, type):
        for seq in func_seqs:
            miss_warn = True
            multi_warn = False
            for img in func:
                if seq in img:
                    miss_warn = False
                if not multi_warn and not miss_warn:
                    multi_warn = True

            if miss_warn:
                warnings.warn(f"No {type} image found for {seq}.")
            elif multi_warn:
                warnings.warn(f"Multiple {type} images found for {seq}")

    func_seqs = ['CAAT', 'CUE-RUN-01', 'CUE-RUN-02', 'NBACK', 'REST']
    _check_seqs(func_seqs, func, 'func')
    fmap_seqs = ['CAAT', 'CUE-RUN-01', 'CUE-RUN-02', 'NBACK', 'REST', 'dwi']
    _check_seqs(fmap_seqs, fmap, 'fmap')

    return anat, func, dwi, fmap