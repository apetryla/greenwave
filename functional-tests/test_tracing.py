# SPDX-License-Identifier: GPL-2.0+

from unittest.mock import MagicMock, patch

import stomp

from greenwave.listeners.resultsdb import ResultsDBListener
from greenwave.subjects.subject import SubjectType

JSON_MESSAGE = {
    "data": {
        "brew_task_id": [
            "57212843"
        ],
        "ci_docs": [
            "https://docs.engineering.redhat.com/display/CVP/" +
            "Container+Verification+Pipeline+E2E+Documentation"
        ],
        "ci_email": [
            "cvp@redhat.com"
        ],
        "ci_name": [
            "Container Verification Pipeline"
        ],
        "ci_team": [
            "CVP Development Team"
        ],
        "ci_url": [
            "https://jenkins-cvp-5c79a5a8d70cc51dd4c37835." +
            "apps.ocp-c1.prod.psi.redhat.com/"
        ],
        "full_names": [
            "registry-proxy.engineering.redhat.com/rh-osbs/openshift-ose-must-gather:" +
            "v4.15.0-202311271051.p0.gc7f5e3f.assembly.stream"
        ],
        "id": [
            "sha256:a7fc01280c6b8173611c75a2cbd5a19f5d2ce42d9578d4efcc944e4bc80b09a0"
        ],
        "issuer": [
            "exd-ocp-buildvm-bot-prod"
        ],
        "item": [
            "avahi"
        ],
        "log": [
            "https://jenkins-cvp-5c79a5a8d70cc51dd4c37835.apps." +
            "ocp-c1.prod.psi.redhat.com/job/cvp-product-test/2555/console"
        ],
        "msg_id": [
            "ID:jenkins-2-8dcwr-46389-1700226798425-136563:1:1:1:1"
        ],
        "scratch": [
            "false"
        ],
        "system_architecture": [
            "x86_64"
        ],
        "system_provider": [
            "openshift"
        ],
        "type": [
            "redhat-module"
        ]
    },
    "groups": [],
    "href": "https://resultsdb-api.engineering.redhat.com/api/v2.0/results/23659469",
    "id": 23659469,
    "note": "Result status PASSED",
    "outcome": "PASSED",
    "ref_url": "http://external-ci-coldstorage.datahub.redhat.com/cvp/cvp-product-test/" +
               "ose-must-gather-container-v4.15.0-202311271051.p0.gc7f5e3f.assembly." +
               "stream/1e4142dc-18cf-409d-b401-57e555156ab6/",
    "submit_time": "2023-11-27T11:42:24.538119",
    "testcase": {
        "href": "https://resultsdb-api.engineering.redhat.com/api/v2.0/testcases/" +
                "cvp.rhproduct.default.source-container-compliance",
        "name": "baseos-ci.redhat-module.tier0.functional",
        "ref_url": None
    },
    "traceparent": "00-a9c3b99a95cc045e573e163c3ac80a77-d99d251a8caecd06-01"
}
patch_subject = SubjectType()
patch_subject.id = "redhat-module"

patch_decision = {
    'policies_satisfied': True,
    'summary': "TestSucced",
    'satisfied_requirements': [None],
    'unsatisfied_requirements': [None]
}
patch_old_decision = {
    'policies_satisfied': True,
    'summary': "TestSucced",
    'satisfied_requirements': [None],
    'unsatisfied_requirements': [None]
}

real_connection = stomp.connect.StompConnection11()
mock_connection = MagicMock(real_connection)
mock_connection.send = MagicMock(side_effect=[])


@patch('greenwave.listeners.base._is_decision_unchanged', return_value=False)
@patch.object(ResultsDBListener, '_old_and_new_decisions',
              return_value=(patch_old_decision, patch_decision))
@patch('greenwave.subjects.factory.subject_types', return_value=[patch_subject])
def test_tracing(mocked_factory, mocked_decision, mocked_decision_unchanged):
    resultdb_class = ResultsDBListener()
    with patch.object(resultdb_class, 'connection', side_effect=mock_connection):
        mock_publish = MagicMock(side_effect=resultdb_class._publish_decision_update)
        resultdb_class._publish_decision_update = mock_publish
        resultdb_class._consume_message(JSON_MESSAGE)
        mock_publish.assert_called_once()
        assert mock_publish.call_args.args[0]["traceparent"] == JSON_MESSAGE[
            "traceparent"]
