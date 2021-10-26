FROM python:3.9

# app requirements
COPY src/requirements.txt /workspace/requirements.txt
RUN python3 -m pip install -r /workspace/requirements.txt

# isntall dev dependencies
COPY requirements-dev.txt /workspace/requirements-dev.txt
RUN python3 -m pip install -r /workspace/requirements-dev.txt
