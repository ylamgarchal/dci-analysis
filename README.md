# Distributed CI Analysis

DCI analysis is a [Pandas](https://pandas.pydata.org) based tool that will retrieve the folowing information
from the jobs tests:

    - Compute the mean of a baseline topic and compare the result to another topic.
    - Compute the median of a baseline topic and compare the result to another topic.
    - Compute the standard deviation of each topic.


## Installation

### Install dependencies

```console
[yassine@Bouceka dci-analysis]$ pip install -r requirements.txt
```

### Install code

```console
[yassine@Bouceka dci-analysis]$ pip install --user ./
```

## Usage

First, get your remoteci credentials from the DCI dashboard.

```console
[yassine@Bouceka dci-analysis]$ source ~/dci/my-remoteci.rc.sh
```

Synchronize all the jobs from the server to your local storage.

```console
[yassine@Bouceka dci-analysis]$ dci-analyze sync TEAM TOPIC Testname
```

This command will create a TOPIC/ directory with all the Testname tests from the jobs
that belongs to the team TEAM, in csv format.

Finally, run the analyzer.

```console
[yassine@Bouceka dci-analysis]$ dci-analyze analyze TOPIC_BASELINE TOPIC
```
This will create several results in csv format:

    - RHEL-8.0_mean_vs_RHEL-8.1.csv
      * compute the mean of the baseline topic and print the delta with the latter topic.
    - RHEL-8.0_median_vs_RHEL-8.1.csv
      * compute the median of the baseline topic and print the delta with the latter topic.
    - RHEL-8.0_standard_deviation.csv
      * compute the standard deviation of every tests cases of the topic
    - RHEL-8.1_standard_deviation.csv
      * compute the standard deviation of every tests cases of the topic

## Example

```console
[yassine@Bouceka dci-analysis]$ source ~/dci/my-remoteci.rc.sh
[yassine@Bouceka dci-analysis]$ dci-analyze sync MyTeam RHEL-8.0 Performance
[yassine@Bouceka dci-analysis]$ dci-analyze sync MyTeam RHEL-8.1 Performance
[yassine@Bouceka dci-analysis]$ dci-analyze analyze RHEL-8.0 RHEL-8.1
INFO - create csv/ directory
INFO - create html/ directory
INFO - compute standard deviation of RHEL-8.0
INFO - write file to csv/RHEL-8.0_standard_deviation.csv
INFO - write file to html/RHEL-8.0_standard_deviation.html
INFO - compute standard deviation of RHEL-8.1
INFO - write file to csv/RHEL-8.1_standard_deviation.csv
INFO - write file to html/RHEL-8.1_standard_deviation.html
INFO - compare the mean of topic RHEL-8.0 with jobs of topic RHEL-8.1...
INFO - write file to csv/RHEL-8.0_mean_vs_RHEL-8.1.csv
INFO - write file to html/RHEL-8.0_mean_vs_RHEL-8.1.html
INFO - compare the median of topic RHEL-8.0 with jobs of topic RHEL-8.1...
INFO - write file to csv/RHEL-8.0_median_vs_RHEL-8.1.csv
INFO - write file to html/RHEL-8.0_median_vs_RHEL-8.1.html
INFO - done
```

## Reading results

Results are available in csv/ and html/ directories.

## Dashboard

To run the dash type the following:

```console
[yassine@Bouceka dci-analysis]$ python dashboard/app.py
Running on http://127.0.0.1:8050/
Debugger PIN: 854-961-740
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
Running on http://127.0.0.1:8050/
Debugger PIN: 178-967-504
```

Then fo to http://127.0.0.1:8050 to visit the dashboard page
