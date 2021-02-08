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

import dash
import dash_core_components as dcc
import dash_html_components as html

import datetime as dt
import glob
import os
import pandas as pd
import sys


def get_sorted_csv_files(csv_files, topic_name):
    sorted_csv_files = []
    for cf in csv_files:
        cf = cf.split("/", 1)[1]
        date, file_name = cf.split("_", 1)
        sorted_csv_files.append({"date": date, "file_name": file_name})
    sorted_csv_files.sort(
        key=lambda a: dt.datetime.strptime(a["date"], "%Y-%m-%dT%H:%M:%S.%f")
    )  # noqa
    return [
        "%s/%s_%s" % (topic_name, scf["date"], scf["file_name"])
        for scf in sorted_csv_files
    ]  # noqa


def get_jobs_dataset(topic_name):
    csv_files = glob.glob("%s/*" % topic_name)
    sorted_csv_files = get_sorted_csv_files(csv_files, topic_name)
    first_csf_file, csv_files = sorted_csv_files[0], sorted_csv_files[1:]
    abs_path_cf = os.path.abspath(first_csf_file)
    jobs_dataset = pd.read_csv(
        abs_path_cf, delimiter=",", engine="python", index_col="testname"
    )  # noqa

    for cf in csv_files:
        abs_path_cf = os.path.abspath(cf)
        df = pd.read_csv(
            abs_path_cf, delimiter=",", engine="python", index_col="testname"
        )  # noqa
        jobs_dataset = jobs_dataset.merge(df, left_on="testname", right_on="testname")
    return jobs_dataset


def dashit(topic_name, testcase_name):
    job_dataset = get_jobs_dataset(topic_name)
    if testcase_name not in set(job_dataset.index.values):
        print("%s not in topic %s" % (testcase_name, topic_name))
        sys.exit(1)

    testcase_series = job_dataset.loc[testcase_name]
    app = dash.Dash()
    app.layout = html.Div(
        children=[
            html.H1(children="Topic %s" % topic_name),
            dcc.Graph(
                id="dci",
                figure={
                    "data": [
                        {
                            "x": list(testcase_series.keys()),
                            "y": list(testcase_series.values),  # noqa
                            "type": "line",
                            "name": "Testcase",
                        }
                    ],
                    "layout": {"title": "Evolution of %s" % testcase_name},
                },
            ),
        ]
    )
    return app


if __name__ == "__main__":
    app = dashit("RHEL-8.0", "benchTPCDS/TPCDS_Q23_SF10_TPCDS_Q23_cpu time")
    app.run_server(debug=True)
