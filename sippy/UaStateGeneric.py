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
# $Id: UaStateGeneric.py,v 1.4 2009/01/05 20:14:00 sobomax Exp $

class UaStateGeneric(object):
    sname = 'Generic'
    ua = None
    connected = False
    dead = False

    def __init__(self, ua):
        self.ua = ua

    def recvRequest(self, req):
        return None

    def recvResponse(self, resp):
        return None

    def recvEvent(self, event):
        return None

    def cancel(self, rtime):
        return None

    def onStateChange(self, newstate):
        pass

    def __str__(self):
        return self.sname
