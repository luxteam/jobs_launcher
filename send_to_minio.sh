#!/bin/bash
PATH="$1"
PATTERN="$2"

python core/isGroupSkipped.py --path $PATH --pattern $PATTERN