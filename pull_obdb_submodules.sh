#!/usr/bin/env bash
set -eo pipefail

ORG="OBDb"
DEST_DIR="obdb-src"

mkdir -p "$DEST_DIR"

special_repo() {
    case "$1" in
        .github|.meta|.vehicle-template|.make-template)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

repo_has_signalsets() {
    local repo="$1"
    gh api "repos/${ORG}/${repo}/contents/signalsets" >/dev/null 2>&1
}

submodule_exists() {
    local path="$1"
    git config --file .gitmodules --get-regexp '^submodule\..*\.path$' 2>/dev/null | awk '{print $2}' | grep -Fx "$path" >/dev/null 2>&1
}

while IFS= read -r repo; do
    [ -n "$repo" ] || continue

    if special_repo "$repo"; then
        echo "skip special repo: $repo"
        continue
    fi

    path="${DEST_DIR}/${repo}"
    url="https://github.com/${ORG}/${repo}.git"

    if submodule_exists "$path"; then
        echo "already submodule: $repo"
        continue
    fi

    if ! repo_has_signalsets "$repo"; then
        echo "skip without signalsets/: $repo"
        continue
    fi

    if [ -e "$path" ]; then
        echo "path exists and is not registered as submodule: $path"
        continue
    fi

    echo "add submodule: $repo"
    git submodule add --depth 1 "$url" "$path"
done < <(gh repo list "$ORG" --limit 1000 --json name -q '.[].name')

echo "Sync modules"
git submodule sync --recursive
git submodule update --init --recursive --depth 1
