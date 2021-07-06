#! /bin/zsh

#
# Script to automate version bumping + deployment to main/master branch
#


BRANCH_DEV=dev
BRANCH_MAIN=main

#
# Get user input.
#

read -r '?Deploy major/minor/PATCH/skip: ' type

if [[ $type == '' ]]; then
    type='patch'
fi

if [[ $type != 'major' && $type != 'minor' && $type != 'patch' && $type != 'skip' ]]; then
    echo "Unrecognized option: ${type}"
    exit 1
fi

#
# Extract version numbers.
#

version=$(cat VERSION)
parts=(${(s/./)version})
major=$parts[1]
minor=$parts[2]
patch=$parts[3]

echo "Current version: $major.$minor.$patch"

if [[ $type == 'major' ]]; then
    major=$((major + 1))
    minor='0'
    patch='0'
fi

if [[ $type == 'minor' ]]; then
    minor=$((minor + 1))
    patch='0'
fi

if [[ $type == 'patch' ]]; then
    patch=$((patch + 1))
fi

if [[ $type != 'skip' ]]; then
    new_version="$major.$minor.$patch"
    echo "New version: $new_version"
fi


#
# Update dev + merge into main
#

echo ------------------------------------------------------------

git checkout $BRANCH_DEV || exit 1
git pull || exit 1

if [[ $type != 'skip' ]]; then
    echo "$new_version" > VERSION
    git add VERSION || exit 1 
    git commit -m "Bump version number to $new_version" || exit 1
fi

git push || exit 1 

git checkout $BRANCH_MAIN || exit 1
git pull || exit 1
git merge $BRANCH_DEV || exit 1
git push || exit 1
