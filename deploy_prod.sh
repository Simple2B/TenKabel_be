#!/bin/bash

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" != "main" ]; then
  git checkout main
fi
git merge develop
git add .
git commit -m "Update changes"
git push origin main
