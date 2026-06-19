import argparse
import os
import shlex
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run AI agent in sandbox")
    _ = parser.add_argument("--engine", default="docker", choices=["docker", "podman"], help="Container engine")
    _ = parser.add_argument("--runtime", default="runsc", help="Container runtime (e.g. runsc, kata)")
    _ = parser.add_argument(
        "agent", nargs="?", default="bash", help="Agent to run (agy, gemini, codex, caveman) or command"
    )

    args, unknown = parser.parse_known_args()

    home = os.environ.get("HOME", "")
    pwd = os.environ.get("PWD", os.getcwd())

    prefix = pwd.strip("/").replace("/", "-")
    root_dir = Path(__file__).resolve().parent

    mounts = [
        f"{prefix}-home:{home}",
        f"{pwd}:{pwd}",
        f"{prefix}-venv:{pwd}/.venv",
        f"{root_dir}/gitconfig:{home}/.gitconfig:ro",
        f"{home}/.config/git/ignore:{home}/.config/git/ignore:ro",
        f"{home}/.agents:{home}/.agents:ro",
    ]

    mcp_config_paths = ["/opt/mcps/jcodemunch/mcp_config.json"]

    pre_start_script = [
        "echo 'Starting...'",
        "mise trust --all --yes --silent",
        "mise install --yes",
        "echo '{}' > /tmp/empty.json",
        f"jq -s '.[0] * .[1]' /tmp/empty.json {' '.join(mcp_config_paths)} > ~/mcp_config.json",
    ]

    def add_mcps(path: str):
        pre_start_script.append(f"jq -s '.[0] * .[1]' /tmp/empty.json {' '.join(mcp_config_paths)} > '{path}'")

    def configure_jcodemunch():
        pre_start_script.extend([
            "pm2 start /opt/mcps/jcodemunch/.venv/bin/jcodemunch-mcp --name mcp-jcodemunch --interpreter none -- watch-all",
            'echo "jcodemunch-mcp index success: $(/opt/mcps/jcodemunch/.venv/bin/jcodemunch-mcp index $PWD | jq .success)"',
        ])

    if args.agent == "agy":
        cmd = ["agy", "--dangerously-skip-permissions"] + unknown
        mounts.extend(
            [
                f"{home}/.antigravity:{home}/.antigravity",
                f"{home}/.gemini:{home}/.gemini",
                f"{home}/.agents/skills:{home}/.gemini/skills:ro",
            ]
        )
        configure_jcodemunch()
        add_mcps(f"{home}/.gemini/config/mcp_config.json")
        add_mcps(f"{home}/.gemini/antigravity/mcp_config.json")

    elif args.agent == "gemini":
        cmd = ["gemini", "--yolo", "--no-sandbox", "--allowed-mcp-server-names=context7", "--skip-trust"] + unknown
        mounts.extend(
            [
                f"{home}/.gemini:{home}/.gemini",
                f"{home}/.agents/skills:{home}/.gemini/skills:ro",
            ]
        )
        configure_jcodemunch()
        add_mcps(f"{home}/.gemini/config/mcp_config.json")

    elif args.agent == "codex":
        cmd = ["codex", "--sandbox", "danger-full-access", "--ask-for-approval", "on-request"] + unknown
        mounts.extend(
            [
                f"{home}/.codex:{home}/.codex",
                f"{home}/.agents/skills:{home}/.codex/skills:ro",
            ]
        )

    elif args.agent == "caveman":
        cmd = ["caveman", "--caveman-mode", "full"] + unknown
        mounts.extend(
            [
                f"{home}/.cave:{home}/.cave",
            ]
        )

    elif args.agent == "mimo":
        cmd = ["mimo"] + unknown

    else:
        if args.agent == "bash" and not unknown:
            cmd = ["bash"]
        else:
            cmd = [args.agent] + unknown

    cmd_str = " ".join(shlex.quote(c) for c in cmd)

    docker_cmd = [
        args.engine,
        "run",
        "--rm",
        "-it",
        "--userns=host",
    ]

    if args.runtime:
        docker_cmd.extend(["--runtime", args.runtime])

    for m in mounts:
        docker_cmd.extend(["-v", m])

    docker_cmd.extend(
        [
            "-w",
            pwd,
            "-e",
            "TERM=xterm-kitty",
            "--add-host=host.docker.internal:host-gateway",
            "local/sandbox:base",
            "bash",
            "--noprofile",
            "-c",
            " && ".join(
                [
                    *pre_start_script,
                    f"exec bash -c {shlex.quote(cmd_str)}",
                ]
            ),
        ]
    )

    os.execvp(args.engine, docker_cmd)


if __name__ == "__main__":
    main()
