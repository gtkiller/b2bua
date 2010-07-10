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
# $Id: SipAddressHF.py,v 1.5 2009/06/11 21:48:25 sobomax Exp $

from SipGenericHF import SipGenericHF
from SipAddress import SipAddress
from ESipHeaderCSV import ESipHeaderCSV

class SipAddressHF(SipGenericHF):
    address = None

    def __init__(self, body = None, address = None):
        SipGenericHF.__init__(self, body)
        if body != None:
            csvs = []
            pidx = 0
            while 1:
                idx = body.find(',', pidx)
                if idx == -1:
                    break;
                onum = body[:idx].count('<')
                cnum = body[:idx].count('>')
                qnum = body[:idx].count('"')
                if (onum == 0 and cnum == 0 and qnum == 0) or (onum > 0 and \
                  onum == cnum and (qnum % 2 == 0)):
                    csvs.append(body[:idx])
                    body = body[idx + 1:]
                    pidx = 0
                else:
                    pidx = idx + 1
            if (len(csvs) > 0):
                csvs.append(body)
                raise ESipHeaderCSV(None, csvs)
        else:
            self.parsed = True
            self.address = address

    def parse(self):
        self.parsed = True
        self.address = SipAddress(self.body)

    def __str__(self):
        if not self.parsed:
            return self.body
        return str(self.address)

    def getCopy(self):
        if not self.parsed:
            return self.__class__(self.body)
        return self.__class__(address = self.address.getCopy())

    def setBody(self, body):
        self.address = body

    def getUri(self):
        return self.address

    def getUrl(self):
        return self.address.url
