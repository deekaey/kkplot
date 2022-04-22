
output="$KKPLOT_TMPDIR/$1"

shift 1
inputs="$@"

function inputs_tagconcat
{
    need_header=1
    for input in ${inputs[@]}
    do
        input="$KKPLOT_DATADIR/$input"
        input=(`printf "$input" | tr '@' ' '`)
        fname="${input[0]}"
        tag="${input[1]}"

        if [ $need_header -eq 1 ]
        then
            printf 'tag\t%s\n' "`head -n1 "$fname"`"
        fi
        #echo "$fname ($tag)" 1>&2
        awk '{if (NR!=1) {print}}' "$fname" | awk "{print \"$tag\\t\" \$0}"
        need_header=0
    done
}

inputs_tagconcat > "$output"
