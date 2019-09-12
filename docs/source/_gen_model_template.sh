#!/usr/bin/env bash

cd $(dirname $0)
echo "Generating template model file..."

cd user_guide/
framat example -f
