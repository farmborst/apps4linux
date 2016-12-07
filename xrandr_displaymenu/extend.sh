#!/bin/sh

# fallback for no detected external displays
setnotebook(){
	xrandr --noprimary --output VGA1 --off --output HDMI1 --off --output DP1 --off --output eDP1 --mode 1920x1080 --pos 0x0 --rotate normal
	sed -i 's/.*monitor=.*/  monitor=0/' ~/.config/lxpanel/LXDE/panels/panel
}
# set desired display settings
setdisplay(){
	xrandr --noprimary --output VGA1 --off --output $1 --off --output eDP1 --mode 1920x1080 --pos 0x$2 --rotate normal --output $3 --mode $4 --pos 0x0 --rotate normal
	sed -i 's/.*monitor=.*/  monitor=1/' ~/.config/lxpanel/LXDE/panels/panel
}

# extend by connected display (if one is found) and align at left edge
# caution! if both are connected hdmi is prefered output!
# DP1   = external via VGA 
# HDMI1 = external via HDMI

if (xrandr | grep "DP1 disconnected"); then
	if (xrandr | grep "HDMI1 disconnected"); then
		setnotebook
	else
		disconnected="DP1"
		connected="HDMI1"
		externalres=$(xrandr | awk '/^HDMI1 connected/ {getline;print $1;}')
		externalheight=$(echo $externalres | cut -d x -f 2)
		setdisplay $disconnected $externalheight $connected $externalres
	fi
else
	disconnected="HDMI1"
	connected="DP1"
	externalres=$(xrandr | awk '/^DP1 connected/ {getline;print $1;}')
	externalheight=$(echo $externalres | cut -d x -f 2)
	setdisplay $disconnected $externalheight $connected $externalres
fi
