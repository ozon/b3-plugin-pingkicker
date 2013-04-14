# -*- encoding: utf-8 -*-

# add extplugins to the Python sys.path
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../extplugins'))

from unittest import TestCase
from mock import Mock
from mockito import when
from b3.fake import FakeConsole, FakeClient
from b3.config import XmlConfigParser, CfgConfigParser
from pingkicker import PingkickerPlugin


class PingkickerPluginTest(TestCase):

    def tearDown(self):
        if hasattr(self, "parser"):
            del self.parser.clients
            self.parser.working = False

    def setUp(self):
        # create a B3 FakeConsole
        self.parser_conf = XmlConfigParser()
        self.parser_conf.loadFromString(r"""<configuration/>""")
        self.console = FakeConsole(self.parser_conf)

        # create our plugin instance
        self.plugin_conf = CfgConfigParser()
        self.p = PingkickerPlugin(self.console, self.plugin_conf)

        # initialise the plugin
        self.plugin_conf.loadFromString(r'''
[settings]
interval: 3
max_ping: 100
max_ping_duration: 5
max_level_checked: 100
        ''')
        when(self.p)._test_getPlayerPings().thenReturn(True)
        self.p._pings_supported = True

        # prevent the plugin from registering its crontab
        self.p._register_crontab = lambda: None

        self.p.onLoadConfig()
        self.p.onStartup()

        # prepare a few players
        self.joe = FakeClient(self.console, name="Joe", exactName="Joe", guid="zaerezarezar", groupBits=1)
        self.simon = FakeClient(self.console, name="Simon", exactName="Simon", guid="qsdfdsqfdsqf", groupBits=0)
        self.admin = FakeClient(self.console, name="Level-40-Admin", exactName="Level-40-Admin", guid="875sasda", groupBits=16,)
        self.superadmin = FakeClient(self.console, name="God", exactName="God", guid="f4qfer654r", groupBits=128)

        # make sure the plugin won't ignore checks because it just started
        self.p._ignoreTill = 0

    def test_warnings(self):
        # GIVEN
        self.joe.connects('joe')
        self.simon.connects('simon')
        # simon have a highping - 666ms
        when(self.console).getPlayerPings().thenReturn({
            self.joe.cid: 10,
            self.simon.cid: 666,
        })

        # WHEN first ping check
        #clear message history
        self.joe.message_history = []
        self.simon.message_history = []
        self.p.check()

        # THEN
        self.assertListEqual([], self.joe.message_history)
        self.assertListEqual([self.p._messages['first_ping_warning']], self.simon.message_history)

        # WHEN second ping check
        self.joe.message_history = []
        self.simon.message_history = []
        self.p.check()

        # THEN
        self.assertListEqual([], self.joe.message_history)
        self.assertListEqual([self.p._messages['reminder_ping_warning']], self.simon.message_history)

    def test_kick(self):
        """
        make sure that a player having a too high ping on 3 successive checks gets kicked.
        """
        # GIVEN
        T0 = 1000  # the time at which we start the test.
        self.joe.kick = Mock()
        self.joe.connects('joe')
        # joe have a highping
        when(self.console).getPlayerPings().thenReturn({
            self.joe.cid: 666,
        })

        # WHEN
        # 1st check
        when(self.console).time().thenReturn(T0)
        self.p.check()

        # 2nd check
        when(self.console).time().thenReturn(T0 + (self.p._interval * 1))
        self.p.check()

        # 3rd check
        when(self.console).time().thenReturn(T0 + (self.p._interval * 2))
        self.p.check()

        # THEN assert that joe got kicked for high ping
        self.joe.kick.assert_called_with(self.p.getMessage('public_ping_kick_message', {'ping': '666'})
)