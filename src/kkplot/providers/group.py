

import os
import sys
import pandas
import datetime
import numpy
import pandas as pd

if __name__ == '__main__' :

    df = pd.read_csv( sys.argv[1], comment="#", sep="\t")
    df.datetime = pd.to_datetime(df.datetime)

    for a in sys.argv:
        if 'column' in a:
            arguments = { 'function': '', 'column': '', 'values':''}
            for i in a.split(';'):
                k,v = i.split(':')[0].strip(), i.split(':')[1].strip()
                arguments.update( {k:v} )

            values = arguments['values'].split(',')
            values = [i.strip() for i in values]

            #df = df.loc[df[arguments['column']].isin(values),]
            df = df.loc[df[arguments['column']].astype(str).isin(values),]
            try:
                if arguments['function'] == 'mean':
                    df = df.groupby(['datetime', arguments['column']]).mean( numeric_only=True)
                elif arguments['function'] == 'std':
                    df = df.groupby(['datetime', arguments['column']]).std( numeric_only=True)
                elif arguments['function'] == 'sum':
                    df = df.groupby(['datetime']).sum( numeric_only=True)
                elif arguments['function'] == 'filter':
                    pass
            #for older python versions not knowing 'numeric_only'
            except:
                if arguments['function'] == 'mean':
                    df = df.groupby(['datetime', arguments['column']]).mean()
                elif arguments['function'] == 'std':
                    df = df.groupby(['datetime', arguments['column']]).std()
                elif arguments['function'] == 'sum':
                    df = df.groupby(['datetime']).sum()
                elif arguments['function'] == 'filter':
                    pass

    out_path = os.getenv( 'KKPLOT_TMPDIR') + "/" + sys.argv[2]

    df.to_csv(out_path, sep="\t")

