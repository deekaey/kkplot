#!/bin/bash

export KKPLOT_DATADIR="${1:-}"
echo "using data directory '$KKPLOT_DATADIR'  [KKPLOT_DATADIR]" 1>&2
export KKPLOT_MEASUREMENTSDIR="${2:-}"
echo "using measurements directory '$KKPLOT_MEASUREMENTSDIR'  [KKPLOT_MEASUREMENTSDIR]" 1>&2


engines=( "pythonpandas" "gnuplot" )
declare -A enginesuffixmap=( ["pythonpandas"]='py' ["gnuplot"]='gnuplot' )

testsdir=tests
mkdir -p $testsdir

testinputs=( examples/config.yml )

export PYTHONDONTWRITEBYTECODE=1

for testinput in ${testinputs[@]}
do
    for engine in ${engines[@]}
    do

        printf "engine '%s'\n" $engine
        python -B  kkplot.py --debug --engine $engine $testinput > $testsdir/${engine}.${enginesuffixmap[$engine]}
    done

done

