# Docker environment for testing Windows package on Mac/Linux
# Uses Wine to run Windows executables

FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install Wine and dependencies
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        wine64 \
        wine32 \
        winbind \
        wget \
        curl \
        xvfb \
        python3 \
        python3-pip \
        procps \
        htop \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up Wine prefix
ENV WINEPREFIX=/root/.wine
ENV WINEARCH=win64
RUN wine wineboot --init

# Install Python packages for testing
RUN pip3 install requests psutil

# Create working directory
WORKDIR /app

# Copy test scripts
COPY test_performance.py /app/
COPY test_packaged.sh /app/

# Make scripts executable
RUN chmod +x /app/test_packaged.sh

# Health check script
COPY healthcheck.sh /app/
RUN chmod +x /app/healthcheck.sh

# Expose ports
EXPOSE 8443 5174

# Default command
CMD ["/bin/bash"]
