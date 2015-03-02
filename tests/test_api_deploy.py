# coding: utf-8

import json

from eru.models import Task, Port
from eru.common import code

from tests.prepare import create_local_test_data


def test_build_image(client, test_db):
    app, version, group, pod, host = create_local_test_data()

    rv = client.post('/api/deploy/build/group/pod/blueberry',
            data=json.dumps({'base': 'containerops.cn/tonicbupt/ubuntu:python-2014.11.28', 'version': version.sha}),
            content_type='application/json')
    assert rv.status_code == 200
    r = json.loads(rv.data)
    assert r[u'r'] == 0
    task_id = r[u'task']
    assert task_id
    task = Task.get(task_id)
    assert task.host_id == host.id
    assert task.app_id == app.id
    assert task.version_id == version.id
    assert task.type == code.TASK_BUILD
    assert task.props == {'base': 'containerops.cn/tonicbupt/ubuntu:python-2014.11.28'}


def test_create_container(client, test_db):
    app, version, group, pod, host = create_local_test_data()
    rv = client.post('/api/deploy/public/group/pod/blueberry',
            data=json.dumps({'ncontainer': 1, 'version': version.sha, 'entrypoint': 'web', 'env': 'prod'}),
            content_type='application/json')
    assert rv.status_code == 200
    r = json.loads(rv.data)
    assert len(r['tasks']) == 1
    task_id = r['tasks'][0]
    assert task_id
    task = Task.get(task_id)
    assert task.host_id == host.id
    assert task.app_id == app.id
    assert task.version_id == version.id
    assert task.type == code.TASK_CREATE
    props = task.props
    assert props['ncontainer'] == 1
    assert props['entrypoint'] == 'web'
    assert props['cores'] == []
    assert len(props['ports']) == 1
    port = Port.get(props['ports'][0])
    assert port.is_used()
    assert port.host_id == host.id

