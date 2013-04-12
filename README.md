PingKicker
==========

This plugin can replace the default PingWatch plugin delivered with B3. You should
only use this plugin if you would like to kick players with a ping you think is too
high.

If a player's ping is too high, he will get a few private messages
telling what is going on and that he can be kicked because of it.

After that, if his ping is still too high, he will be kicked and a public message
will be shown to explain why he was kicked.

### Requirements
- latest [B3 Server](http://bigbrotherbot.net)

Usage
-----

### Installation
1. Copy the file [extplugins/pingkicker.py](extplugins/pingkicker.py) into your `b3/extplugins` folder and
[extplugins/conf/plugin_pingkicker.ini](extplugins/conf/plugin_pingkicker.ini) into your `b3/conf` folder

2. Add the following line in your b3.xml file (below the other plugin lines)
  ```xml
  <plugin name="pingkicker" config="@conf/plugin_pingkicker.ini"/>
  ```

Remember, it is not necessary to use this plugin and default pingwatch plugin.
If you enable this pingkicker, you should disable the pingwatch.

### Configuration
The following options can be configured in the file [extplugins/conf/plugin_pingkicker.ini](extplugins/conf/plugin_pingkicker.ini):

`[settings]`

| option            | value   | description
| ----------------- |:-------:|:-----------------------------------------:|
| interval          | 30      | *the interval of ping checking*           |
| max_ping          | 100     | *the maximum allowed ping*                |
| max_ping_duration | 90      | *how long before an offender gets kicked* |
| max_level_checked | 100     | *which levels get ping checking*          |

`[messages]`
Plugin messages.

Support
-------
Support is only provided on www.bigbrotherbot.net forums on the following topic: http://forum.bigbrotherbot.net/releases/pingkicker-plugin/

Credit
------

This plugin has been make possible thanks to:

- `Walker's work (initiator and maintainer to version 1.0.1)
  `http://www.1stsop.nl`_
  Walker@1stsop.nl

Contrib
-------

- documented and reproducible *bugs* can be reported on the [issue tracker](https://github.com/ozon/b3-plugin-pingkicker/issues).
- *patches* are welcome. Send me a [pull request](http://help.github.com/send-pull-requests/).

.. image:: https://api.travis-ci.org/ozon/b3-plugin-pingkicker.png
   :alt: Build Status
   :target: https://api.travis-ci.org/ozon/b3-plugin-pingkicker
