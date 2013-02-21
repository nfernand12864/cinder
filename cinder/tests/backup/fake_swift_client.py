# Copyright (C) 2012 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import httplib
import json
import os
import zlib

from cinder.openstack.common import log as logging
from swiftclient import client as swift

LOG = logging.getLogger(__name__)


class FakeSwiftClient(object):
    """Logs calls instead of executing."""
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def Connection(self, *args, **kargs):
        LOG.debug("fake FakeSwiftClient Connection")
        return FakeSwiftConnection()


class FakeSwiftConnection(object):
    """Logging calls instead of executing"""
    def __init__(self, *args, **kwargs):
        pass

    def head_container(self, container):
        LOG.debug("fake head_container(%s)" % container)
        if container == 'missing_container':
            raise swift.ClientException('fake exception',
                                        http_status=httplib.NOT_FOUND)
        if container == 'unauthorized_container':
            raise swift.ClientException('fake exception',
                                        http_status=httplib.UNAUTHORIZED)
        pass

    def put_container(self, container):
        LOG.debug("fake put_container(%s)" % container)
        pass

    def get_container(self, container, **kwargs):
        LOG.debug("fake get_container(%s)" % container)
        fake_header = None
        fake_body = [{'name': 'backup_001'},
                     {'name': 'backup_002'},
                     {'name': 'backup_003'}]
        return fake_header, fake_body

    def head_object(self, container, name):
        LOG.debug("fake put_container(%s, %s)" % (container, name))
        return {'etag': 'fake-md5-sum'}

    def get_object(self, container, name):
        LOG.debug("fake get_object(%s, %s)" % (container, name))
        if 'metadata' in name:
            fake_object_header = None
            metadata = {}
            metadata['version'] = '1.0.0'
            metadata['backup_id'] = 123
            metadata['volume_id'] = 123
            metadata['backup_name'] = 'fake backup'
            metadata['backup_description'] = 'fake backup description'
            metadata['created_at'] = '2013-02-19 11:20:54,805'
            metadata['objects'] = [{
                'backup_001': {'compression': 'zlib', 'length': 10},
                'backup_002': {'compression': 'zlib', 'length': 10},
                'backup_003': {'compression': 'zlib', 'length': 10}
            }]
            metadata_json = json.dumps(metadata, sort_keys=True, indent=2)
            fake_object_body = metadata_json
            return (fake_object_header, fake_object_body)

        fake_header = None
        fake_object_body = os.urandom(1024 * 1024)
        return (fake_header, zlib.compress(fake_object_body))

    def put_object(self, container, name, reader):
        LOG.debug("fake put_object(%s, %s)" % (container, name))
        return 'fake-md5-sum'

    def delete_object(self, container, name):
        LOG.debug("fake delete_object(%s, %s)" % (container, name))
        pass
