
import os
import sys
import pandas as pd

if __name__ == '__main__':
    df = pd.read_csv(sys.argv[1], comment="#", sep="\t")

    if 'datetime' in df:
        df['datetime'] = pd.to_datetime(df['datetime'])
    elif 'date' in df:
        df['datetime'] = pd.to_datetime(df['date'])
        df.drop(columns=['date'], inplace=True)

    for a in sys.argv:
        if 'column' in a:
            arguments = {'function': '', 'column': '', 'values': ''}
            for i in a.split(';'):
                k, v = i.split(':', 1)
                arguments[k.strip()] = v.strip()

            values = [i.strip() for i in arguments['values'].split(',')]

            for val in values:
                if '~' in val:
                    df = df.loc[df[arguments['column']].astype(str) != val.replace('~', ''), ]
                else:
                    df = df.loc[df[arguments['column']].astype(str) == val, ]

            try:
                group_cols = ['datetime', arguments['column']]
                if arguments['function'] == 'mean':
                    df = df.groupby(group_cols).mean(numeric_only=True)
                elif arguments['function'] == 'std':
                    df = df.groupby(group_cols).std(numeric_only=True)
                elif arguments['function'] == 'sum':
                    df = df.groupby(['datetime']).sum(numeric_only=True)
                elif arguments['function'] == 'filter':
                    pass
            #for older python versions not knowing 'numeric_only'
            except:
                if arguments['function'] == 'mean':
                    df = df.groupby(group_cols).mean()
                elif arguments['function'] == 'std':
                    df = df.groupby(group_cols).std()
                elif arguments['function'] == 'sum':
                    df = df.groupby(['datetime']).sum()
                elif arguments['function'] == 'filter':
                    pass

    out_path = os.getenv( 'KKPLOT_TMPDIR') + "/" + sys.argv[2]

    df.to_csv(out_path, sep="\t")

