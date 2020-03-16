

dg = DataGrabber(infields=['sid'], outfields=['func', 'struct', 'ref'])
dg.inputs.base_directory = '.'
dg.inputs.template = '%s/%s.nii'
dg.inputs.template_args['func'] = [['sid', ['f3', 'f5']]]
dg.inputs.template_args['struct'] = [['sid', ['struct']]]
dg.inputs.template_args['ref'] = [['sid', 'ref']]
dg.inputs.sid = 's1'
