
LDNDC_PROJECTSDIR="$HOME/projects"
ldndccatclimate_bin="ldndc-cat-climate"

timearg="$1"
inputarg="$2" #$LDNDC_PROJECTSDIR/$2"
idlistarg="$3"
outputarg="$KKPLOT_TMPDIR/$4"

$ldndccatclimate_bin "$timearg" "$inputarg" "$idlistarg" "$outputarg"

