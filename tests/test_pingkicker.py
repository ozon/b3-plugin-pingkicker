# -*- encoding: utf-8 -*-

# add extplugins to the Python sys.path
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../extplugins'))

from unittest import TestCase
from mock import patch, call, Mock
from mockito import when, verify
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

        self.p.onLoadConfig()
        self.p.onStartup()

        # prepare a few players
        self.joe = FakeClient(self.console, name="Joe", exactName="Joe", guid="zaerezarezar", groupBits=1)
        self.simon = FakeClient(self.console, name="Simon", exactName="Simon", guid="qsdfdsqfdsqf", groupBits=0)
        self.admin = FakeClient(self.console, name="Level-40-Admin", exactName="Level-40-Admin", guid="875sasda", groupBits=16,)
        self.superadmin = FakeClient(self.console, name="God", exactName="God", guid="f4qfer654r", groupBits=128)

    def test_warnings(self):
        self.joe.connects('joe')
        self.simon.connects('simon')
        # simon have a highping - 666ms
        when(self.console).getPlayerPings().thenReturn({
            self.joe.cid:10,
            self.simon.cid: 666,
        })
        #clear message hostory
        self.joe.message_history = []
        self.simon.message_history = []

        self.p._ignoreTill = 0
        # let the pingkicker work
        time.sleep(10)
        self.p._ignoreTill = 90

        #self.assertEqual('Your ping is too high. If you can, try to reduce it!', self.simon.message_history[0])
        #self.assertEqual('Your ping is still too high. You will get kicked automatically.            Nothing personal!', self.simon.message_history[1])

        self.assertListEqual(['Your ping is too high. If you can, try to reduce it!',
                              'Your ping is still too high. You will get kicked automatically.            Nothing personal!'

                             ], self.simon.message_history)

    def test_kick(self):
        self.joe.kick = Mock()
        self.joe.connects('joe')
        # joe have a highping
        when(self.console).getPlayerPings().thenReturn({
            self.joe.cid:666,
        })
        self.p._ignoreTill = 0
        # let the pingkicker work
        time.sleep(10)
        self.p._ignoreTill = 90

        # joe get kick for highping
        self.joe.kick.assert_called_with('because his ping was too high for this server 666.')
