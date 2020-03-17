#!/usr/bin/env python3

from mjxproc.utils import Subject
import os.path as op
import shutil
import pytest


@pytest.mark.parametrize("site", ['UTD', 'NL'])
def test_to_nii(site):
    base_dir = '/mnt/Filbey/common/Studies/MJXProcessing/MJXProcessing'
    base_dir = f'{base_dir}/tests/examples'

    if site == 'UTD':
        ursi = 'M75005160'
        subj = Subject(f'{base_dir}/UTD/{ursi}', f'{base_dir}/BIDS_test',
                       f'{base_dir}/PROC')
    elif site == 'NL':
        ursi = '1126'
        subj = Subject(f'{base_dir}/NL/sub-{ursi}', f'{base_dir}/BIDS_test',
                       f'{base_dir}/PROC')

    subj.to_nii()

    for ftype in ['nii', 'json']:
        assert op.isfile(f'{base_dir}/BIDS_test/sub-{ursi}/ses-01/anat/'
                         f'sub-{ursi}_ses-01_T1w.{ftype}')

    for task in ['CAAT', 'CUE-RUN-01', 'CUE-RUN-02', 'NBACK', 'REST']:
        for type in ['func', 'fmap']:
            if type == 'func':
                assert op.isfile(f'{base_dir}/BIDS_test/sub-{ursi}/ses-01/'
                                 f'{type}/sub-{ursi}_ses-01_task-{task}_bold.nii')
            elif type == 'fmap':
                assert op.isfile(f'{base_dir}/BIDS_test/sub-{ursi}/ses-01/'
                                 f'{type}/sub-{ursi}_ses-01_acq-{task}_epi.nii')

    for ftype in ['nii', 'json']:
        assert op.isfile(f'{base_dir}/BIDS_test/sub-{ursi}/ses-01/dwi/'
                         f'sub-{ursi}_ses-01_dwi.{ftype}')

    shutil.rmtree(f'{base_dir}/BIDS_test')
