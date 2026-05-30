#!/bin/bash
EXCLUDE="/cygdrive/c/pysawitweb/exclusions"
LOCAL="/cygdrive/c/pysawitweb/"
DEST="cbsteh@ssh.pythonanywhere.com:/home/cbsteh/pysawitweb/"
FLAGS="-avzhne"
SIM="Testing only"

echo "(1) Office or (2) HP computer? Enter 1 or 2 (suffix with '999' for NOT a dry run):"
read ans

if (("${ans:0:1}" == 2)); then
    EXCLUDE="/cygdrive/d/pysawitweb/exclusions"
    LOCAL="/cygdrive/d/pysawitweb/"
fi

if ((${#ans} == 4)); then
    if (("${ans:1:4}" == 999)); then
        FLAGS="-avzhe"
        SIM="Here we go!"
    fi
fi

# shellcheck disable=SC2027
echo "You chose: "${ans:0:1}" ($SIM). Syncing now ..."
rsync $FLAGS ssh -i -c --exclude-from=$EXCLUDE $LOCAL $DEST | grep '^<' | awk '{ print $2 }'
echo "... done#"
