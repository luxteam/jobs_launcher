#!/bin/bash
SKIPPED_CASES_PATH="$1"
ERROR_CASES_PATH="$2"
HOST="$3"
OS="$4"
GPU="$5"

python core/isGroupSkipped.py --path_to_skipped_cases $SKIPPED_CASES_PATH --path_to_error_cases $ERROR_CASES_PATH --host $HOST --os $OS --gpu $GPU
