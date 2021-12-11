#!/usr/bin/python3

import argparse
import json
import logging
import os
import signal
import subprocess
import sys

import gi

from menu.menu import Panel

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, GLib

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def configure_fetch_interval(config_path: str, fetch_interval: int):
    """
    Updates the fetch interval in the config JSON file.

    :param config_path: the path of the JSON config file
    :type config_path: str
    :param fetch_interval: the time in seconds specifying the reloading interval of the menu items
    :type fetch_interval: int
    """
    with open(config_path, 'r') as config:
        data = json.loads(config.read())

    data["fetch_interval"] = fetch_interval

    with open(config_path, 'w', encoding='utf-8') as config:
        json.dump(data, config, ensure_ascii=False, indent=4)


def configure_default_devices(config_path: str, default: str, secondary: str):
    """
    Updates the default and secondary device IDs in the JSON config file.

    :param config_path: the path of the JSON config file
    :type config_path: str
    :param default: the ID (e.g. 3C:4D:BE:1B:38:E4) of a default bluetooth device, False if not set.
    :type default: str
    :param secondary: the ID (e.g. 3C:4D:BE:1B:38:E4) of a secondary bluetooth device, False if not set.
    :type secondary: str
    """
    with open(config_path, 'r') as config:
        data = json.loads(config.read())

    if default is not False:
        data["default"] = default
    if secondary is not False:
        data["secondary"] = secondary

    with open(config_path, 'w', encoding='utf-8') as config:
        json.dump(data, config, ensure_ascii=False, indent=4)


def disable_enable_autostart(disable_autostart: bool, working_dir: str):
    """
    Disables or enables autostart (enabled by default).

    :param disable_autostart: True if autostart flag is set, else False.
    :type disable_autostart: bool
    :param working_dir: the absolute path of the file which is under execution (main.py).
    :type working_dir: str
    """
    copy_into_autostart_path = working_dir + '/config/copy_into_autostart.sh'
    remove_from_autostart_path = working_dir + '/config/remove_from_autostart.sh'

    if disable_autostart:
        subprocess.call(['sh', copy_into_autostart_path])
    else:
        subprocess.call(['sh', remove_from_autostart_path])


def configure_autostart(exec_command: str, working_dir: str):
    """
    Adds the autostart execution line to the .desktop file in the config directory.

    :param exec_command: the execution string (path to program)
    :type exec_command: str
    :param working_dir: the absolute path of the file which is under execution (main.py).
    :type working_dir: str
    """
    desktop_file_path = working_dir + '/config/ubuntu-bluetooth-menu.desktop'
    if not os.path.exists(desktop_file_path):
        logger.error("\nPlease add the ubuntu-bluetooth-menu.desktop to the config directory.\n")
        raise FileNotFoundError('config/ubuntu-bluetooth-menu.desktop')

    exists = False
    with open(desktop_file_path, 'r') as f:
        if exec_command in f.read():
            exists = True

    if not exists:
        with open(desktop_file_path, 'a') as f:
            f.write(exec_command)


def disable_enable_system_sleep(disable_autostart: bool, working_dir: str):
    """
    Disables or enables system sleep (based on whether the autostart flag is enabled/disabled)

    :param disable_autostart: True if autostart flag is set, else False.
    :type disable_autostart: bool
    :param working_dir: the absolute path of the file which is under execution (main.py).
    :type working_dir: str
    """
    copy_into_system_sleep = working_dir + '/config/configure_system_sleep.sh'
    remove_from_system_sleep = working_dir + '/config/remove_from_system_sleep.sh'

    if disable_autostart:
        subprocess.call(['sh', copy_into_system_sleep])
    else:
        subprocess.call(['sh', remove_from_system_sleep])


def configure_system_sleep(main_path: str, working_dir: str):
    """
    Configures sleep script which will be placed into "/lib/systemd/system-sleep/ubuntu-menu-bluetooth-sleep.sh"

    :param main_path: the path of the ubuntu-bluetooth-menu main.py
    :type main_path: str
    :param working_dir: the absolute path of the file which is under execution (main.py).
    :type working_dir: str
    """
    sleep_file_path = working_dir + '/config/ubuntu-bluetooth-menu-sleep.sh'
    if not os.path.exists(sleep_file_path):
        logger.error("\nPlease add the ubuntu-bluetooth-menu-sleep.sh to the config directory.\n")
        raise FileNotFoundError('config/ubuntu-bluetooth-menu-sleep.sh')

    with open(sleep_file_path, 'r') as f:
        replaced_text = f.read().replace('<AUTO_REPLACEMENT_WITH_MAIN_PATH>', main_path)

    with open(sleep_file_path, 'w') as f:
        f.write(replaced_text)


def main():
    parser = argparse.ArgumentParser(usage="%(prog)s [options]")

    parser.add_argument("--config", "-c",
                        action="store_true",
                        default=False,
                        help="Enter configuration mode"
                        )
    parser.add_argument("--default", "-d",
                        type=str,
                        action="store",
                        default=False,
                        help="Configure default device ID"
                        )
    parser.add_argument("--secondary", "-s",
                        type=str,
                        action="store",
                        default=False,
                        help="Configure secondary device ID"
                        )
    parser.add_argument("--disable-autostart", "-na",
                        action="store_false",
                        default=True,
                        help="Program gets automatically added to the Ubuntu autostart folder by default."
                        )
    parser.add_argument("--fetch-interval", "-f",
                        type=int,
                        action="store",
                        default=10,
                        help="Program gets automatically added to the Ubuntu autostart folder by default."
                        )

    args = parser.parse_args()
    config = args.config
    default = args.default
    secondary = args.secondary
    disable_autostart = args.disable_autostart
    fetch_interval = args.fetch_interval

    # set path variables
    working_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = working_dir + '/config/config.json'
    icon_path = working_dir + '/images/bluetooth.svg'
    main_path = working_dir + '/main.py'
    exec_command = '\nExec=python3 ' + main_path + '\n'

    # configure autostart
    configure_autostart(exec_command, working_dir)
    disable_enable_autostart(disable_autostart, working_dir)

    # configure system sleep / wakeup
    configure_system_sleep(main_path, working_dir)

    # set default and/or secondary device and store in json
    if config:
        if hasattr(args, 'fetch_interval'):
            configure_fetch_interval(config_path, fetch_interval)

        if hasattr(args, 'default') or hasattr(args, 'secondary'):
            configure_default_devices(config_path, default, secondary)

        disable_enable_system_sleep(disable_autostart, working_dir)

        sys.exit()

    # get fetch interval
    if not hasattr(args, 'fetch_interval'):
        with open(config_path, 'r') as config:
            data = json.load(config)
            fetch_interval = data['fetch_interval']

    # create Menu panel
    panel = Panel(icon_path)

    # define fetch interval in milliseconds
    fetch_interval_milliseconds = fetch_interval * 1000

    GLib.timeout_add(fetch_interval_milliseconds, panel.build_panel)
    Gtk.main()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
