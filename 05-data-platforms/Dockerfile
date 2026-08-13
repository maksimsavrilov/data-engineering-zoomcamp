FROM ghcr.io/bruin-data/bruin:v0.11.712

USER root
EXPOSE 22

RUN mkdir -p /var/lib/apt/lists && apt-get update && apt-get install -y \
    openssh-server \
    vim \
    sudo \
    lsof
#    && rm -rf /var/lib/apt/lists/*

RUN usermod -aG sudo bruin && \
    mkdir -p /run/sshd && mkdir /workspace && chown -R bruin:bruin /workspace

CMD ["/usr/sbin/sshd", "-D", "-e"]
