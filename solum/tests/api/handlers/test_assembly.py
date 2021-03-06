# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock

from solum.api.handlers import assembly_handler
from solum.objects import assembly
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


STATES = assembly.States


@mock.patch('solum.objects.registry')
class TestAssemblyHandler(base.BaseTestCase):
    def setUp(self):
        super(TestAssemblyHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_assembly_get(self, mock_registry):
        mock_registry.return_value.Assembly.get_by_uuid.return_value = {
            'plan_id': '1234'
        }
        handler = assembly_handler.AssemblyHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        get_by_uuid = mock_registry.Assembly.get_by_uuid
        get_by_uuid.assert_called_once_with(self.ctx, 'test_id')

    def test_assembly_get_all(self, mock_registry):
        mock_registry.AssemblyList.get_all.return_value = {}
        handler = assembly_handler.AssemblyHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.AssemblyList.get_all.assert_called_once_with(self.ctx)

    def test_update(self, mock_registry):
        data = {'user_id': 'new_user_id',
                'plan_uuid': 'input_plan_uuid'}
        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_uuid.return_value = db_obj
        handler = assembly_handler.AssemblyHandler(self.ctx)
        res = handler.update('test_id', data)
        self.assertEqual(db_obj.user_id, res.user_id)
        db_obj.save.assert_called_once_with(self.ctx)
        db_obj.update.assert_called_once_with(data)
        mock_registry.Assembly.get_by_uuid.assert_called_once_with(self.ctx,
                                                                   'test_id')

    @mock.patch('solum.worker.api.API.build')
    @mock.patch('solum.common.solum_keystoneclient.KeystoneClientV3')
    def test_create(self, mock_kc, mock_build, mock_registry):
        data = {'user_id': 'new_user_id',
                'uuid': 'input_uuid',
                'plan_uuid': 'input_plan_uuid'}

        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.return_value = db_obj
        fp = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = fp
        fp.raw_content = {
            'name': 'theplan',
            'artifacts': [{'name': 'nodeus',
                           'artifact_type': 'heroku',
                           'content': {
                               'href': 'https://example.com/ex.git'},
                           'language_pack': 'auto'}]}
        mock_registry.Image.return_value = fakes.FakeImage()
        trust_ctx = utils.dummy_context()
        trust_ctx.trust_id = '12345'
        mock_kc.return_value.create_trust_context.return_value = trust_ctx

        handler = assembly_handler.AssemblyHandler(self.ctx)
        res = handler.create(data)
        db_obj.update.assert_called_once_with(data)
        db_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)
        mock_build.assert_called_once_with(
            build_id=8, name='nodeus', assembly_id=8,
            source_uri='https://example.com/ex.git',
            test_cmd=None,
            base_image_id='auto', source_format='heroku', image_format='qcow2')
        mock_kc.return_value.create_trust_context.assert_called_once_with()

    @mock.patch('solum.common.solum_keystoneclient.KeystoneClientV3')
    @mock.patch('solum.deployer.api.API.delete_heat_stack')
    def test_delete(self, mock_deploy, mock_kc, mock_registry):
        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_uuid.return_value = db_obj
        handler = assembly_handler.AssemblyHandler(self.ctx)
        handler.delete('test_id')
        db_obj.save.assert_called_once_with(self.ctx)
        mock_registry.Assembly.get_by_uuid.assert_called_once_with(self.ctx,
                                                                   'test_id')
        mock_kc.return_value.delete_trust.assert_called_once_with(
            'trust_worthy')
        mock_deploy.assert_called_once_with(assem_id=db_obj.id)
        self.assertEqual(STATES.DELETING, db_obj.status)

    def test_trigger_workflow(self, mock_registry):
        trigger_id = 1
        artifacts = [{"name": "Test",
                      "artifact_type": "heroku",
                      "content": {"href": "https://github.com/some/project"},
                      "language_pack": "auto"}]
        db_obj = fakes.FakeAssembly()
        mock_registry.Assembly.get_by_trigger_id.return_value = db_obj
        plan_obj = fakes.FakePlan()
        mock_registry.Plan.get_by_id.return_value = plan_obj
        plan_obj.raw_content = {"artifacts": artifacts}
        handler = assembly_handler.AssemblyHandler(self.ctx)
        handler._build_artifact = mock.MagicMock()
        handler._context_from_trust_id = mock.MagicMock(return_value=self.ctx)
        handler.trigger_workflow(trigger_id)
        handler._build_artifact.assert_called_once_with(db_obj, artifacts[0])
        handler._context_from_trust_id.assert_called_once_with('trust_worthy')
        mock_registry.Assembly.get_by_trigger_id.assert_called_once_with(
            None, trigger_id)
        mock_registry.Plan.get_by_id.assert_called_once_with(self.ctx,
                                                             db_obj.plan_id)
