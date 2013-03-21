#
# BigBrotherBot(B3) (www.bigbrotherbot.com)
# Copyright (C) 2006 Walker 
# Walker@1stsop.nl
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# CHANGELOG
#       01/02/2006 - 1.0.1 - Walker
#       - Use self.getMessage() to get messages. 
#       - changed time.time() to self.console.time()
#       - Don't send messages when ping = 999
#	12/28/2005 - 1.0.0 - Walker
#	Copied Thorn's PingWatch plugin and added kick functionality


__author__ = 'Walker'
__version__ = '1.0.1'

import b3
import thread
import b3.events
import b3.plugin
import b3.cron
from ConfigParser import NoOptionError


class PingInfo:
    _1stPingTime = 0
    _2ndPingTime = 0


class PingkickerPlugin(b3.plugin.Plugin):
    _interval = 0
    _maxPing = 0
    _maxPingDuration = 0
    _max_level = 1
    _ignoreTill = 0
    _cronTab = None
    _clientvar_name = 'ping_info'

    def onStartup(self):
        self.registerEvent(b3.events.EVT_GAME_EXIT)

        # dont check pings on startup
        self._ignoreTill = self.console.time() + 90

    def onLoadConfig(self):
        self._load_messages()
        self._interval = self.config.getint('settings', 'interval')
        self._maxPing = self.config.getint('settings', 'max_ping')
        self._maxPingDuration = self.config.getint('settings', 'max_ping_duration')
        self._max_level = self.config.getint('settings', 'max_level_checked')

        if self._cronTab:
            # remove existing crontab
            self.console.cron - self._cronTab

        self._cronTab = b3.cron.PluginCronTab(self, self.check, '*/%s' % self._interval)
        self.console.cron + self._cronTab

    def onEvent(self, event):
        if event.type == b3.events.EVT_GAME_EXIT:
            # ignore ping watching for 1 minutes
            self._ignoreTill = self.console.time() + 90

    def get_ping_info(self, client):
    # get the PingInfo stats

        if not client.isvar(self, self._clientvar_name):
        # initialize the default PingInfo object
            client.setvar(self, self._clientvar_name, PingInfo())

        return client.var(self, self._clientvar_name).value

    def check(self):
        #self.console.verbose('Ping check started')
        if self.isEnabled() and (self.console.time() > self._ignoreTill):
            #self.console.verbose('Ping check enabled')
            for cid, ping in self.console.getPlayerPings().items():
                #self.console.verbose('ping %s = %s', cid, ping)
                if ping > self._maxPing:
                    client = self.console.clients.getByCID(cid)
                    if client and client.maxLevel <= self._max_level:
                        pingInfo = self.get_ping_info(client)

                        #self.console.verbose('%s time=(%s) 1stPingTime = %s, 2ndPingTime = %s', client.name, self.console.time(), pingInfo._1stPingTime, pingInfo._2ndPingTime )

                        if pingInfo._1stPingTime > 0:
                            if self.console.time() - pingInfo._1stPingTime >= self._maxPingDuration and self.console.time() - pingInfo._2ndPingTime < (self._interval + 3):
                                # Max ping duration has gone by and he hasn't missed a ping interval. Kicking time!
                                client.kick(self.getMessage('public_ping_kick_message', {'ping': ping}))
                            elif self.console.time() - pingInfo._2ndPingTime > (self._interval + 3):
                                # There is a gap between ping measures, maybe it was a ping spike. Reset counters
                                pingInfo._1stPingTime = self.console.time()
                                pingInfo._2ndPingTime = self.console.time()
                                if ping != 999:
                                    client.message(self.getMessage('first_ping_warning'))
                            else:
                                # Ping is still too high, but not longer than max ping duration.
                                pingInfo._2ndPingTime = self.console.time()
                                if ping != 999:
                                    client.message(self.getMessage('reminder_ping_warning'))
                        else:
                            # Ping is too high, this is the first time.
                            pingInfo._1stPingTime = self.console.time()
                            pingInfo._2ndPingTime = self.console.time()
                            if ping != 999:
                                client.message(self.getMessage('first_ping_warning'))

    def _load_messages(self):
        """Load plugin messages."""
        # first warning message
        try:
            self.getMessage('first_ping_warning')
        except NoOptionError:
            self._messages['first_ping_warning'] = "Your ping is too high. If you can, try to reduce it!."
        # remind user message
        try:
            self.getMessage('reminder_ping_warning')
        except NoOptionError:
            self._messages['reminder_ping_warning'] = "Your ping is still too high. You will get kicked automatically.\
            Nothing personal!"
        # public kick message
        try:
            self.getMessage('public_ping_kick_message', {'ping': ''})
        except NoOptionError:
            self._messages['public_ping_kick_message'] = "because his ping was too high for this server %(ping)s."