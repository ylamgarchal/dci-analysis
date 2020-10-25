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

import concurrent.futures

from lxml import etree
import json
import logging
import os
import requests
import sys


LOG = logging.getLogger(__name__)

formatter = logging.Formatter('%(levelname)s - %(message)s')
streamhandler = logging.StreamHandler(stream=sys.stdout)
streamhandler.setFormatter(formatter)
LOG.addHandler(streamhandler)
LOG.setLevel(logging.DEBUG)

HTTP_TIMEOUT = 600


def get_with_retry(dci_context, uri, timeout=5, nb_retry=5):
    res = None
    for i in range(nb_retry):
        try:
            res = dci_context.session.get(uri, timeout=5)
            break
        except requests.exceptions.Timeout:
            LOG.info('timeout on %s, retrying...' % uri)
        except requests.ConnectionError:
            LOG.info('connection error on %s, retrying...' % uri)
    return res


def get_team_id(dci_context, team_name):
    uri = '%s/teams?where=name:%s' % (dci_context.dci_cs_api, team_name)
    res = get_with_retry(dci_context, uri)
    if res.status_code != 200 or len(res.json()['teams']) == 0:
        LOG.error('team %s: status: %s, message: %s' % (team_name,
                                                        res.status_code,
                                                        res.text))
    if len(res.json()['teams']) == 0:
        LOG.exception('teams %s not found' % team_name)
    return res.json()['teams'][0]['id']


def get_product_id(dci_context, product_name):
    uri = '%s/products?where=name:%s' % (dci_context.dci_cs_api, product_name)
    res = get_with_retry(dci_context, uri)
    if res.status_code != 200 or len(res.json()['products']) == 0:
        LOG.error('product %s: status: %s, message: %s' % (product_name,
                                                           res.status_code,
                                                           res.text))
    if len(res.json()['products']) == 0:
        LOG.exception('product %s not found' % product_name)
    return res.json()['products'][0]['id']


def get_topics_of_product(dci_context, product_id):
    uri = '%s/products/%s?embed=topics' % (dci_context.dci_cs_api, product_id)
    res = get_with_retry(dci_context, uri)
    if res.status_code != 200:
        LOG.error('product %s: status: %s, message: %s' % (product_id,
                                                           res.status_code,
                                                           res.text))
    return res.json()['product']['topics']


def get_topic_id(dci_context, topic_name):
    uri = '%s/topics?where=name:%s' % (dci_context.dci_cs_api, topic_name)
    res = get_with_retry(dci_context, uri)
    if res.status_code != 200:
        LOG.error('topic %s: status: %s, message: %s' % (topic_name,
                                                         res.status_code,
                                                         res.text))
    if len(res.json()['topics']) == 0:
        LOG.exception('topic %s not found' % topic_name)
        sys.exit(1)
    return res.json()['topics'][0]['id']


def get_jobs(dci_context, team_id, topic_id):
    uri = '%s/jobs?where=team_id:%s,topic_id:%s&embed=components' % \
             (dci_context.dci_cs_api, team_id, topic_id)
    res = get_with_retry(dci_context, uri)

    if res is not None and res.status_code != 200:
        LOG.error('status: %s, message: %s' % (res.status_code, res.text))
    return res.json()['jobs']


def get_files_of_job(dci_context, job_id):
    uri = '%s/jobs/%s/files' % (dci_context.dci_cs_api, job_id)
    res = get_with_retry(dci_context, uri)

    if res is not None and res.status_code != 200:
        LOG.error('status: %s, message: %s' % (res.status_code, res.text))
    return res.json()['files']


def junit_to_dict(junit):
    res = dict()
    try:
        root = etree.fromstring(junit)
        for testsuite in root.findall('testsuite'):
            for tc in testsuite:
                key = "%s/%s" % (tc.get('classname'), tc.get('name'))
                key = key.strip()
                key = key.replace(',', '_')
                if tc.get('time'):
                    res[key] = float(tc.get('time'))
    except etree.XMLSyntaxError as e:
        LOG.error('XMLSyntaxError %s' % str(e))
    return res


