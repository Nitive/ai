FROM ubuntu:26.04

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
        less \
        vim \
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

ENV BASH_ENV=$HOME/.bash_profile
RUN echo 'eval "$(mise activate bash)"' >> ~/.bash_profile && \
    echo '[[ -f ~/.bash_profile ]] && source ~/.bash_profile' >> ~/.bashrc

RUN --mount=type=cache,target=$HOME/.cache/mise/,uid=$USER_ID,gid=$GROUP_ID mise use --global node@lts

ENV PNPM_HOME="$HOME/.local/share/pnpm"
ENV PATH="$HOME/.local/bin:$PNPM_HOME/bin:$PATH"
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0

RUN mkdir -p $HOME/.local/bin && \
    bash -c 'corepack enable --install-directory $HOME/.local/bin'

ENV GEMINI_VERSION=latest \
    CODEX_VERSION=latest \
    CAVEMAN_VERSION=latest

RUN bash -c "pnpm add -g @openai/codex@${CODEX_VERSION} @google/gemini-cli@${GEMINI_VERSION} @juliusbrussee/caveman-code@${CAVEMAN_VERSION} --allow-build '*'"
RUN bash -c 'curl -fsSL https://antigravity.google/cli/install.sh | bash'
ENV EDITOR=vim \
    LOCALHOST_HOSTNAME=host.docker.internal
