#!/bin/sh

PATH=/sbin:/usr/sbin/:/bin:/usr/bin

if [ -x /usr/bin/python3 ]; then
    PYTHON=python3
else
    PYTHON=python
fi

case "${1}" in
    pre)
            # executes before sleeping
            pkill -9 -f <AUTO_REPLACEMENT_WITH_MAIN_PATH>
    ;;
    post|*)
            # executes after resuming
            $PYTHON <AUTO_REPLACEMENT_WITH_MAIN_PATH>
    ;;
esac

exit 0