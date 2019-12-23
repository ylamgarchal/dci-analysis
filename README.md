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

This command will create a TOPIC/ directory with all the jobs tests in csv format.

Finally, run the analyzer.

```console
[yassine@Bouceka dci-analysis]$ dci-analyze analyze TOPIC_BASELINE TOPIC
```
This will create several results in csv format:

    - RHEL-8.0_mean_vs_RHEL-8.1.csv
    - RHEL-8.0_median_vs_RHEL-8.1.csv
    - RHEL-8.0_standard_deviation.csv
    - RHEL-8.1_standard_deviation.csv

## Example

```console
[yassine@Bouceka dci-analysis]$ source ~/dci/my-remoteci.rc.sh
[yassine@Bouceka dci-analysis]$ dci-analyze sync MyTeam RHEL-8.0 Performance
[yassine@Bouceka dci-analysis]$ dci-analyze sync MyTeam RHEL-8.1 Performance
[yassine@Bouceka dci-analysis]$ dci-analyze analyze RHEL-8.0 RHEL-8.1
```

## Reading results with Jupyter

### Install and run Jupyter

```console
[yassine@Bouceka dci-analysis]$ pip install jupyter
[yassine@Bouceka dci-analysis]$ jupyter notebook
```

After this command your browser should be open with the Jupyter page. Click on
"new" and select your python interpeter to create a new notebook.

### Read the results

```python
import pandas

rhel_80_deviation = pandas.read_csv('RHEL-8.0_standard_deviation.csv', delimiter='!', engine='python')
```

This will read the csv file, press shift + enter to validate the statement code.

### Show the results

```python
rhel_80_deviation
```

Simply read the variable and press shift + enter to show the results.
