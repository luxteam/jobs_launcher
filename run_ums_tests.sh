#!/bin/bash
# export variabels *** default values for easy manual testing
export UMS_URL_TEST=${1:-'https://umsapi2.cistest.luxoft.com'}
export UMS_JOB_ID_TEST=${2:-'5f881e5a8e8872f31dc413e3'}
export UMS_ENV_LABEL=${3:-'Windows-AMD'}
export UMS_LOGIN_TEST=${4:-'dm1tryG'}
export UMS_PASSWORD_TEST=${5:-'root'}
export UMS_BUILD_ID_TEST=${6:-'6007fd00cf43c198e4d3e298'}

# print configuration
echo "Test cases configuration."
echo "$UMS_URL_TEST"
echo "$UMS_JOB_ID_TEST"
echo "$UMS_ENV_LABEL"
echo "$UMS_LOGIN_TEST"
echo "$UMS_PASSWORD_TEST"
echo "$UMS_BUILD_ID_TEST"

# run tests
# TODO: optimize to version or use virtual env in jobs launcher
python3.6 -m pytest tests/ums.py
