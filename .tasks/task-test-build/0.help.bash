#!/usr/bin/env bash
# place in $root/.tasks/task-{name}/0.help.bash
# and chmod +x it.
set -o nounset
set -o pipefail

# shellcheck disable=SC1091
source "$POLY_SRC/lib/lib-util.bash"
[[ -e "$POLYGLOT_ROOT/.tasks/task-util.bash" ]] && source "$POLYGLOT_ROOT/.tasks/task-util.bash"

PRINT_TEXT="
usage: polyglot task build [srcdir] [-h]

Build the sphinx website

positional arguments:
srcdir  : the dir of source .rst and .bib files. default: ws root

options:
-h, --help    : show this help message and exit
-nc | -no-clean   : don't delete existing site files
--conf {conf dir} : the dir for the conf.py
--out  {out dir}  : the subdir of .temp/site to build into
"

maybe-print-help "leaf" 0 "$PRINT_TEXT" "$@"
