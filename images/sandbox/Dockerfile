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
    echo "$USER ALL=NOPASSWD: ALL" >> /etc/sudoers

USER $USER_ID:$GROUP_ID
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

RUN sudo install -dm 755 /etc/apt/keyrings && \
    curl -fSs https://mise.en.dev/gpg-key.pub | sudo tee /etc/apt/keyrings/mise-archive-keyring.asc 1> /dev/null && \
    echo "deb [signed-by=/etc/apt/keyrings/mise-archive-keyring.asc] https://mise.en.dev/deb stable main" | sudo tee /etc/apt/sources.list.d/mise.list

RUN sudo apt-get update
RUN sudo apt-get install -y postgresql-18 postgresql-client-18 mise
ENV PATH="/usr/lib/postgresql/18/bin:$PATH"

ENV TOOLS_DIR=/opt/tools
RUN sudo mkdir -p $TOOLS_DIR && sudo chown -R $USER_ID:$GROUP_ID $TOOLS_DIR

ENV BASH_ENV=/etc/bash.bashrc
RUN echo 'eval "$(mise activate bash)"' | sudo tee -a /etc/bash.bashrc && \
    echo 'export PATH="$TOOLS_DIR/bin:$TOOLS_DIR/pnpm/bin:$TOOLS_DIR/.mimocode/bin:$HOME/.local/share/pnpm/bin:$PATH"' | sudo tee -a /etc/bash.bashrc && \
    echo 'export PNPM_HOME="$HOME/.local/share/pnpm"' | sudo tee -a /etc/bash.bashrc && \
    echo 'set -o vi' | sudo tee -a /etc/bash.bashrc

RUN wget -qO difft.tar.gz https://github.com/Wilfred/difftastic/releases/latest/download/difft-x86_64-unknown-linux-gnu.tar.gz && \
    sudo tar xf difft.tar.gz -C /usr/local/bin && \
    rm difft.tar.gz

RUN wget -qO delta.deb https://github.com/dandavison/delta/releases/download/0.19.2/git-delta_0.19.2_amd64.deb && \
    sudo dpkg -i delta.deb && \
    rm delta.deb

RUN curl -fsSL https://deb.nodesource.com/setup_26.x | sudo -E bash - && \
    sudo apt-get install -y nodejs && \
    sudo npm install -g corepack

ENV PNPM_HOME="$HOME/.local/share/pnpm"
ENV PATH="$TOOLS_DIR/bin:$TOOLS_DIR/pnpm/bin:$TOOLS_DIR/.mimocode/bin:$HOME/.local/share/pnpm/bin:$PATH"
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0

RUN mkdir -p $TOOLS_DIR/bin && \
    bash -c 'corepack enable --install-directory $TOOLS_DIR/bin'

# Set current user permissions for directory
WORKDIR /opt/mise

ENV PATH="/opt/mise/shims:$PATH"
WORKDIR /opt/mcps/jcodemunch
COPY ./mcps/jcodemunch/ ./
USER root
RUN chown $USER_ID:$GROUP_ID -R ./
USER $USER_ID:$GROUP_ID
RUN ./install.sh

ARG GEMINI_VERSION=latest \
    CODEX_VERSION=latest \
    CAVEMAN_VERSION=latest \
    MIMO_VERSION=latest

RUN bash -c "PNPM_HOME=$TOOLS_DIR/pnpm pnpm add -g pm2 @openai/codex@${CODEX_VERSION} @google/gemini-cli@${GEMINI_VERSION} @juliusbrussee/caveman-code@${CAVEMAN_VERSION} @mimo-ai/cli@${MIMO_VERSION} --allow-build '*'"
RUN bash -c 'curl -fsSL https://antigravity.google/cli/install.sh | bash -s -- --dir $TOOLS_DIR/bin'
ENV EDITOR=vim \
    LOCALHOST_HOSTNAME=host.docker.internal \
    UV_PROJECT_ENVIRONMENT=.venv-agent
