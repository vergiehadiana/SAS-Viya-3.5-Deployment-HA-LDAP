
#!/bin/sh
#right now this has to be run on the same machine as the log with the reset link - but if http proxy is on another machine this will need to be updated
set -vx
#export host=$(hostname -f)
export host=sasviya02
export password=lnxsas
SASMAINROOT=${SASMAINROOT:=/opt/sas}
export code=$(ls -tr $SASMAINROOT/viya/config/var/log/saslogon/default/sas-saslogon_* | tail -n1 | grep '.log$' | xargs grep 'sasboot' | cut -d'=' -f2)
# make the first request, this expends the link
curl -k https://$host/SASLogon/reset_password?code=$code -c cookies -o output
# get a few things out of the output to use in the next request
echo $code
export CSRF_TOKEN=`grep 'name="_csrf"' output | cut -f 6 -d '"'`
export NEW_CODE=`grep 'name="code"' output | cut -f 6 -d '"'`
# make the second request with the password and other information
curl -kvb cookies https://$host/SASLogon/reset_password.do -H "Content-Type: application/x-www-form-urlencoded" -d "code=${NEW_CODE}&email=none&password=${password}&password_confirmation=${password}&_csrf=${CSRF_TOKEN}"
echo $?

