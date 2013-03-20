###################################################################################
#
# PingKicker
# Plugin for B3 (www.bigbrotherbot.com)
# www.1stsop.nl (mailto:Walker@1stsop.nl)
#
# This program is free software and licensed under the terms of
# the GNU General Public License (GPL), version 2.
#
# http://www.gnu.org/copyleft/gpl.html
###################################################################################

PingKicker (v1.0.1) for B3
###################################################################################

This plugin can replace the default PingWatch plugin delivered with B3. You should
only use this plugin if you would like to kick players with a ping you think is too
high.

If a player's ping is too high, he will get a few private messages 
telling what is going on and that he can be kicked because of it.

After that, if his ping is still too high, he will be kicked and a public message
will be shown to explain why he was kicked.

Configurable (in the plugin_pingkicker.xml):
- the max ping that is allowed
- the interval of ping checking
- the max duration, before a pinger will get kicked
- the level, players of this level and lower will be kicked (when their ping is too high)
- the first, reminder and public message that will be sent.

Requirements:
###################################################################################

- B3 version 1.1.0 or higher


Installation:
###################################################################################

1. Place the pingkicker.py in your ../b3/extplugins and the 
plugin_pingkicker.xml in your ../b3/extplugins/conf folders.

2. Open the .xml file with your favorite editor and modify the
settings to your wishes.

3. Open your B3.xml file (default in b3/conf) and add the next line in the
<plugins> section of the file:

<plugin name="pingkicker" priority="5" config="@b3/extplugins/conf/plugin_pingkicker.xml"/>

Remember, it is not necessary to use this plugin and de default pingwatch plugin.
If you enable this pingkicker, you should disable the pingwatch.

Changelog
###################################################################################
v1.0.1         : - Moved the messages to the messages section in the config
                 - Use self.getMessage
                 - Use self.config.time
v1.0.0         : Initial creation

###################################################################################
Walker - 2 jan 2006 - www.bigbrotherbot.com // www.1stSoP.nl