# -*- coding: utf-8 -*-
#
# Copyright (C) Red Hat, Inc
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

from lxml import etree
import logging
import os
import sys


LOG = logging.getLogger(__name__)

formatter = logging.Formatter('%(levelname)s - %(message)s')
streamhandler = logging.StreamHandler(stream=sys.stdout)
streamhandler.setFormatter(formatter)
LOG.addHandler(streamhandler)
LOG.setLevel(logging.DEBUG)

HTTP_TIMEOUT = 600


def get_team_id(dci_context, team_name):
    uri = '%s/teams?where=name:%s' % (dci_context.dci_cs_api, team_name)
    res = dci_context.session.get(uri, timeout=HTTP_TIMEOUT)
    if res.status_code != 200 or len(res.json()['teams']) == 0:
        LOG.error('team %s: status: %s, message: %s' % (team_name,
                                                        res.status_code,
                                                        res.text))
    if len(res.json()['teams']) == 0:
        LOG.exception('teams %s not found' % team_name)
    return res.json()['teams'][0]['id']


def get_topic_id(dci_context, topic_name):
    uri = '%s/topics?where=name:%s' % (dci_context.dci_cs_api, topic_name)
    res = dci_context.session.get(uri, timeout=HTTP_TIMEOUT)
    if res.status_code != 200:
        LOG.error('topic %s: status: %s, message: %s' % (topic_name,
                                                         res.status_code,
                                                         res.text))
    if len(res.json()['topics']) == 0:
        LOG.exception('topic %s not found' % topic_name)
    return res.json()['topics'][0]['id']


def get_jobs(dci_context, team_id, topic_id):
    uri = '%s/jobs?where=team_id:%s,topic_id:%s&embed=files' % \
             (dci_context.dci_cs_api, team_id, topic_id)
    res = dci_context.session.get(uri, timeout=HTTP_TIMEOUT)
    if res.status_code != 200:
        LOG.error('status: %s, message: %s' % (res.status_code, res.text))
    return res.json()['jobs']


def junit_to_dict(junit):
    res = dict()
    try:
        root = etree.fromstring(junit)
        for testsuite in root.findall('testsuite'):
            for tc in testsuite:
                key = "%s/%s" % (tc.get('classname'), tc.get('name'))
                key = key.strip()
                if tc.get('time') is None or float(tc.get('time')) == 0.0:
                    res[key] = ""
                else:
                    res[key] = float(tc.get('time'))
    except etree.XMLSyntaxError as e:
        LOG.error('XMLSyntaxError %s' % str(e))
    return res


def get_test_path(topic_name, job_id, test_name):
    test_csv_name = '%s_%s.csv' % (job_id, test_name)
    path = '%s/%s' % (topic_name, test_csv_name)
    return os.path.abspath(path)


def write_test_csv(job_id, test_path, test_dict):
    with open(test_path, 'w') as f:
        f.write('testname!%s\n' % job_id)
        for tc in test_dict:
            f.write('%s!%s\n' % (tc, test_dict[tc]))


def get_junit_of_file(dci_context, file_id):
    uri = '%s/files/%s/content' % (dci_context.dci_cs_api, file_id)
    res = dci_context.session.get(uri, timeout=HTTP_TIMEOUT)
    if res.status_code != 200:
        LOG.error('file not found: %s' % file_id)
    return res.text


def sync(dci_context, team_name, topic_name, test_name):

    team_id = get_team_id(dci_context, team_name)
    LOG.info('%s team id %s' % (team_name, team_id))
    topic_id = get_topic_id(dci_context, topic_name)
    LOG.info('%s topic id %s' % (topic_name, topic_id))
    LOG.info('getting jobs...')
    jobs = get_jobs(dci_context, team_id, topic_id)

    LOG.info('convert jobs %s tests to csv files...' % test_name)
    for job in jobs:
        for file in job['files']:
            if file['name'] == test_name:
                test_path = get_test_path(topic_name, job['id'], test_name)  # noqa
                if os.path.exists(test_path):
                    LOG.debug('%s test of job %s already exist' % (test_name, job['id']))  # noqa
                    continue
                LOG.info('convert junit job %s to csv' % job['id'])
                junit = get_junit_of_file(dci_context, file['id'])
                test_dict = junit_to_dict(junit)
                write_test_csv(job['id'], test_path, test_dict)