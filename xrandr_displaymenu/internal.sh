#!/bin/bash
xrandr --noprimary --output VGA1 --off --output HDMI1 --off --output DP1 --off --output eDP1 --mode 1920x1080 --pos 0x0 --rotate normal
sed -i 's/.*monitor=.*/  monitor=0/' ~/.config/lxpanel/LXDE/panels/panel
