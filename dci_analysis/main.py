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

from dciclient.v1.api import context

import argparse
import logging
import os
import sys
import traceback

from dci_analysis import analyzer
from dci_analysis import sync_jobs
from dci_analysis import visualization


LOG = logging.getLogger(__name__)

formatter = logging.Formatter('%(levelname)s - %(message)s')
streamhandler = logging.StreamHandler(stream=sys.stdout)
streamhandler.setFormatter(formatter)
LOG.addHandler(streamhandler)
LOG.setLevel(logging.DEBUG)


def sync():
    parser = argparse.ArgumentParser(description='Synchronize jobs locally')

    parser.add_argument('team', type=str, help='The name of the user\'s team')
    parser.add_argument('topic', type=str, help='The name of the topic to pull jobs from')  # noqa
    parser.add_argument('testname', type=str, help='The name of the job\'s test')  # noqa
    args = parser.parse_args(sys.argv[2:])

    if 'DCI_CS_URL' not in os.environ or \
       'DCI_CLIENT_ID' not in os.environ or \
       'DCI_API_SECRET' not in os.environ:
        LOG.info('missing environment variables:\n\tDCI_CS_URL=%s\n '
                 '\tDCI_CLIENT_ID=%s\n\tDCI_API_SECRET=%s' %
                 (os.environ.get('DCI_CS_URL', ''),
                  os.environ.get('DCI_CLIENT_ID', ''),
                  os.environ.get('DCI_API_SECRET', '')))
        sys.exit(1)

    dci_context = context.build_signature_context(
        dci_cs_url=os.environ['DCI_CS_URL'],
        dci_client_id=os.environ['DCI_CLIENT_ID'],
        dci_api_secret=os.environ['DCI_API_SECRET'])

    if not os.path.exists(args.topic):
        LOG.info('create %s/ directory' % args.topic)
        if args.topic == 'RHEL-8' or args.topic == 'RHEL-8-nightly':
            try:
                os.mkdir('RHEL-8.3')
            except:
                pass
        else:
            try:
                os.mkdir(args.topic)
            except:
                pass

    try:
        sync_jobs.sync(dci_context, args.team, args.topic, args.testname)
        LOG.info('done')
    except Exception:
        LOG.error(traceback.format_exc())


def analyze():
    parser = argparse.ArgumentParser(description='Analyze topic\'s jobs')
    parser.add_argument('baseline', type=str, help='The baseline topic')
    parser.add_argument('topic', type=str, help='The topic to compare to')
    args = parser.parse_args(sys.argv[2:])

    for path in ('csv', 'html'):
        if not os.path.exists(path):
            LOG.info('create %s/ directory' % path)
            os.mkdir(path)

    try:
        analyzer.analyze(args.baseline, args.topic)
        LOG.info('done')
    except Exception:
        LOG.error(traceback.format_exc())


def visualize():
    parser = argparse.ArgumentParser(description='Visualize the evolution of a testcase')
    parser.add_argument('topic', type=str, help='The topic')
    parser.add_argument('testcase', type=str, help='The testcase to show')
    args = parser.parse_args(sys.argv[2:])

    try:
        app = visualization.dashit(args.topic, args.testcase)
        app.run_server(debug=True)
    except Exception:
        LOG.error(traceback.format_exc())


_COMMANDS = {
    'sync': sync,
    'analyze': analyze,
    'visualize': visualize
}


def main():
    parser = argparse.ArgumentParser(
        description='DCI Analyzing command line tool')
    parser.add_argument(
        dest='command',
        type=str,
        choices=_COMMANDS.keys(),
        help='Command to run')

    args = parser.parse_args(sys.argv[1:2])
    if args.command not in _COMMANDS.keys():
            print('Unrecognized command')
            parser.print_usage()
            sys.exit(1)

    _COMMANDS[args.command]()
    sys.exit(0)
