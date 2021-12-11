script=$(readlink -f "$0")
path=$(dirname "$script")
mkdir -p /lib/systemd/system-sleep/
echo "\nAdding file to system sleep directory requires privileged access:"
sudo cp $path/ubuntu-bluetooth-menu-sleep.sh /lib/systemd/system-sleep/
sudo chmod +x /lib/systemd/system-sleep/ubuntu-bluetooth-menu-sleep.sh