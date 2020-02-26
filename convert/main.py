from Subject import Subject
out_path = "/home/evan/Filbey/Evan/BIDS"

test_subject = Subject("/home/evan/Filbey/common/Studies/MJXProcessing/examples/NL/sub-1126")

test_subject.to_bids(out_path)

