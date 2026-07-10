FROM ubuntu:26.04 AS base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y \
        build-essential \
        sudo \
        ca-certificates \
        git \
        openssl \
        ripgrep \
        jq \
        yq \
        bash \
        curl \
        wget \
        less \
        vim \
        gettext \
        kitty-terminfo

COPY install-docker.sh /tmp/install-docker.sh
RUN /tmp/install-docker.sh && rm /tmp/install-docker.sh

RUN chown root:root /usr/bin/sudo && chmod 4755 /usr/bin/sudo

ARG USER=agent
ARG USER_ID=1000
ARG GROUP=agent
ARG GROUP_ID=1000
ARG HOME=/home/agent

RUN userdel --remove ubuntu && \
    groupadd \
    --gid $GROUP_ID \
    $GROUP && \
    useradd \
    --create-home \
    --home-dir $HOME \
    --shell /bin/bash \
    --uid $USER_ID \
    --gid $GROUP_ID \
    $USER && \
    usermod -aG docker $USER && \
    echo "$USER ALL=NOPASSWD: ALL" >> /etc/sudoers

USER $USER
WORKDIR $HOME

RUN sudo install -d /usr/share/postgresql-common/pgdg && \
    sudo curl -fsSLo /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc && \
    . /etc/os-release && \
    printf '%s\n' \
    'Types: deb' \
    'URIs: https://apt.postgresql.org/pub/repos/apt' \
    "Suites: ${VERSION_CODENAME}-pgdg" \
    'Components: main' \
    "Architectures: $(dpkg --print-architecture)" \
    'Signed-By: /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc' \
    | sudo tee /etc/apt/sources.list.d/pgdg.sources > /dev/null

RUN sudo apt-get update
RUN sudo apt-get install -y postgresql-18 postgresql-client-18
ENV PATH="/usr/lib/postgresql/18/bin:$PATH"

ENV TOOLS_DIR=/opt/tools
RUN sudo mkdir -p $TOOLS_DIR && sudo chown -R $USER_ID:$GROUP_ID $TOOLS_DIR

ARG MISE_VERSION=latest
RUN curl https://mise.run | MISE_INSTALL_PATH=${TOOLS_DIR}/bin/mise MISE_VERSION=${MISE_VERSION} sh

ENV BASH_ENV=/etc/bash.bashrc
RUN echo 'eval "$(mise activate bash)"' | sudo tee -a /etc/bash-extend.bashrc && \
    echo 'export PATH="$TOOLS_DIR/bin:$TOOLS_DIR/pnpm/bin:$TOOLS_DIR/.mimocode/bin:$HOME/.local/share/pnpm/bin:$PATH"' | sudo tee -a /etc/bash-extend.bashrc && \
    echo 'export PNPM_HOME="$HOME/.local/share/pnpm"' | sudo tee -a /etc/bash-extend.bashrc && \
    echo 'set -o vi' | sudo tee -a /etc/bash-extend.bashrc && \
    echo ". /etc/bash-extend.bashrc\n\n$(cat /etc/bash.bashrc)" | sudo tee /etc/bash.bashrc

RUN wget -qO difft.tar.gz https://github.com/Wilfred/difftastic/releases/latest/download/difft-x86_64-unknown-linux-gnu.tar.gz && \
    sudo tar xf difft.tar.gz -C /usr/local/bin && \
    rm difft.tar.gz

RUN wget -qO delta.deb https://github.com/dandavison/delta/releases/download/0.19.2/git-delta_0.19.2_amd64.deb && \
    sudo dpkg -i delta.deb && \
    rm delta.deb

RUN wget -qO gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz && \
    sudo tar xf gitleaks.tar.gz -C /usr/local/bin gitleaks && \
    rm gitleaks.tar.gz

RUN curl -fsSL https://deb.nodesource.com/setup_26.x | sudo -E bash - && \
    sudo apt-get install -y nodejs && \
    sudo npm install -g corepack

ENV PNPM_HOME="$HOME/.local/share/pnpm"
ENV PATH="$TOOLS_DIR/bin:$TOOLS_DIR/pnpm/bin:$TOOLS_DIR/.mimocode/bin:$HOME/.local/share/pnpm/bin:$PATH"
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0

RUN mkdir -p $TOOLS_DIR/bin && \
    bash -c 'corepack enable --install-directory $TOOLS_DIR/bin'

RUN export dirs="/opt/mise ~/.cave /opt/mcps/jcodemunch $TOOLS_DIR" && \
    sudo mkdir -p $dirs && \
    sudo chown $USER_ID:$GROUP_ID $dirs

ENV PATH="/opt/mise/shims:$PATH"
WORKDIR /opt/mcps/jcodemunch
COPY ./mcps/jcodemunch/ ./
RUN ./install.sh

WORKDIR /opt/mcps/archcore
COPY ./mcps/archcore/ ./
RUN ./install.sh

ARG GEMINI_VERSION=latest \
    CODEX_VERSION=latest \
    CAVEMAN_VERSION=latest \
    MIMO_VERSION=latest \
    HERDR_VERSION=latest

RUN bash -c "PNPM_HOME=$TOOLS_DIR/pnpm pnpm add -g pm2 @openai/codex@${CODEX_VERSION} @google/gemini-cli@${GEMINI_VERSION} @mimo-ai/cli@${MIMO_VERSION} --allow-build '*' && pnpm add -g --config.node-linker=hoisted @juliusbrussee/caveman-code@${CAVEMAN_VERSION} --allow-build '*'"
RUN bash -c 'curl -fsSL https://antigravity.google/cli/install.sh | bash -s -- --dir $TOOLS_DIR/bin'
ENV EDITOR=vim \
    LOCALHOST_HOSTNAME=host.docker.internal \
    UV_PROJECT_ENVIRONMENT=.venv-agent
