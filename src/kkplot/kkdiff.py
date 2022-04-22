
## kkdiff wraps kkgen.py --diff calls, e.g.,
##  python kkgen.py --diff --range '1996-01-01->2012-01-01' --title 'Debug vs Release' --columns dC_ch4_emis: --names="wet:dry" soilchemistry-daily-wet.txt soilchemistry-daily-dry.txt | kkplot -
## 
##
##  python kkdiff.py --range '1996-01-01->2012-01-01' --title 'Debug vs Release' --columns dC_ch4_emis: soilchemistry-daily-wet.txt soilchemistry-daily-dry.txt | kkplot -

import sys
import kkutils as utils
import kkgen as gen

if __name__ == '__main__':

    sys.argv.append( '--diff')

    rc = gen.main()
    sys.exit( rc)

