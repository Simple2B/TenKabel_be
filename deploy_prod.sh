#!/bin/bash

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" != "main" ]; thens
  git checkout main
fi

git pull origin main

git add .
git commit -m "Update changes"
git push origin main
