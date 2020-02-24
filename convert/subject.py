#!/usr/bin/env python3

import find_files
import os
import re
import glob


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
    subject_id : str
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
        self.subject_id = re.sub(".*/", '', self.dir_path)
        if self.subject_id.startswith("sub"):
            self.site = 'NL'
        else:
            self.site = 'UTD'
            self.subject_id = 'sub-' + self.subject_id

        # Skip sessions that have already been converted
        self.bids_complete = []
        for ses in glob.glob(self.bids_path + '/*'):
            if "ses-01" in ses:
                self.bids_complete.append("ses-01")
            elif "ses-02" in ses:
                self.bids_complete.append("ses-02")

        self.seqs = {'anat': [], 'func': [], 'dwi': [], 'fmap': []}

    def func_seq_match(self, seq, topup):
        """
        Arguments
        ---------
        seq_name : str
            name of sequence to match
        topup : bool
            is seq a field map
        """
        if self.site == 'UTD':
            pattern = self.dir_path + "/*/*" + seq + "*"
        elif self.site == 'NL':
            pattern = self.dir_path + "/*/*" + seq + "*.PAR"

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

    def get_seqs(self):
        if self.site == 'UTD':
            self.seqs['anat'] = glob.glob(self.dir_path + "/*/*MPR*/*")[0]
            try:
                rest = [img for img in glob.glob(dir_path + "/*/*BOLD_REST*")
                        if "TOP_UP" not in img][0]
            except IndexError:
                print(self.subj_id + ' missing task-rest.')



            self.seqs['func'].append()
            self.seqs['fmap'] = [glob.glob(i + "/*")[0] for i in
                                 glob.glob(self.dir_path + "/*/*TOP_UP*")]

    def to_bids(self, outPath):
        #os.mkdir(outPath + "/" + self.subject_id)
        os.makedirs("%s/%s" % (outPath, self.subject_id))
        for session in self.sessions:
            os.makedirs("%s/%s/%s" % (outPath, self.subject_id, session))
            os.makedirs("%s/%s/%s/%s" % (outPath, self.subject_id, session, "anat"))
            os.makedirs("%s/%s/%s/%s" % (outPath, self.subject_id, session, "dwi"))
            os.makedirs("%s/%s/%s/%s" % (outPath, self.subject_id, session, "fmap"))
            os.makedirs("%s/%s/%s/%s" % (outPath, self.subject_id, session, "func"))




class Session:
    def __init__(self, path):
        self.path = path
        self.anat_files = []
        self.dwi_files = []
        self.fmap_files = []
        self.func_files = []
        self.setNL()

    def setNL(self):
        # creates list of files eligible for use in different BIDS folders
        self.anat_files = find_files.findT1(self.path)
        self.dwi_files = find_files.findDwi(self.path)
        self.fmap_files = find_files.findFmap(self.path)
        self.func_files = find_files.findTask(self.path)
