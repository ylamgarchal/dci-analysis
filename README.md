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

## Synchronization

### run the synchronization

First, get your remoteci credentials from the DCI dashboard.

```console
[yassine@Bouceka dci-analysis]$ source ~/dci/my-remoteci.rc.sh
```

Synchronize all the jobs of a topic from the server to your local storage.

```console
[yassine@Bouceka dci-analysis]$ dci-analysis --workding-dir=/tmp sync --topic=TOPIC TEAM Testname
```

This command will create a TOPIC/ directory, in the 'working-dir' path, with all the Testname
tests from the jobs that belongs to the team TEAM, in csv format.

Synchronize all the jobs of a product from the server to your local storage.

```console
[yassine@Bouceka dci-analysis]$ dci-analysis --working-dir=/tmp sync --product=PRODUCT TEAM Testname
```

This command will loop over each topic of the product to pull the jobs from.

### run the synchronization with a Systemd timer on RHEL/Centos

Assuming the repo has been cloned at /opt/dci-analysis.

Fill the systemd/remoteci.env file with the remoteci credentials and the parameters to the sync command.

Update the file systemd/dci-analysis-sync.service with the correct User and Group value.

Copy the files systemd/* to /etc/systemd/system/ and reload:

```console
[yassine@Bouceka dci-analysis]$ sudo cp systemd/* /etc/systemd/system
[yassine@Bouceka dci-analysis]$ sudo systemctl daemon-reload
```

Start the service and enable the timer:

```console
[yassine@Bouceka dci-analysis]$ sudo systemctl start dci-analysis-sync.service
[yassine@Bouceka dci-analysis]$ sudo systemctl enable dci-analysis-sync.timer
```

Finally, run the dashboard.

## Dashboard

### run the dashboard

```console
[yassine@Bouceka dci-analysis]$ export DCI_ANALYSIS_PORT=1234
[yassine@Bouceka dci-analysis]$ export DCI_ANALYSIS_HOST=0.0.0.0
[yassine@Bouceka dci-analysis]$ $ dci-analysis --working-dir=/tmp dashboard
Running on http://0.0.0.0:1234/
Debugger PIN: 854-961-740
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
Running on http://0.0.0.0:1234/
Debugger PIN: 178-967-504
```

Then fo to http://127.0.0.1:1234 to visit the dashboard page

### run the dashboard with Podman:

```console
[yassine@Bouceka dci-analysis]$ sudo setenforce 0
[yassine@Bouceka dci-analysis]$ podman build -t dci-analysis ./
[yassine@Bouceka dci-analysis]$ podman run -p 1234:1234 -v /home/yassine/dci/dci-analysis:/opt/dci-analysis -it localhost/dci-analysis
```

With "/home/yassine/dci/dci-analysis" the directory with dci-analysis code.
