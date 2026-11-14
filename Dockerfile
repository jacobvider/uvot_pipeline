FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        bash \
        perl \
        libcurl4t64 \
        libreadline8t64 \
        libx11-6 \
        libgfortran5 \
        libpng16-16t64 \
        ca-certificates \
        curl \
        bzip2 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    -o /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

ENV PATH="/opt/conda/bin:${PATH}"

WORKDIR /app

COPY environment.yml .

RUN printf 'channels:\n  - conda-forge\ndefault_channels: []\nchannel_priority: strict\n' > /opt/conda/.condarc && \
    conda env create -f environment.yml && \
    conda clean -afy

ENV PATH="/opt/conda/envs/uvot/bin:${PATH}"

COPY . .

ENV HEADAS="/opt/heasoft"
ENV LHEAPERL="/usr/bin/perl"
ENV PERL5LIB="${HEADAS}/x86_64-pc-linux-gnu-libc2.39/lib/perl"
ENV LD_LIBRARY_PATH="${HEADAS}/x86_64-pc-linux-gnu-libc2.39/lib"
ENV PYTHONPATH="${HEADAS}/x86_64-pc-linux-gnu-libc2.39/lib/python"
ENV PFILES="/tmp/pfiles;${HEADAS}/x86_64-pc-linux-gnu-libc2.39/syspfiles"
ENV CALDB="/caldb"

ENV PATH="${HEADAS}/x86_64-pc-linux-gnu-libc2.39/bin:${PATH}"
ENV HEADASNOQUERY=1

RUN mkdir -p /tmp/pfiles /data/reference /results /work/input /opt/heasoft

ENTRYPOINT ["python", "-u", "main.py"]