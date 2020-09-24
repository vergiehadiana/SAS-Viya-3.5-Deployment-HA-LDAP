#!/bin/bash

if [ "$#" != 1 ]; then
   script="$(basename "$0")"
   echo "Usage: $script <userid>" >&2
   exit 1
fi

userid="$1"

ent=$(getent passwd "$userid")
if [ -z "$ent" ]; then
    echo "Userid not found: $userid" >&2
    exit 2
fi

login_shell=$(cut -d: -f7 <<< "$ent")
if [ -z "$login_shell" ]; then
   echo "Login shell not found for user: $userid" >&2
   exit 2
fi

nologin_shells=("/bin/false" "/sbin/nologin")
for (( i = 0; i < ${#nologin_shells[@]}; i++ )) {
   if [ "${nologin_shells[i]}" == "$login_shell" ]; then
      rc=4
      in_passwd="not in /etc/passwd"
      if grep -q "^$userid:" /etc/passwd; then
         rc=3
         in_passwd="in /etc/passwd"
      fi
      echo "User $userid, $in_passwd, cannot login with current shell: $login_shell" >&2
      exit $rc
   fi
}
