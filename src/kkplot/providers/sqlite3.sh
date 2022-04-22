
sqlite_bin="sqlite3"
providerdir="`dirname $0`"

tmpdir="${KKPLOT_TMPDIR:-.}"
datadir="${KKPLOT_DATADIR:-.}"

output="$tmpdir/$1"
db_list=( `echo "$2" | tr ';' ' '` )
header="$3"
sqlquery="$4"


#dryrun='echo '

loadmathfunctions=''
if [ -r "$providerdir/libsqlitefunctions.so" ]
then
    loadmathfunctions=".load $providerdir/libsqlitefunctions.so"
fi

function get_header
{
    hdr=( $header )
    if [[ "$header" =~ ^\ *\*\ * ]]
    then
       tbl=`printf "%s" "$sqlquery" | egrep -o 'from\ +[a-zA-Z0-9_]+' | cut -d ' ' -f2`
       hdr=( `$sqlite_bin "$db" "pragma table_info($tbl);" | cut -d '|' -f2` )
    fi
    echo -n ${hdr[@]}
}

function dbquery
{
    sep=""
    for h in ${header[@]}
    do
        printf '%b%s' "$sep" "$h"
        sep='\t'
    done
    printf '\n'

    for db_j in ${DBs[@]}
    do
        $dryrun $sqlite_bin -cmd "$loadmathfunctions" -separator $'\t' "$datadir/$db_j" "$sqlquery;"
    done
}

maxDBs=100
DBs=( )
for db_j in ${db_list[@]}
do
    if [[ "$db_j" =~ \%0*[0-9]*d ]]
    then
        for k in `seq 0 $maxDBs`
        do
            db_j_k=`printf "$db_j" $k`
            if [ ! -r "$datadir/$db_j_k" ]
            then
                break;
            fi
            DBs+=( "$db_j_k" )
        done
    else
        DBs+=( "$db_j" )
    fi
done

db="$datadir/${DBs[0]}"

#echo -e "dblist=${db_list[@]};\nDBs=${DBs[@]};\ndb=$db;\nhdr=$header;\nquery=$sqlquery;" >&2

header="`get_header "$header"`"
dbquery > "$output"

