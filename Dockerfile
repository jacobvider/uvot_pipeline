FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
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

# Install Miniconda
RUN curl -fsSL \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    -o /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

ENV PATH="/opt/conda/bin:${PATH}"

WORKDIR /app

# Create the Python environment
COPY environment.yml .

# Configure Conda to use only conda-forge
RUN printf 'channels:\n  - conda-forge\ndefault_channels: []\nchannel_priority: strict\n' > /opt/conda/.condarc && \
    conda env create -f environment.yml && \
    conda clean -afy

ENV PATH="/opt/conda/envs/uvot/bin:${PATH}"

# Copy pipeline code
COPY . .

# Configure existing HEASoft installation
ENV HEADAS="/home/jacob/heasoft-6.36/x86_64-pc-linux-gnu-libc2.39"
ENV LHEAPERL="/usr/bin/perl"
ENV PERL5LIB="/home/jacob/heasoft-6.36/lib/perl"
ENV LD_LIBRARY_PATH="/home/jacob/heasoft-6.36/lib"
ENV PYTHONPATH="/home/jacob/heasoft-6.36/x86_64-pc-linux-gnu-libc2.39/lib/python"
ENV PFILES="/tmp/pfiles;/home/jacob/heasoft-6.36/syspfiles"
ENV CALDB="/caldb"

ENV PATH="/home/jacob/heasoft-6.36/bin:${PATH}"

RUN mkdir -p /tmp/pfiles /data/reference /results /work/input

ENTRYPOINT ["python", "-u", "main.py"]