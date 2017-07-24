#!/usr/bin/env python3
import os
import signal
import subprocess
from collections import defaultdict
from Xlib import X, display
from Xlib.ext import randr

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

APPINDICATOR_ID = 'scree-resolution'

resolutions = defaultdict(bool)

def main():
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath('icon.svg'), appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    notify.init(APPINDICATOR_ID)
    gtk.main()

def build_menu():
    d = display.Display()
    s = d.screen()
    screen_res = s.root.get_geometry()
    current_resolution = (screen_res.width, screen_res.height)
    window = s.root.create_window(0, 0, 1, 1, 1, s.root_depth)
    res = randr.get_screen_resources(window)
    for mode in res.modes:
        w, h = mode.width, mode.height
        if abs(1 - (w / h) / (16 / 9)) < 0.01 and w >= 1360:
            resolutions[(w, h)] = current_resolution == (w, h)

    menu = gtk.Menu()
    for res in sorted(resolutions):
        res_button = gtk.MenuItem('%d x %d' % res)
        res_button.connect('activate', set_resoltuion, res, window)
        menu.append(res_button)

    button_quit = gtk.MenuItem('Quit')
    button_quit.connect('activate', quit)
    menu.append(button_quit)
    menu.show_all()
    return menu

def set_resoltuion(_, resolution, window):
    # TODO: Check how to use this function correctly
    # randr.set_screen_size(window, 1600, 900)
    subprocess.call(['xrandr', '-s', '%dx%d' % resolution])
    notify.Notification.new("<b>Screen resolution changed</b>", '%d x %d' % resolution).show()

def quit(_):
    notify.uninit()
    gtk.main_quit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()