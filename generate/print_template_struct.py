from path import path


for file in path('templates').walk():
    path_depth = len(str(file).split('/'))
    print "".join("    " for _ in xrange(path_depth - 2)), file.basename()
