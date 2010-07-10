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
# $Id: SipVia.py,v 1.6.2.1 2009/11/20 19:51:52 sobomax Exp $

from random import random
from hashlib import md5
from time import time
from SipGenericHF import SipGenericHF
from SipConf import SipConf
from ESipHeaderCSV import ESipHeaderCSV

class SipVia(SipGenericHF):
    hf_names = ('via', 'v')

    sipver = None
    hostname = None
    port = None
    params = None

    def __init__(self, body = None, sipver = None, hostname = None, port = None, params = None):
        if body != None and body.find(',') > -1:
            raise ESipHeaderCSV(None, body.split(','))
        SipGenericHF.__init__(self, body)
        if body == None:
            self.parsed = True
            self.params = {}
            if sipver == None:
                self.sipver = 'SIP/2.0/UDP'
            else:
                self.sipver = sipver
            if hostname == None:
                self.hostname = SipConf.my_address
                self.params['rport'] = None
            else:
                self.hostname = hostname
            if port == None:
                self.port = SipConf.my_port
            else:
                self.port = port
            if params != None:
                self.params = params

    def parse(self):
        self.parsed = True
        self.params = {}
        self.sipver, hostname = self.body.split(None, 1)
        hcomps = [x.strip() for x in hostname.split(';')]
        for param in hcomps[1:]:
            sparam = param.split('=', 1)
            if len(sparam) == 1:
                val = None
            else:
                val = sparam[1]
            self.params[sparam[0]] = val
        hcomps = hcomps[0].split(':', 1)
        if len(hcomps) == 2:
            self.port = int(hcomps[1])
        else:
            self.port = ''
        self.hostname = hcomps[0]

    def __str__(self):
        if not self.parsed:
            return self.body
        s = self.sipver + ' ' + self.hostname
        if self.port != '':
            s += ':' + str(self.port)
        for key, val in self.params.items():
            s += ';' + key
            if val != None:
                s += '=' + val
        return s

    def getCopy(self):
        if not self.parsed:
            return SipVia(self.body)
        return SipVia(sipver = self.sipver, hostname = self.hostname, port = self.port, params = self.params.copy())

    def genBranch(self):
        self.params['branch'] = 'z9hG4bK' + md5(str((random() * 1000000000L) + time())).hexdigest()

    def getBranch(self):
        return self.params.get('branch', None)

    def setParam(self, name, value = None):
        self.params[name] = value

    def getAddr(self):
        if self.port == '':
            return (self.hostname, SipConf.default_port)
        else:
            return (self.hostname, self.port)

    def getTAddr(self):
        rport = self.params.get('rport', None)
        if rport == None:
            rport = self.getAddr()[1]
        else:
            rport = int(rport)
        return (self.params.get('received', self.getAddr()[0]), rport)
