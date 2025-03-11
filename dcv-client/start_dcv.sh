#!/bin/bash

# Workaround for the Shift_L+Alt_L is Meta_L issue
xmodmap -e "keycode 64 = Alt_L Alt_L Alt_L Alt_L Alt_L Alt_L"
exec dcvviewer "$@"

