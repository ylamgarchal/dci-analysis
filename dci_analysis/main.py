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
from dci_analysis import app
from dci_analysis import sync_jobs


LOG = logging.getLogger(__name__)

formatter = logging.Formatter("%(levelname)s - %(message)s")
streamhandler = logging.StreamHandler(stream=sys.stdout)
streamhandler.setFormatter(formatter)
LOG.addHandler(streamhandler)
LOG.setLevel(logging.DEBUG)

_EXCLUDE_TOPICS = {
    "RHEL-7-nightly",
    "RHEL-7-milestone",
    "RHEL-8-nightly",
    "RHEL-8-milestone",
    "RHEL-9.0",
}


def sync_topic(dci_context, team_name, topic_name, testname, working_dir):
    LOG.info("create %s/%s/ directory" % (working_dir, topic_name))
    os.makedirs("%s/%s" % (working_dir, topic_name), exist_ok=True)

    try:
        sync_jobs.sync(dci_context, team_name, topic_name, testname, working_dir)
        LOG.info("done")
    except Exception:
        LOG.error(traceback.format_exc())


def sync(team, product, topic, testname, working_dir):
    if (
        "DCI_CS_URL" not in os.environ
        or "DCI_CLIENT_ID" not in os.environ
        or "DCI_API_SECRET" not in os.environ
    ):
        LOG.info(
            "missing environment variables:\n\tDCI_CS_URL=%s\n "
            "\tDCI_CLIENT_ID=%s\n\tDCI_API_SECRET=%s"
            % (
                os.environ.get("DCI_CS_URL", ""),
                os.environ.get("DCI_CLIENT_ID", ""),
                os.environ.get("DCI_API_SECRET", ""),
            )
        )
        sys.exit(1)

    dci_context = context.build_signature_context(
        dci_cs_url=os.environ["DCI_CS_URL"],
        dci_client_id=os.environ["DCI_CLIENT_ID"],
        dci_api_secret=os.environ["DCI_API_SECRET"],
    )

    if product is not None:
        product_id = sync_jobs.get_product_id(dci_context, product)
        topics = sync_jobs.get_topics_of_product(dci_context, product_id)
        for topic in topics:
            if topic["name"] not in _EXCLUDE_TOPICS:
                sync_topic(dci_context, team, topic["name"], testname, working_dir)
    elif topic is not None:
        sync_topic(dci_context, team, topic, testname, working_dir)
    else:
        LOG.error("missing --product or --topic option")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="DCI Analyzing command line tool")
    parser.add_argument(
        "--working-dir",
        required=True,
        help="DCI login or 'DCI_LOGIN' environment variable.",
    )

    subparsers = parser.add_subparsers()
    p = subparsers.add_parser("sync", help="sync topics results")
    p.add_argument("team", type=str, help="The name of the user's team")
    p.add_argument("testname", type=str, help="The name of the job's test")  # noqa
    p.add_argument(
        "--product", type=str, help="The name of the product to pull jobs from"
    )  # noqa
    p.add_argument(
        "--topic", type=str, help="The name of the topic to pull jobs from"
    )  # noqa
    p.set_defaults(command="sync")

    p = subparsers.add_parser("dashboard", help="run the dashboard server")
    p.set_defaults(command="dashboard")

    args = parser.parse_args(sys.argv[1:])
    if args.command == "sync":
        sync(args.team, args.product, args.topic, args.testname, args.working_dir)
    elif args.command == "dashboard":
        analyzer.WORKING_DIR = args.working_dir
        app.dashboard.run_server(
            host=os.getenv("DCI_ANALYSIS_HOST", "0.0.0.0"),
            port=os.getenv("DCI_ANALYSIS_PORT", 1234),
            debug=True,
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
