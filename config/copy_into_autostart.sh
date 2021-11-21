script=$(readlink -f "$0")
path=$(dirname "$script")
cp $path/ubuntu-bluetooth-menu.desktop ~/.config/autostart/