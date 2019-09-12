#!/usr/bin/env bash

cd $(dirname $0)
echo "Generating help page"

framat -h > user_guide/_help_page.txt

# Help pages for modes
framat run -h > user_guide/_help_page_run.txt
framat example -h > user_guide/_help_page_example.txt
