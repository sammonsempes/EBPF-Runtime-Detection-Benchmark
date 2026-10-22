FROM ubuntu:24.04 AS workloads

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev make \
    && rm -rf /var/lib/apt/lists/*

COPY workloads/ /src/workloads/
RUN make -C /src/workloads CC=gcc BINDIR=/out


FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        coreutils \
        cron \
        curl \
        findutils \
        gcc \
        gzip \
        iproute2 \
        kmod \
        libc6-dev \
        libcap2-bin \
        logrotate \
        make \
        netcat-openbsd \
        openssh-client \
        passwd \
        procps \
        python3 \
        tar \
        util-linux

COPY --from=workloads /out/ /opt/bench/bin/

COPY victim/honey/aws-credentials /root/.aws/credentials
COPY victim/honey/authorized_keys /root/.ssh/authorized_keys
COPY victim/honey/bash_history /root/.bash_history
COPY victim/honey/app.env /opt/app/.env
COPY victim/honey/serviceaccount-token /var/run/secrets/kubernetes.io/serviceaccount/token
COPY victim/honey/auth.log /var/log/auth.log

RUN printf '%s\n' \
        '-----BEGIN OPENSSH PRIVATE KEY-----' \
        'YmVuY2ggaG9uZXkgZmlsZSwgdGhpcyBpcyBub3QgYSByZWFsIHByaXZhdGUga2V5Lg==' \
        '-----END OPENSSH PRIVATE KEY-----' > /root/.ssh/id_rsa \
    && chmod 700 /root/.ssh /root/.aws \
    && chmod 600 /root/.ssh/id_rsa /root/.ssh/authorized_keys /root/.aws/credentials /root/.bash_history /opt/app/.env \
    && chmod 640 /var/log/auth.log \
    && mkdir -p /etc/cron.d /etc/systemd/system /backup

COPY scenarios/ /scenarios/

WORKDIR /root

CMD ["sleep", "infinity"]
