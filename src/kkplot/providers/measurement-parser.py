
import sys
import pandas
import datetime
import numpy

pandas_version = pandas.__version__.split( '.')
pandas_version_major = int( pandas_version[0])
pandas_version_minor = int( pandas_version[1])


def mp_makeyear( _df) :

    d = _df['date'].astype( str)
    y = pandas.Series( [ ymd[0:4] for ymd in d], d.index)
    return  y

def mp_makedatetime( _df) :

    d = _df['date'].astype( str)
    if 'time' in _df.columns :
        t = _df['time'].astype( str)
        t[t=='nan'] = '12:00'
        return d + 'T' + t
    return  d

def mp_parse( _outfile, _infile) :

    skiprows = mp_getskiprows( _infile)
    if skiprows < 0 :
        return  -1

    if pandas_version_minor < 15 :
        df_infile = pandas.read_table( _infile, index_col=False, header=0, skiprows=skiprows, na_values=['-99.99','na','nan'])
    else :
        df_infile = pandas.read_table( _infile, index_col=False, header=skiprows, skip_blank_lines=False, na_values=['-99.99','na','nan'])

    ## we require 'date' column
    if ('date' not in df_infile.columns) and ('datetime' not in df_infile.columns) :
        sys.stderr.write( '"date/datetime" column missing measurement file\n')
        return  -1

    ## add dummy ID
    df_infile.insert( 0, 'id', 0)
    if 'datetime' not in df_infile.columns:
        df_infile.insert( 0, 'year', mp_makeyear( df_infile))
        df_infile.insert( 0, 'datetime', mp_makedatetime( df_infile))
    if 'date' in df_infile.columns :
        df_infile.drop( [ 'date'], axis=1, inplace=True)
    if 'time' in df_infile.columns :
        df_infile.drop( [ 'time'], axis=1, inplace=True)

    df_infile.to_csv( _outfile, header=True, na_rep='-99.99', sep='\t', index=False)
    return 0

def mp_getskiprows( _infile) :
    f = open( _infile, 'r')
    if not f :
        return -1
    line_count = 0
    for line in f :
        line_count += 1
        words = line.split()
        if len( words) > 0 :
            if '%data' in words[0] :
                f.close()
                if len( words) > 1 :
                    sys.stderr.write( '%%data line contains garbage [%s]\n' % ( ' '.join( words[1:])))
                    return -1
                return  line_count
    f.close()
    return 0


import os
if __name__ == '__main__' :

    if len( sys.argv) < 3 :
        sys.stderr.write( 'usage: measurement-parser.py <infile> <outfile> [--no-dir-prefix]\n')
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

    rc = mp_parse( outfile, infile)
    sys.exit( rc)

