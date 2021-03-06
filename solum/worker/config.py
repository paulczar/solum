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

"""Config options for Solum Worker service."""


from oslo.config import cfg

SERVICE_OPTS = [
    cfg.StrOpt('topic',
               default='solum-worker',
               help='The queue to add build tasks to'),
    cfg.StrOpt('host',
               default='localhost',
               help='The location of the build rpc queue'),
    cfg.StrOpt('handler',
               default='shell',
               help='The worker endpoint to employ'),
    cfg.StrOpt('task_log_dir',
               default='/var/log/solum/worker',
               help='The directory containing task log output.'),
]

opt_group = cfg.OptGroup(
    name='worker',
    title='Options for the solum-worker service')
cfg.CONF.register_group(opt_group)
cfg.CONF.register_opts(SERVICE_OPTS, opt_group)
