#!/usr/bin/env python
#
# Copyright (c) 2003-2005 Maxim Sobolev. All rights reserved.
# Copyright (c) 2006-2009 Sippy Software, Inc. All rights reserved.
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
# $Id: setup.py,v 1.1.2.3 2009/12/01 04:58:44 sobomax Exp $

from distutils.core import setup

setup(name = 'sippy',
  version = '1.0.3',
  description = 'SIP RFC3261 Back-to-back User Agent (B2BUA)',
  author = 'Sippy Software, Inc.',
  author_email = 'sales@sippysoft.com',
  url = 'http://www.b2bua.org/',
  packages = ['sippy'],
  scripts = ['sippy/b2bua_radius.py', 'sippy/b2bua_simple.py'],
  data_files = [('etc/sippy', ['sippy/dictionary']),
                ('share/doc/sippy', ['COPYING'])])
