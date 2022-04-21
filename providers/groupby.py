
import sys
import pandas
import datetime
import numpy

pandas_version = pandas.__version__.split( '.')
pandas_version_major = int( pandas_version[0])
pandas_version_minor = int( pandas_version[1])

def parse( _outfile, _infile, _groups, _method) :
    df_infile = pandas.read_table( _infile, comment='#')
    if _method == 'mean' :
        df_infile = df_infile.groupby(groups).mean().reset_index()
    elif _method == 'std' :
        df_infile = df_infile.groupby(groups).std().reset_index()
    df_infile.to_csv( _outfile, header=True, na_rep='-99.99', sep='\t', index=False)
    
    return 0

import os
if __name__ == '__main__' :

    if len( sys.argv) < 5 :
        sys.stderr.write( 'usage: groupby.py <infile> <outfile> <groups> <method> [--no-dir-prefix]\n')
        sys.exit( 1)

    no_prepend_dirprefix = False
    if len( sys.argv) > 5 :
        if sys.argv[3] == '--no-dir-prefix' :
            no_prepend_dirprefix = True

    ## output file
    outdir_prefix = None
    if not no_prepend_dirprefix :
        outdir_prefix = os.getenv( 'KKPLOT_TMPDIR')
    outfile = sys.argv[1].strip()
    if len( outfile) == 0 :
        sys.exit( 2)
    outfile = outfile.replace( '\\', '/')
    if not os.path.isabs( outfile) and outdir_prefix is not None :
        outfile = '%s/%s' % ( outdir_prefix, outfile)

    ## input file
    indir_prefix = None
    if not no_prepend_dirprefix :
        indir_prefix = os.getenv( 'KKPLOT_MEASUREMENTSDIR')
    infile = sys.argv[2].strip()

    if len( infile) == 0 :
        sys.exit( 2)
    infile = infile.replace( '\\', '/')
    if not os.path.isabs( infile) and indir_prefix is not None :
        infile = '%s/%s' % ( indir_prefix, infile)

    if os.path.normpath( infile) == os.path.normpath( outfile) :
        sys.stderr.write( 'output file points to input file; refusing to trash input file :(\n')
        sys.exit( 3)

    #groups
    groups = []
    for arg in  sys.argv[3].split(',') :
        groups.append(arg.strip())

    #methods
    method = sys.argv[4].strip()

    rc = parse( outfile, infile, groups, method)
    sys.exit( rc)


