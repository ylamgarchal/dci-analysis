FROM centos:7

LABEL name="DCI Analysis Dashboard" version="0.0.1"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

RUN mkdir /opt/dci-analysis
COPY requirements.txt /tmp/requirements.txt

RUN yum -y install epel-release && \
    yum -y install git \
    python36 python36-devel python36-pip python36-setuptools && \
    yum clean all && \
    pip3 install --no-cache-dir -U pip && \
    pip3 install --no-cache-dir -U tox && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt

ENV PYTHONPATH /opt/dci-analysis

EXPOSE 1234

CMD ["python3", "/opt/dci-analysis/dci_analysis/main.py", "--working-dir=/opt/dci-analysis", "dashboard"]
