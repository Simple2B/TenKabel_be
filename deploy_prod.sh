#!/bin/bash

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" != "main" ]; then
  TARGET_BRANCH="main"
  git checkout $TARGET_BRANCH
fi

git pull origin $TARGET_BRANCH  # Ensure you have the latest changes from the target branch
git merge develop  # Merge changes from develop into the target branch (main)
git add .
git commit -m "Merge changes from develop into $TARGET_BRANCH"
git push origin $TARGET_BRANCH  # Push the merged changes to the target branch