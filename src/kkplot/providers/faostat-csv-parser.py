
import sys
import pandas
import datetime
import numpy

pandas_version = pandas.__version__.split( '.')
pandas_version_major = int( pandas_version[0])
pandas_version_minor = int( pandas_version[1])


def date_parser( _year) :

    t = '0:0'
    return  numpy.array([ datetime.datetime.strptime( '%s-7-1 %s' % ( y, t), '%Y-%m-%d %H:%M') for y in _year if not pandas.isnull( y) ] )


def parse( _outfile, _infile) :

    if pandas_version_minor < 15 :
        df_infile = pandas.read_table( _infile, index_col=False, sep=",", skipfooter=2, header=0, parse_dates={ 'datetime':[ 'Year']}, date_parser=date_parser, engine='python')
    else :
        df_infile = pandas.read_table( _infile, index_col=False, sep=",", skipfooter=2, header=0, skip_blank_lines=False, parse_dates={ 'datetime':[ 'Year']}, date_parser=date_parser, engine='python')

    df_infile.insert( 0, 'julianday', pandas.DatetimeIndex( df_infile['datetime']).dayofyear)
    df_infile.insert( 0, 'year', pandas.DatetimeIndex( df_infile['datetime']).year)
    ## add dummy ID
    df_infile.insert( 0, 'id', 0)

    df_infile.drop( 'datetime', axis=1, inplace=True)

    df_infile.to_csv( _outfile, header=True, na_rep='-99.99', sep='\t', index=False)
    
    return 0


import os
if __name__ == '__main__' :

    if len( sys.argv) < 3 :
        sys.stderr.write( 'usage: faostat-csv-parser.py <infile> <outfile> [--no-dir-prefix]\n')
        sys.exit( 1)

    no_prepend_dirprefix = False
    if len( sys.argv) > 3 :
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

    rc = parse( outfile, infile)
    sys.exit( rc)


