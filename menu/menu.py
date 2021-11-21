import json
import logging
import os
import re
import subprocess
import webbrowser
from collections import defaultdict
from typing import List

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk
from gi.repository import AppIndicator3
from gi.repository import Notify
from gi.repository.Gtk import MenuItem
from gi.repository.Gtk import Menu
from gi.repository.Gtk import SeparatorMenuItem
from gi.repository.Gtk import Window
from gi.repository.Gtk import Button, Box, Label
from gi.repository.Gtk import Orientation, Justification


ID = 'bluetooth_menu'

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


class AboutWindow(Window):
    def __init__(self):
        super().__init__(title="The (better) Ubuntu Bluetooth Menu")
        self.github_button = Button(label="Find more information on Github")
        self.label2 = Label()
        self.label = Label(label="Ubuntu Bluetooth Menu")
        self.vbox_right = Box(orientation=Orientation.VERTICAL, spacing=10)
        self.vbox_left = Box(orientation=Orientation.VERTICAL, spacing=10)
        self.box = Box(spacing=10)

    def fill_window(self):
        self.vbox_left.set_homogeneous(False)
        self.vbox_right.set_homogeneous(False)

        self.box.pack_start(self.vbox_left, True, True, 0)
        self.box.pack_start(self.vbox_right, True, True, 0)

        self.label.set_margin_left(50)
        self.vbox_left.pack_start(self.label, True, True, 20)

        self.label2.set_text("Product Version 1.0.0\n"
                             "Created by github.com/thomasgruebl\n"
                             "License MIT")
        self.label2.set_justify(Justification.LEFT)
        self.vbox_left.pack_start(self.label2, True, True, 0)

        self.github_button.connect("clicked", self.open_github)
        self.github_button.set_margin_left(45)
        self.github_button.set_margin_bottom(20)
        self.vbox_left.pack_start(self.github_button, True, True, 0)

        self.add(self.box)

    @staticmethod
    def open_github(_):
        webbrowser.open('https://github.com/thomasgruebl/ubuntu-bluetooth-menu')


class Component:
    def __init__(self, label, method, gtk_menu):
        self.label = label
        self.method = method
        self.gtk_menu = gtk_menu

    def connect(self):
        item = MenuItem()
        item = item.new_with_label(label=self.label)
        item.connect('activate', self.method)
        self.gtk_menu.append(item)
        return item


class Panel:

    def __init__(self, icon_path):
        self.available_devices = list()
        self.lookup_device_id = defaultdict(str)
        self.gtk_menu = Menu()
        self.indicator = AppIndicator3.Indicator.new(ID, icon_path,
                                                     AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_panel())
        Notify.init(ID)

        working_dir = os.path.dirname(os.path.realpath(__file__))
        self.config_path = working_dir + '/config/config.json'
        self.config_path = self.config_path.replace("/menu", "")

    def update_menu(self):
        self.gtk_menu.foreach(lambda child: child.destroy())

    def fetch_devices(self):
        logger.debug("Fetching devices and rebuilding menu...")
        available_devices = self.list_available_devices()
        self.available_devices = self.extract_device_name(available_devices)

        for device in self.available_devices:
            connect_device = Component(device.group(2), self.connect_available, self.gtk_menu)
            menu_item = connect_device.connect()
            self.lookup_device_id[menu_item] = device.group(1)

    def build_panel(self):
        self.update_menu()

        bluetooth_on = Component("Bluetooth ON", self.activate_bluetooth, self.gtk_menu)
        bluetooth_off = Component("Bluetooth OFF", self.deactivate_bluetooth, self.gtk_menu)
        bluetooth_on.connect()
        bluetooth_off.connect()

        seperator0 = SeparatorMenuItem()
        self.gtk_menu.append(seperator0)

        connect_default = Component("Connect default device", self.connect_default, self.gtk_menu)
        connect_secondary = Component("Connect secondary device", self.connect_secondary, self.gtk_menu)
        connect_default.connect()
        connect_secondary.connect()

        seperator1 = SeparatorMenuItem()
        self.gtk_menu.append(seperator1)

        disconnect_current = Component("Disconnect current device", self.disconnect_current_device, self.gtk_menu)
        disconnect_current.connect()

        seperator2 = SeparatorMenuItem()
        self.gtk_menu.append(seperator2)

        # fetches and adds devices to panel on first and every subsequent run (to keep device list up-to-date)
        self.fetch_devices()

        seperator3 = SeparatorMenuItem()
        self.gtk_menu.append(seperator3)

        about = Component("About", self.about, self.gtk_menu)
        about.connect()

        seperator4 = SeparatorMenuItem()
        self.gtk_menu.append(seperator4)

        quit = Component("Quit", self.quit, self.gtk_menu)
        quit.connect()

        self.gtk_menu.show_all()

        return self.gtk_menu

    @staticmethod
    def activate_bluetooth(_):
        connect = subprocess.Popen(["bluetooth", "on"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = connect.communicate()
        logger.debug(f"{stdout}, {stderr}")

    @staticmethod
    def deactivate_bluetooth(_):
        connect = subprocess.Popen(["bluetooth", "off"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = connect.communicate()
        logger.debug(f"{stdout}, {stderr}")

    @staticmethod
    def connect_device(device_id: str) -> List[bytes]:
        connect = subprocess.Popen(["bluetoothctl", "connect", device_id],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = connect.communicate()
        return [stdout, stderr]

    def connect_default(self, menu_item: Gtk.MenuItem):
        with open(self.config_path, 'r') as config:
            data = json.load(config)
            default_device_id = data['default']

        stdout, stderr = self.connect_device(default_device_id)
        logger.debug(f"{stdout}, {stderr}")

    def connect_secondary(self, menu_item: Gtk.MenuItem):
        with open(self.config_path, 'r') as config:
            data = json.load(config)
            secondary_device_id = data['secondary']

        stdout, stderr = self.connect_device(secondary_device_id)
        logger.debug(f"{stdout}, {stderr}")

    def connect_available(self, menu_item: Gtk.MenuItem):
        stdout, stderr = self.connect_device(self.lookup_device_id[menu_item])
        logger.debug(f"{stdout}, {stderr}")

    @staticmethod
    def disconnect_current_device(_):
        disconnect_current = subprocess.Popen(["bluetoothctl", "disconnect"],
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = disconnect_current.communicate()
        logger.debug(f"{stdout}, {stderr}")

    @staticmethod
    def extract_device_name(available_devices: List[str]):
        return [re.search('([0-9A-F]{2}(?::[0-9A-F]{2}){5})(.*)',
                          str(device)) for device in available_devices]

    @staticmethod
    def list_available_devices():
        list_available_devices = subprocess.Popen(["bluetoothctl", "devices"],
                                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = list_available_devices.communicate()
        logger.debug(f"{stdout}, {stderr}")
        stdout = stdout.decode('UTF-8').splitlines()
        stderr = stderr.decode('UTF-8').splitlines()
        return stdout

    @staticmethod
    def about(_):
        window = AboutWindow()
        window.fill_window()
        window.show_all()

    @staticmethod
    def quit(_):
        Notify.uninit()
        Gtk.main_quit()
