FROM apache/superset
# Switching to root to install the required packages
USER root

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

# Switching back to using the `superset` user
USER superset