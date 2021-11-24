script=$(readlink -f "$0")
path=$(dirname "$script")
mkdir -p ~/.config/autostart
cp $path/ubuntu-bluetooth-menu.desktop ~/.config/autostart/