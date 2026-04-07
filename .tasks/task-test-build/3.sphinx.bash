#!/usr/bin/env bash
#set -o errexit
set -o nounset
set -o pipefail

# shellcheck disable=SC1091
source "$POLY_SRC/lib/lib-util.bash"
[[ -e "$POLYGLOT_ROOT/.tasks/task-util.bash" ]] && source "$POLYGLOT_ROOT/.tasks/task-util.bash"


# builder="${POLYGLOT_SPHINX_BUILDER:-bibhtml}"
builder="html"
conf="${POLYGLOT_TEST_BUILD_DIR:-$POLYGLOT_ROOT}"
src="${conf}"
out="${POLYGLOT_TEMP}"
site_out="$out/site"

while [[ $# -gt 0 ]]; do
    case $1 in
        --conf)
            shift
            echo "Conf: $1"
            conf=$(realpath "$1")
            ;;
        --out)
            shift
            echo "Out: $1"
            site_out=$(realpath "$site_out/$1")
            ;;
        *) # Positional
            echo "Src: $1"
            src=$(realpath "$1")
            ;;
    esac
    shift
done


subhead "Building:\n- (conf:$conf)\n- (src:$src)\n->(out:$site_out)"
    # --verbose \
    # --write-all \
    # --fresh-env \
(uv run sphinx-build \
    --write-all \
    --fresh-env \
    --conf-dir "$conf" \
    --doctree-dir "$out/doctrees" \
    --warning-file "$conf/.temp/logs/sphinx.log" \
    --builder "$builder" \
    "$src" "$site_out"
 )
