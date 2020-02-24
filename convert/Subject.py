import convert.find_files
import os

class Subject:
    # everything about a new subject
    # takes path to subject as argument Ex: newSubject = Subject(NL/sub-1234)
    def __init__(self, path):
        self.path = path
        self.subject_id
        self.sessions = []

    def set_subject_id(self):
        pass
    def set_sessions(self):
        for session in os.listdir(self.path):
            self.sessions.append(Session(self.path + '/' + session))



class Session(Subject):
    def __init__(self, path):
        self.path = path
        self.anat_files = []
        self.dwi_files = []
        self.fmap_files = []
        self.func_files = []

    def setNL(self):
        # creates list of files eligible for use in different BIDS folders
        self.anat_files = convert.find_files.findT1(self.path)
        self.dwi_files = convert.find_files.findDwi(self.path)
        self.fmap_files = convert.find_files.findFmap(self.path)
        self.func_files = convert.find_files.findTask(self.path)
