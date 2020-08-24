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

from datetime import datetime as dt
from datetime import timedelta
import glob
import json
import logging
import os
import sys

import numpy
import pandas as pd


LOG = logging.getLogger(__name__)

formatter = logging.Formatter('%(levelname)s - %(message)s')
streamhandler = logging.StreamHandler(stream=sys.stdout)
streamhandler.setFormatter(formatter)
LOG.addHandler(streamhandler)
LOG.setLevel(logging.DEBUG)

WORKING_DIR = os.getenv('DCI_ANALYSIS_WORKING_DIR',
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 


def string_to_date(date):
    if 'T' in date:
        date = date.split('T')[0]
    return dt.strptime(date, '%Y-%m-%d')


def get_sorted_csv_files(csv_files, topic_name):
    sorted_csv_files = []
    for cf in csv_files:
        cf = cf.split('/')[-1]
        date, file_name = cf.split('_', 1)
        sorted_csv_files.append({'date': date, 'file_name': file_name})
    sorted_csv_files.sort(key=lambda a: dt.strptime(a['date'], '%Y-%m-%d'))  # noqa
    return ['%s/%s_%s' % (topic_name, scf['date'], scf['file_name']) for scf in sorted_csv_files]  # noqa


def get_files_between_start_and_end_date(csv_files, start_date, end_date):
    files = []
    for cf in csv_files:
        date = cf.split('/')[-1].split('_')[0]
        date = string_to_date(date)
        if date >= start_date and date <= end_date:
            files.append(cf)
    return files


def filter_by_tags(jobs, topic_name, tags):
    result_jobs = []
    if not tags:
        return jobs
    with open('%s/%s/index_tags.json' % (WORKING_DIR, topic_name), 'r') as f:
        index_tags = f.read()
        index_tags = json.loads(index_tags)
        for job in jobs:
            job = os.path.basename(job)
            if job in index_tags:
                if set(tags).issubset(set(index_tags[job])):
                    result_jobs.append(job)
    return result_jobs


def get_jobs_dataset(topic_name, start_date, end_date, tags, latest_job=False):
    LOG.info('get files files from %s/%s' % (WORKING_DIR, topic_name))
    csv_files = glob.glob('%s/%s/*.csv' % (WORKING_DIR, topic_name))
    csv_files = filter_by_tags(csv_files, topic_name, tags)
    sorted_csv_files = get_sorted_csv_files(csv_files, topic_name)
    sorted_csv_files = get_files_between_start_and_end_date(sorted_csv_files, start_date, end_date)
    if latest_job is True:
        sorted_csv_files = sorted_csv_files[-1:]

    first_csf_file, csv_files = sorted_csv_files[0], sorted_csv_files[1:] if len(sorted_csv_files) > 1 else []
    abs_path_cf = os.path.abspath('%s/%s' % (WORKING_DIR, first_csf_file))
    jobs_dataset = pd.read_csv(abs_path_cf, delimiter=',', engine='python', index_col='testname')  # noqa

    for cf in csv_files:
        abs_path_cf = os.path.abspath('%s/%s' % (WORKING_DIR, cf))
        df = pd.read_csv(abs_path_cf, delimiter=',', engine='python', index_col='testname')  # noqa
        jobs_dataset = jobs_dataset.merge(
            df, left_on='testname', right_on='testname')
    return jobs_dataset


def write_series_csv(file_path, series, header):
    with open(file_path, 'w') as f:
        f.write('%s/%s\n' % (WORKING_DIR, header))
        for tc, time in series.items():
            f.write('%s,%s\n' % (tc, time))


def comparison_with_mean(topic_name_1, topic_name_2, baseline_start_date, baseline_end_date,
                         topic_start_date, topic_end_date, baseline_tags, topic2_tags, topic2_computation=None):
    # compare baseline mean with jobs
    LOG.info('compare the mean of topic %s with jobs of topic %s...' % (topic_name_1, topic_name_2))  # noqa
    baseline_jobs = get_jobs_dataset(topic_name_1, baseline_start_date, baseline_end_date, baseline_tags)
    baseline_jobs_mean = baseline_jobs.mean(axis=1)

    jobs = None
    if topic2_computation is None:
        jobs = get_jobs_dataset(topic_name_2, topic_start_date, topic_end_date, topic2_tags, False)
    elif topic2_computation == 'latest':
        jobs = get_jobs_dataset(topic_name_2, topic_start_date, topic_end_date, topic2_tags, True)
    elif topic2_computation == 'median':
        jobs = get_jobs_dataset(topic_name_2, topic_start_date, topic_end_date, topic2_tags, False)
        jobs = jobs.median(axis=1).to_frame()
    elif topic2_computation == 'mean':
        jobs = get_jobs_dataset(topic_name_2, topic_start_date, topic_end_date, topic2_tags, False)
        jobs = jobs.mean(axis=1).to_frame()

    def delta_mean(lign):
        if lign.name not in baseline_jobs.index.values:
            return "N/A"
        diff = lign - baseline_jobs_mean[lign.name]
        return (diff * 100.0) / baseline_jobs_mean[lign.name]

    compared_jobs = jobs.apply(delta_mean, axis=1)
    csv_file_path = '%s/csv/%s_mean_vs_%s.csv' % (WORKING_DIR, topic_name_1, topic_name_2)
    LOG.info('write file to %s' % csv_file_path)
    compared_jobs.to_csv(csv_file_path, sep=',')

    html_file_path = '%s/html/%s_mean_vs_%s.html' % (WORKING_DIR, topic_name_1, topic_name_2)
    with open(html_file_path, 'w') as f:
        LOG.info('write file to %s' % html_file_path)
        if isinstance(compared_jobs, pd.Series):
            compared_jobs.to_frame().to_html(f, justify='left')
        else:
            compared_jobs.to_html(f, justify='left')
    return compared_jobs


def comparison_with_median(topic_name_1, topic_name_2, baseline_start_date, baseline_end_date,
                           topic_start_date, topic_end_date, baseline_tags, topic2_tags, topic2_computation=None):
    # compare baseline median with jobs
    LOG.info('compare the median of topic %s with jobs of topic %s...' % (topic_name_1, topic_name_2))  # noqa
    baseline_jobs = get_jobs_dataset(topic_name_1, baseline_start_date, baseline_end_date, baseline_tags)
    print('shape baseline jobs: %s,%s' % baseline_jobs.shape)
    baseline_jobs_median = baseline_jobs.median(axis=1)

    jobs = None
    if topic2_computation is None:
        jobs = get_jobs_dataset(topic_name_2, topic_start_date, topic_end_date, topic2_tags, False)
    elif topic2_computation == 'latest':
        jobs = get_jobs_dataset(topic_name_2, topic_start_date, topic_end_date, topic2_tags, True)
    elif topic2_computation == 'median':
        jobs = get_jobs_dataset(topic_name_2, topic_start_date, topic_end_date, topic2_tags, False)
        jobs = jobs.median(axis=1).to_frame()
    elif topic2_computation == 'mean':
        jobs = get_jobs_dataset(topic_name_2, topic_start_date, topic_end_date, topic2_tags, False)
        jobs = jobs.mean(axis=1).to_frame()

    print('shape topic2 jobs: %s,%s' % jobs.shape)
    print('topic2 jobs type %s' % str(type(jobs)))

    def delta_median(lign):
        if lign.name in baseline_jobs.index.values:
            diff = lign - baseline_jobs_median[lign.name]
            return (diff * 100.0) / baseline_jobs_median[lign.name]

    compared_jobs = jobs.apply(delta_median, axis=1)
    csv_file_path = '%s/csv/%s_median_vs_%s.csv' % (WORKING_DIR, topic_name_1, topic_name_2)
    try:
        os.mkdir('%s/csv' % (WORKING_DIR))
    except:
        pass
    LOG.info('write file to %s' % csv_file_path)
    compared_jobs.to_csv(csv_file_path, sep=',')

    html_file_path = '%s/html/%s_median_vs_%s.html' % (WORKING_DIR, topic_name_1, topic_name_2)
    try:
        os.mkdir('%s/html' % (WORKING_DIR))
    except:
        pass
    with open(html_file_path, 'w') as f:
        LOG.info('write file to %s' % html_file_path)
        if isinstance(compared_jobs, pd.Series):
            compared_jobs.to_frame().to_html(f, justify='left')
        else:
            compared_jobs.to_html(f, justify='left')
    return compared_jobs


def analyze(topic_name_1, topic_name_2):
    # compute standard deviation
    for topic_name in (topic_name_1, topic_name_2):
        jobs_dataset = get_jobs_dataset(topic_name)
        # write the evolution
        csv_file_path = '%s/csv/%s_evolution.csv' % (WORKING_DIR, topic_name)
        LOG.info('write file to %s' % csv_file_path)
        jobs_dataset.to_csv(csv_file_path, sep=',')
        html_file_path = '%s/html/%s_evolution.html' % (WORKING_DIR, topic_name)
        with open(html_file_path, 'w') as f:
            LOG.info('write file to %s' % html_file_path)
            jobs_dataset.to_html(f, justify='left')
        # write the standart deviation
        LOG.info('compute standard deviation of %s' % topic_name)
        jobs_std = jobs_dataset.apply(numpy.std, axis=1)
        jobs_std.sort_values(ascending=False, inplace=True)
        csv_file_path = '%s/csv/%s_standard_deviation.csv' % (WORKING_DIR, topic_name)
        LOG.info('write file to %s' % csv_file_path)
        write_series_csv(csv_file_path, jobs_std, 'testname, time')
        html_file_path = '%s/html/%s_standard_deviation.html' % (WORKING_DIR, topic_name)
        with open(html_file_path, 'w') as f:
            LOG.info('write file to %s' % html_file_path)
            jobs_std.to_frame().to_html(f, justify='left')

    comparison_with_mean(topic_name_1, topic_name_2)
    comparison_with_median(topic_name_1, topic_name_2)
