#!/bin/sh

if grep -r "</failure>" report/*; then
  exit 1
else
  exit 0
fi
