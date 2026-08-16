FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Lean 4 via elan, pinned to the ten-proofs toolchain.
ENV ELAN_HOME=/root/.elan
ENV PATH="${ELAN_HOME}/bin:${PATH}"
RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf \
    | sh -s -- -y --default-toolchain leanprover/lean4:v4.32.0

WORKDIR /work
COPY requirements.txt pyproject.toml ./
RUN python -m pip install --no-cache-dir -U pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .
# lake update / cache get are left to runtime so the image stays smaller.
CMD ["bash"]
