#!/usr/bin/env bash
# Prints the current user's name and local time as one line of JSON.
# Only uses tools that ship with macOS/Linux and git. Nothing to install.
name="$(git config user.name 2>/dev/null)"
username="$(id -un 2>/dev/null || echo "$USER")"
hour=$((10#$(date +%H)))
if   [ "$hour" -lt 12 ]; then part="morning"
elif [ "$hour" -lt 18 ]; then part="afternoon"
else                          part="evening"
fi
printf '{"name":"%s","username":"%s","os":"%s","local_time":"%s","part_of_day":"%s"}\n' \
  "$name" "$username" "$(uname -s)" "$(date +%H:%M)" "$part"
