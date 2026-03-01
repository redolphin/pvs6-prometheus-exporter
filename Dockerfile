FROM almalinux:10

RUN python3 -m ensurepip --upgrade
RUN python3 -m pip install pdm

WORKDIR pvs6
COPY pyproject.toml ./
COPY pdm.lock ./
COPY src/ ./src/
RUN pdm install
ENTRYPOINT ["pdm", "run", "python3", "src/pvs6_exporter.py"]