r"""
Evennia settings file.

The available options are found in the default settings file found
here:

C:\Users\lemca\Documents\muddev\evenv\lib\site-packages\evennia\settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.contrib.base_systems import color_markups
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "Beckoning"
INSTALLED_APPS += ('jobs',)
INSTALLED_APPS += ('bbs',)
INSTALLED_APPS += ('wiki',)

COLOR_ANSI_EXTRA_MAP = color_markups.MUX_COLOR_ANSI_EXTRA_MAP
COLOR_XTERM256_EXTRA_FG = color_markups.MUX_COLOR_XTERM256_EXTRA_FG
COLOR_XTERM256_EXTRA_BG = color_markups.MUX_COLOR_XTERM256_EXTRA_BG
COLOR_XTERM256_EXTRA_GFG = color_markups.MUX_COLOR_XTERM256_EXTRA_GFG
COLOR_XTERM256_EXTRA_GBG = color_markups.MUX_COLOR_XTERM256_EXTRA_GBG
COLOR_ANSI_XTERM256_BRIGHT_BG_EXTRA_MAP = color_markups.MUX_COLOR_ANSI_XTERM256_BRIGHT_BG_EXTRA_MAP

TELNET_PORTS = [6666]
CLIENT_DEFAULT_WIDTH = 80

# Optional channel (same form as CHANNEL_MUDINFO) that will receive connection
# messages like ("<account> has (dis)connected"). While the MudInfo channel
# will also receieve this info, this channel is meant for non-staffers. If
# None, this information will only be logged.
CHANNEL_CONNECTINFO = {
    "key": "ConnInfo",
    "aliases": "",
    "desc": "Player Connect/Disconnect Log",
    "locks": "control:perm(Developer);listen:true();send:false()",
}

OPTIONS_ACCOUNT_DEFAULT = {
    "border_color": ("Headers, footers, table borders, etc.", "Color", "R"),
    "header_star_color": ("* inside Header lines.", "Color", "n"),
    "header_text_color": ("Text inside Header lines.", "Color", "w"),
    "header_fill": ("Fill for Header lines.", "Text", "="),
    "separator_star_color": ("* inside Separator lines.", "Color", "n"),
    "separator_text_color": ("Text inside Separator lines.", "Color", "w"),
    "separator_fill": ("Fill for Separator Lines.", "Text", "-"),
    "footer_star_color": ("* inside Footer lines.", "Color", "n"),
    "footer_text_color": ("Text inside Footer Lines.", "Color", "n"),
    "footer_fill": ("Fill for Footer Lines.", "Text", "="),
    "column_names_color": ("Table column header text.", "Color", "w"),
    "timezone": ("Timezone for dates.", "Timezone", "UTC"),
}

# Parent class for all default commands. Changing this class will
# modify all default commands, so do so carefully.
COMMAND_DEFAULT_CLASS = "commands.command.Command"

# Different Multisession modes allow a player (=account) to connect to the
# game simultaneously with multiple clients (=sessions).
#  0 - single session per account (if reconnecting, disconnect old session)
#  1 - multiple sessions per account, all sessions share output
#  2 - multiple sessions per account, one session allowed per puppet
#  3 - multiple sessions per account, multiple sessions per puppet (share output)
#      session getting the same data.
MULTISESSION_MODE = 3

# The maximum number of characters allowed by be created by the default ooc
# char-creation command. This can be seen as how big of a 'stable' of characters
# an account can have (not how many you can puppet at the same time). Set to
# None for no limit.
MAX_NR_CHARACTERS = 10

# How many *different* characters an account can puppet *at the same time*. A value
# above 1 only makes a difference together with MULTISESSION_MODE > 1.
MAX_NR_SIMULTANEOUS_PUPPETS = 3


# Disable the default autocreate account logic because we implement our own custom logic for this
AUTO_CREATE_CHARACTER_WITH_ACCOUNT = False

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
