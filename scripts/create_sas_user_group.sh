#!/bin/sh

getent group sas >/dev/null || groupadd -f -g 1001 -r sas
if ! getent passwd sas >/dev/null ; then
    if ! getent passwd 1001 >/dev/null ; then
      useradd -r -u 1001 -g sas -d /opt/sas/viya/home -s /sbin/nologin -c "SAS User account" sas
    else
      useradd -r -g sas -d /opt/sas/viya/home -s /sbin/nologin -c "SAS User account" sas
    fi
fi
exit 0