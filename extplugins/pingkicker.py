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
from inspect import getargspec


class PingInfo:
    _1stPingTime = 0
    _2ndPingTime = 0


class PingkickerPlugin(b3.plugin.Plugin):
    _interval = 0
    _maxPing = 0
    _maxPingDuration = 0
    _max_level = 100
    _ignoreTill = 0
    _cronTab = None
    _clientvar_name = 'ping_info'
    _pings_supported = False
    _filter_ids_supported = False

    def onStartup(self):
        self.registerEvent(b3.events.EVT_GAME_EXIT)

        # dont check pings on startup
        self._ignoreTill = self.console.time() + 90

    def onLoadConfig(self):
        # give a warning if pingwatch plugin is enabled
        if 'pingwatch' in self.console._plugins:
            self.warning('It is not necessary to use this plugin and the pingwatch plugin together.\
            If you enable this pingkicker, you should disable the pingwatch plugin.')

        # check for getPlayerPings support
        self._test_getPlayerPings()
        if not self._pings_supported:
            self.error('plugin disabled!')
            self.disable()
        else:
            self._load_messages()
            self._load_settings()

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
        # check player pings
        check_cids = [client.cid for client in self.console.clients.getClientsByLevel(max=self._max_level)]
        if self.isEnabled() and (self.console.time() > self._ignoreTill) and check_cids:
            if self._filter_ids_supported:
                _player_pings = self.console.getPlayerPings(filter_client_ids=check_cids)
            else:
                _player_pings = self.console.getPlayerPings()
            for cid, ping in _player_pings.items():
                self.debug('ping %s = %s', cid, ping)
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

    def _test_getPlayerPings(self):
        """Check if getPlayerPings available."""
        try:
            self.console.getPlayerPings()
            self.debug('getPlayerPings are supported.')
            self._pings_supported = True
            # check for filter_client_ids - older b3 versions dosnt support it
            if self._pings_supported:
                if 'filter_client_ids' in getargspec(self.console.getPlayerPings).args:
                    self._filter_ids_supported = True
        except NotImplementedError:
            self.error('%s does not support pings or it has not been implemented in B3.' % self.console.game.gameName)

    def _load_settings(self):
        """Load plugin settings."""

        # Interval sets the scheduling time
        try:
            self._interval = self.config.getint('settings', 'interval')
        except NoOptionError:
            self.info('No config option \"settings\\interval\" found. Using default value: %s' % self._interval)
        # allowed max ping
        try:
            self._maxPing = self.config.getint('settings', 'max_ping')
        except NoOptionError:
            self.info('No config option \"settings\\maxping\" found. Using default value: %s' % self._maxPing)
        # ?
        try:
            self._maxPingDuration = self.config.getint('settings', 'max_ping_duration')
        except NoOptionError:
            self.info(
                'No config option \"settings\\maxPingDuration\" found. Using default value: %s' % self._maxPingDuration)
        # Which levels get ping checking. In this case, players with level 1 and lower gets checked
        try:
            self._max_level = self.config.getint('settings', 'max_level_checked')
        except NoOptionError:
            self.info(
                'No config option \"settings\\max_level_checked\" found. Using default value: %s' % self._max_level)

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