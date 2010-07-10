# Copyright (c) 2003-2005 Maxim Sobolev. All rights reserved.
# Copyright (c) 2006-2007 Sippy Software, Inc. All rights reserved.
#
# This file is part of SIPPY, a free RFC3261 SIP stack and B2BUA.
#
# SIPPY is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# For a license to use the SIPPY software under conditions
# other than those described here, or to purchase support for this
# software, please contact Sippy Software, Inc. by e-mail at the
# following addresses: sales@sippysoft.com.
#
# SIPPY is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.
#
# $Id: Cli_session.py,v 1.2 2008/02/18 19:49:45 sobomax Exp $

from twisted.internet.protocol import Protocol
import sys, traceback

class Cli_session(Protocol):
    command_cb = None
    rbuffer = None
    wbuffer = None
    cb_busy = False

    def __init__(self):
        self.rbuffer = ''
        self.wbuffer = ''

    #def connectionMade(self):
    #    print self.transport.getPeer()
    #    self.transport.loseConnection()

    def dataReceived(self, data):
        if len(data) == 0:
            return
        self.rbuffer += data
        self.pump_rxdata()

    def pump_rxdata(self):
        while self.rbuffer.find('\n') != -1:
            if self.cb_busy:
                return
            cmd, self.rbuffer = self.rbuffer.split('\n', 1)
            cmd = cmd.strip()
            if len(cmd) > 0:
                try:
                    self.cb_busy = self.command_cb(self, cmd)
                except:
                    print 'Cli_session: unhandled exception when processing incoming data'
                    print '-' * 70
                    traceback.print_exc(file = sys.stdout)
                    print '-' * 70

    def done(self):
        self.cb_busy = False
        self.pump_rxdata()

    def send(self, data):
        return self.transport.write(data)

    def close(self):
        return self.transport.loseConnection()
