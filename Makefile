export SANDBOX_IMAGE := local/sandbox

build-sandbox:
	@ docker build ./images/sandbox/ -f images/sandbox/Dockerfile \
	  --build-arg GEMINI_VERSION=$(shell pnpm info @google/gemini-cli --json | jq -r .version) \
	  --build-arg CODEX_VERSION=$(shell pnpm info @openai/codex --json | jq -r .version) \
	  --build-arg CAVEMAN_VERSION=$(shell pnpm info @juliusbrussee/caveman-code --json | jq -r .version) \
	  --build-arg MIMO_VERSION=$(shell pnpm info @mimo-ai/cli --json | jq -r .version) \
	  --build-arg MISE_VERSION=$(shell mise version --json | jq -r .latest) \
	  --build-arg ARCHCORE_VERSION=$(shell mise latest github:archcore-ai/cli) \
	  --build-arg HOME=$$HOME \
	  --build-arg PWD=$$PWD \
	  --build-arg USER=$(shell id -un) \
	  --build-arg GROUP=$(shell id -gn) \
	  --build-arg USER_ID=$(shell id -u) \
	  --build-arg GROUP_ID=$(shell id -g) \
	  --target $(target) \
	  -t $(SANDBOX_IMAGE):$(target)

build-all:
	make build-sandbox target=base

test-sandbox:
	make build-sandbox target=base
	./scripts/agent.sh bash

test-sandbox-plain-bash:
	make build-sandbox target=base
	docker run -it --rm $(SANDBOX_IMAGE):base bash