def get_test_path(working_dir, topic_name, job, test_name):
    job_date = job['created_at'].split('T')[0]
    test_csv_name = '%s_%s_%s.csv' % (job_date, job['id'], test_name)
    path = '%s/%s/%s' % (working_dir, topic_name, test_csv_name)
    return os.path.abspath(path)


def write_test_csv(job_id, test_path, test_dict):
    with open(test_path, 'w') as f:
        f.write('testname,%s\n' % job_id)
        for tc in test_dict:
            f.write('%s,%s\n' % (tc, test_dict[tc]))


def write_test_json(job_id, test_path, test_json):
    with open(test_path, 'w') as f:
        f.write(json.dumps(test_json, indent=4))


def get_junit_of_file(dci_context, file_id):
    uri = '%s/files/%s/content' % (dci_context.dci_cs_api, file_id)
    res = get_with_retry(dci_context, uri)
    if res is not None and res.status_code != 200:
        LOG.error('file not found: %s' % file_id)
    return res.text


def handle_job(dci_context, job, working_dir, topic_name, topic_name_component, test_name):
    jobs_tags = {}
    topic_name_in_component = False
    for component in job['components']:
        if topic_name_component.lower() in component['name'].lower():
            topic_name_in_component = True
        if not topic_name_in_component:
            continue
        test_path = get_test_path(working_dir, topic_name, job, test_name)  # noqa
        if os.path.exists(test_path):
            LOG.debug('%s test of job %s already exist' % (test_name, job['id']))  # noqa
            continue
    
        files = get_files_of_job(dci_context, job['id'])
        for file in files:
            if file['name'] == test_name:
                LOG.info('download file %s of job %s' % (file['id'], job['id']))  # noqa
                junit = get_junit_of_file(dci_context, file['id'])
                LOG.info('convert junit job %s to csv' % job['id'])
                test_dict = junit_to_dict(junit)
                if len(test_dict.keys()) >= 697:
                    write_test_csv(job['id'], test_path, test_dict)
                    base_test_path = os.path.basename(test_path)
                    jobs_tags[base_test_path] = job['tags']
                else:
                    LOG.warn('job %s tests contains less than 697 tests' % job['id'])
        return jobs_tags


def sync(dci_context, team_name, topic_name, test_name, working_dir):

    team_id = get_team_id(dci_context, team_name)
    LOG.info('%s team id %s' % (team_name, team_id))
    topic_id = get_topic_id(dci_context, topic_name)
    LOG.info('%s topic id %s' % (topic_name, topic_id))
    LOG.info('getting jobs...')
    jobs = get_jobs(dci_context, team_id, topic_id)
    jobs_tags = {}

    topic_name_component = topic_name
    if '-milestone' in topic_name_component:
        topic_name_component = topic_name_component.replace('-milestone', '')
    LOG.info('convert jobs %s tests to csv files...' % test_name)

    futures = []
    pool = concurrent.futures.ProcessPoolExecutor()
    for job in jobs:
        future = pool.submit(handle_job, dci_context, job, working_dir, topic_name, topic_name_component, test_name)
        futures.append(future)
    
    for future in concurrent.futures.as_completed(futures):
        if isinstance(future.result(), dict):
            jobs_tags.update(future.result())
    
    file_jobs_tags = {}
    jobs_tags_file_path = '%s/%s/index_tags.json' % (working_dir, topic_name)
    if os.path.exists(jobs_tags_file_path):
        file_jobs_tags = open(jobs_tags_file_path, 'r').read()
        file_jobs_tags = json.loads(file_jobs_tags)
    file_jobs_tags.update(jobs_tags)


    with open('%s/%s/index_tags.json' % (working_dir, topic_name), 'w') as f:
        f.write(json.dumps(file_jobs_tags))
