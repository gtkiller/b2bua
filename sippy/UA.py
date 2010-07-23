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
# $Id: UA.py,v 1.13.2.1 2009/11/20 19:51:52 sobomax Exp $

from SipHeader import SipHeader
from SipAuthorization import SipAuthorization
from UasStateIdle import UasStateIdle
from UacStateIdle import UacStateIdle
from SipRequest import SipRequest
from SipContentType import SipContentType
from SipProxyAuthorization import SipProxyAuthorization
from CCEvents import CCEventTry, CCEventFail, CCEventDisconnect, CCEventInfo
from MsgBody import MsgBody
from hashlib import md5
from random import random
from time import time

class UA(object):
    global_config = None
    state = None
    event_cb = None
    uasReq = None
    uacResp = None
    username = None
    password = None
    equeue = None
    dId = None
    credit_time = None
    credit_timer = None
    warn_timer = None
    conn_cbs = None
    disc_cbs = None
    fail_cbs = None
    ring_cbs = None
    dead_cbs = None
    rCSeq = None
    lTag = None
    lUri = None
    rUri = None
    cId = None
    lCSeq = None
    lContact = None
    cGUID = None
    rAddr = None
    rAddr0 = None
    routes = None
    rTarget = None
    uasResp = None
    lSDP = None
    rSDP = None
    kaInterval = 0
    branch = None
    reqs = None
    extra_headers = None
    useRefer = True
    expire_time = None
    expire_timer = None
    no_progress_time = None
    no_progress_timer = None
    on_local_sdp_change = None
    on_remote_sdp_change = None
    last_scode = 100
    user_agent = None
    elast_seq = None
    origin = None

    def __init__(self, global_config, event_cb = None, username = None, password = None, nh_address = None, credit_time = None, \
      conn_cbs = None, disc_cbs = None, fail_cbs = None, ring_cbs = None, dead_cbs = None, ltag = None, extra_headers = None, \
      expire_time = None, no_progress_time = None):
        self.global_config = global_config
        self.event_cb = event_cb
        self.equeue = []
        self.username = username
        self.password = password
        self.rAddr = nh_address
        self.rAddr0 = self.rAddr
        self.credit_time = credit_time
        if conn_cbs:
            self.conn_cbs = conn_cbs
        else:
            self.conn_cbs = ()
        if disc_cbs:
            self.disc_cbs = disc_cbs
        else:
            self.disc_cbs = ()
        if fail_cbs:
            self.fail_cbs = fail_cbs
        else:
            self.fail_cbs = ()
        if ring_cbs:
            self.ring_cbs = ring_cbs
        else:
            self.ring_cbs = ()
        if dead_cbs:
            self.dead_cbs = dead_cbs
        else:
            self.dead_cbs = ()
        if ltag:
            self.lTag = ltag
        else:
            self.lTag = md5(str((random() * 1000000000L) + time())).hexdigest()
        self.reqs = {}
        self.extra_headers = extra_headers
        self.expire_time = expire_time
        self.no_progress_time = no_progress_time
        #print self.username, self.password

    def recvRequest(self, req):
        #print 'Received request %s in state %s instance %s' % (req.getMethod(), self.state, self)
        #print self.rCSeq, req.getHFBody('cseq').getCSeqNum()
        if not self.user_agent:
            self.update_ua(req)
        if self.rCSeq != None and self.rCSeq >= req.getHFBody('cseq').getCSeqNum():
            return (req.genResponse(500, 'Server Internal Error'), None, None)
        self.rCSeq = req.getHFBody('cseq').getCSeqNum()
        if not self.state:
            if req.getMethod() == 'INVITE':
                self.changeState((UasStateIdle,))
            else:
                return None
        newstate = self.state.recvRequest(req)
        if newstate:
            self.changeState(newstate)
        self.emitPendingEvents()
        if newstate and req.getMethod() == 'INVITE':
            return (None, self.state.cancel, self.disconnect)
        else:
            return None

    def recvResponse(self, resp):
        if not self.state:
            return
        self.update_ua(resp)
        code, reason = resp.getSCode()
        cseq, method = resp.getHFBody('cseq').getCSeq()
        if method == 'INVITE' and self.reqs.has_key(cseq) and code == 401 and resp.countHFs('www-authenticate') != 0 and \
          self.username and self.password and self.reqs[cseq].countHFs('authorization') == 0:
            challenge = resp.getHFBody('www-authenticate')
            req = self.genRequest('INVITE', self.lSDP, challenge.getNonce(), challenge.getRealm())
            self.lCSeq += 1
            self.tr = self.global_config['sip_tm'].newTransaction(req, self.recvResponse)
            del self.reqs[cseq]
            return None
        if method == 'INVITE' and self.reqs.has_key(cseq) and code == 407 and resp.countHFs('proxy-authenticate') != 0 and \
          self.username and self.password and self.reqs[cseq].countHFs('proxy-authorization') == 0:
            challenge = resp.getHFBody('proxy-authenticate')
            req = self.genRequest('INVITE', self.lSDP, challenge.getNonce(), challenge.getRealm(), SipProxyAuthorization)
            self.lCSeq += 1
            self.tr = self.global_config['sip_tm'].newTransaction(req, self.recvResponse)
            del self.reqs[cseq]
            return None
        if code >= 200 and self.reqs.has_key(cseq):
            del self.reqs[cseq]
        newstate = self.state.recvResponse(resp)
        if newstate:
            self.changeState(newstate)
        self.emitPendingEvents()

    def recvEvent(self, event):
        #print self, event
        if not self.state:
            if isinstance(event, CCEventTry) or isinstance(event, CCEventFail) or isinstance(event, CCEventDisconnect):
                self.changeState((UacStateIdle,))
            else:
                return
        newstate = self.state.recvEvent(event)
        if newstate:
            self.changeState(newstate)
        self.emitPendingEvents()

    def disconnect(self, rtime = None):
        if not rtime:
            rtime = time()
        self.equeue.append(CCEventDisconnect(rtime = rtime))
        self.recvEvent(CCEventDisconnect(rtime = rtime))

    def expires(self):
        self.expire_timer = None
        self.disconnect()

    def no_progress_expires(self):
        self.no_progress_timer = None
        self.disconnect()

    def credit_expires(self):
        self.credit_timer = None
        self.disconnect()

    def warn(self):
        rtime = time()
        self.warn_timer = None
        body = MsgBody('Signal=3\r\nDuration=1640\r\n', 'application/dtmf-relay')
        self.equeue.append(CCEventInfo(body, rtime = rtime))
        self.recvEvent(CCEventInfo(body.getCopy(), rtime = rtime))

    def changeState(self, newstate):
        if self.state:
            self.state.onStateChange(newstate[0])
        self.state = newstate[0](self)
        if len(newstate) > 1:
            for callback in newstate[1]:
                callback(self, *newstate[2:])

    def emitEvent(self, event):
        if self.event_cb:
            if self.elast_seq and self.elast_seq >= event.seq:
                #print 'ignoring out-of-order event', event, event.seq, self.elast_seq, self.cId
                return
            self.elast_seq = event.seq
            self.event_cb(event, self)

    def emitPendingEvents(self):
        while self.equeue and self.event_cb:
            event = self.equeue.pop(0)
            if self.elast_seq != None and self.elast_seq >= event.seq:
                #print 'ignoring out-of-order event', event, event.seq, self.elast_seq, self.cId
                continue
            self.elast_seq = event.seq
            self.event_cb(event, self)

    def genRequest(self, method, body = None, nonce = None, realm = None, SipXXXAuthorization = SipAuthorization):
        req = SipRequest(method = method, ruri = self.rTarget, to = self.rUri, fr0m = self.lUri,
                         cseq = self.lCSeq, callid = self.cId, contact = self.lContact,
                         routes = self.routes, target = self.rAddr, cguid = self.cGUID)
        if nonce != None and realm != None and self.username != None and self.password != None:
            auth = SipXXXAuthorization(realm = realm, nonce = nonce, method = method, uri = str(self.rTarget),
              username = self.username, password = self.password)
            req.appendHeader(SipHeader(body = auth))
        if body != None:
            req.setBody(body)
        if self.extra_headers != None:
            req.appendHeaders(self.extra_headers)
        self.reqs[self.lCSeq] = req
        return req

    def sendUasResponse(self, scode, reason, body = None, contact = None, \
      extra_header = None):
        self.uasResp.setSCode(scode, reason)
        self.uasResp.setBody(body)
        self.uasResp.delHFs('www-authenticate')
        self.uasResp.delHFs('contact')
        if contact != None:
            self.uasResp.appendHeader(SipHeader(name = 'contact', body = contact))
        if extra_header != None:
            self.uasResp.appendHeader(extra_header)
        self.global_config['sip_tm'].sendResponse(self.uasResp)

    def isYours(self, req = None, call_id = None, from_tag = None, to_tag = None):
        #print self.branch, req.getHFBody('via').getBranch()
        if req != None:
            if self.branch != None and self.branch != req.getHFBody('via').getBranch():
                return None
            call_id = str(req.getHFBody('call-id'))
            from_tag = req.getHFBody('from').getTag()
            to_tag = req.getHFBody('to').getTag()
        #print str(self.cId), call_id
        if call_id != str(self.cId):
            return None
        #print self.rUri.getTag(), from_tag
        if self.rUri != None and self.rUri.getTag() != from_tag:
            return None
        #print self.lUri.getTag(), to_tag
        if self.lUri != None and self.lUri.getTag() != to_tag:
            return None
        return self

    def isDead(self):
        if self.state:
            return self.state.dead
        return False

    def isConnected(self):
        if self.state:
            return self.state.connected
        return False

    def getCLD(self):
        if not self.rUri:
            return None
        return self.rUri.getUrl().username

    def getCLI(self):
        if not self.lUri:
            return None
        return self.lUri.getUrl().username

    def getCallingName(self):
        if not self.lUri:
            return None
        return self.lUri.getUri().name

    def getRAddr(self):
        return self.rAddr

    def getRAddr0(self):
        return self.rAddr0

    def getCID(self):
        # Return tuple containing call-id, local tag and remote tag
        rval = [str(self.cId), None, None]
        if self.lUri:
            rval[1] = self.lUri.getTag()
        if self.rUri:
            rval[2] = self.rUri.getTag()
        return tuple(rval)

    def delayed_remote_sdp_update(self, event, remote_sdp_body):
        self.rSDP = remote_sdp_body.getCopy()
        self.equeue.append(event)
        self.emitPendingEvents()

    def update_ua(self, msg):
        if msg.countHFs('user-agent') > 0:
            self.user_agent = msg.getHFBody('user-agent').name
        elif msg.countHFs('server') > 0:
            self.user_agent = msg.getHFBody('server').name
        return
