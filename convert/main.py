from convert.Subject import Subject
out_path = "/home/evan/Filbey/Evan/BIDS"

test_subject = Subject("/home/evan/Filbey/common/Studies/MJXProcessing/examples/NL/sub-1126", out_path, "/home/evan/Filbey/Evan")

#convert dicom to nifti
test_subject.get_seqs()
test_subject.to_bids(out_path)




