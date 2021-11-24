# ubuntu-bluetooth-menu

![GitHub last commit](https://img.shields.io/github/last-commit/thomasgruebl/ubuntu-bluetooth-menu?style=plastic) ![GitHub](https://img.shields.io/github/license/thomasgruebl/phone-scraper?style=plastic) <a style="text-decoration: none" href="https://github.com/thomasgruebl/ubuntu-bluetooth-menu/stargazers">
<img src="https://img.shields.io/github/stars/thomasgruebl/ubuntu-bluetooth-menu.svg?style=plastic" alt="Stars">
</a>
<a style="text-decoration: none" href="https://github.com/thomasgruebl/ubuntu-bluetooth-menu/fork">
<img src="https://img.shields.io/github/forks/thomasgruebl/ubuntu-bluetooth-menu.svg?style=plastic" alt="Forks">
</a>
![Github All Releases](https://img.shields.io/github/downloads/thomasgruebl/ubuntu-bluetooth-menu/total.svg?style=plastic)
<a style="text-decoration: none" href="https://github.com/thomasgruebl/ubuntu-bluetooth-menu/issues">
<img src="https://img.shields.io/github/issues/thomasgruebl/ubuntu-bluetooth-menu.svg?style=plastic" alt="Issues">
</a>

<p align=center>
  <img src="images/ubuntu_bluetooth_menu.png"/>
</p>


## Features
- Provides a simple, convenient menu to connect bluetooth devices
- Reduces the pain of connecting bluetooth devices via the standard Ubuntu bluetooth menu
- Provides the option to set a default and a secondary device
- Fetches new devices automatically when they appear (leaves the option to manually specify the --fetch-interval)


## Dependencies
Install by running:
```console
$ sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```

As outlined in the requirements.txt file:
- PyGObject>=3.42.0
- pycairo>=1.20.1
- vext>=0.7.6
- vext.gi>=0.7.4
- PyGObject-stubs>=0.0.2


## Installation

```console
# clone the repo
$ git clone https://github.com/thomasgruebl/ubuntu-bluetooth-menu.git

# navigate into the repo
$ cd ubuntu-bluetooth-menu

# install requirements
$ pip3 install -r requirements.txt
```

```console
# run
$ python3 main.py [options]

# run in background
$ python3 main.py [options] &
```

Note: By default you should run the program once with the config flag to set your default and secondary devices of your choice. If you don't set the --disable-autostart flag, the program will also be added to the ubuntu autostart directory (~/.config/autostart) by default.
Also, when you move the program to a different directory, you need to rerun it once so that the autostart config adapts accordingly.

You can identify your the bluetooth device IDs (of currently connected devices) by running the following command.
```console
$ bluetoothctl devices
```
Use the --default <XX.XX.XX.XX.XX.XX> and/or the --secondary <XX.XX.XX.XX.XX.XX> flag to set the device ID.

## Usage

```console
$ ubuntu-bluetooth-menu --help
usage: ubuntu-bluetooth-menu [options]

optional arguments:
  -h, --help                            Show help information
  -c, --config                          Enter configuration mode
  -d, --default                         [In combincation with --config] Specify device ID of default device (e.g. --default E4:AF:22:11:22:33)
  -s, --secondary                       [In combincation with --config] Specify device ID of secondary device
  -na, --disable-autostart              By default, autostart is enabled. Disable autostart using this flag
  -f, --fetch-interval                  Specify fetch interval for searching for available bluetooth devices and updating the menu
```

## Contributing

1. Fork the repository
2. Create a new feature branch (`git checkout -b my-feature-branch-name`)
3. Commit your new changes (`git commit -m 'commit message' <changed-file>`)
4. Push changes to the branch (`git push origin my-feature-branch-name`)
5. Create a Pull Request

## TODO
- Create Daemon (or systemd service)