
output="$KKPLOT_TMPDIR/$1"
shift 1
header="$1"
shift 1
sqlquery="$1"
shift 1

if [[ "$OSTYPE" == "linux-gnu" ]]
then
    tmpfile="`mktemp --tmpdir=.`"
elif [[ "$OSTYPE" == "darwin"* ]]
then
    tmpfile=`mktemp tag-sqlite3.tmp`
fi

inputs="$@"

function inputs_tagconcat
{
    need_header=1
    for input in ${inputs[@]}
    do
        input=(`printf "$input" | tr '@' ' '`)
        fname="${input[0]}"
        tag="${input[1]}"

        if [ $need_header -eq 1 ]
        then
            if [[ "$OSTYPE" == "linux-gnu" ]]
            then
                printf 'tag\t%s\n' "`echo $header | sed 's/\ \+/\t/g'`"
            elif [[ "$OSTYPE" == "darwin"* ]]
            then
                printf 'tag\t%s\n' "`echo $header | gsed 's/\ \+/\t/g'`"
            fi
        fi

## sk:dbg        echo "$fname ($tag)" 1>&2
## sk:dbg        echo -e "\t$header" 1>&2
## sk:dbg        echo -e "\t$sqlquery" 1>&2
## sk:dbg
## sk:dbg        echo -e "\t$KKPLOT_PROVIDERSDIR/sqlite3.sh" 1>&2

        bash "$KKPLOT_PROVIDERSDIR/sqlite3.sh" "$tmpfile" "$fname" "$header" "$sqlquery"
        awk '{if (NR!=1) {print}}' "$KKPLOT_TMPDIR/$tmpfile" | awk "{print \"$tag\\t\" \$0}"

        need_header=0
    done
}

inputs_tagconcat > "$output"

rm "$tmpfile"

