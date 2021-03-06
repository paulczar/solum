#!/usr/bin/env python
# Copyright 2014 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import sys

from oslo.config import cfg

from solum.common import context
from solum.openstack.common import log as logging
from solum.worker import api


LOG = logging.getLogger(__name__)


if __name__ == '__main__':
    conf_files = ['--config-file=/etc/solum/solum.conf']
    cfg.CONF(conf_files, project='solum')
    message = ' '.join(sys.argv[1:])
    api.API(context=context.RequestContext()).echo(message)
