import find_files
import os


class Subject:
    # everything about a new subject
    # takes path to subject as argument Ex: newSubject = Subject(NL/sub-1234)
    def __init__(self, path):
        self.path = path
        self.subject_id = 1126
        self.sessions = []
        self.set_sessions()

    def set_subject_id(self):
        # get from path
        # fixMe
        pass

    def set_sessions(self):
        i=0
        for session in os.listdir(self.path):
            print(i)
            i=i+1
            self.sessions.append(Session(self.path + '/' + session))

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
