import secrets
import argparse
import os
import shlex
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run AI agent in sandbox")
    _ = parser.add_argument("--engine", default="docker", choices=["docker", "podman"], help="Container engine")
    _ = parser.add_argument("--runtime", default="runsc", help="Container runtime (e.g. runsc, kata)")
    _ = parser.add_argument("--docker", action=argparse.BooleanOptionalAction, help="Enable docker support")
    _ = parser.add_argument("--open-design", action=argparse.BooleanOptionalAction, help="Enable Open Design daemon")
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

    pre_start_script = [
        "echo 'Starting...'",
        "sudo chown nitive:nitive ~/* ~/.* &> /dev/null || true",
        "mise trust --all --yes --silent",
        "mise install --yes",
        "gitleaks detect --no-git --source . -v",
        "echo '{}' > /tmp/empty.json",
    ]

    def add_mcps(path: str):
        pre_start_script.append(f"jq -s 'reduce .[] as $item ({{}}; . * $item)' /opt/mcps/*/mcp_config.json > '{path}'")

    add_mcps(f"{home}/mcp_config.json")

    def configure_jcodemunch():
        pre_start_script.extend(
            [
                "pm2 start /opt/mcps/jcodemunch/.venv/bin/jcodemunch-mcp --name mcp-jcodemunch --interpreter none -- watch-all",
                "pm2 start --no-autorestart /opt/mcps/jcodemunch/.venv/bin/jcodemunch-mcp --name mcp-jcodemunch-initial-index --interpreter none -- index $PWD",
            ]
        )

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
        cmd = ["caveman"] + unknown
        mounts.extend(
            [
                f"{home}/.cave:{home}/.cave",
            ]
        )
        add_mcps(f"{home}/.cave/mcp.json")

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
        "--userns",
        "host",
    ]

    if args.docker:
        args.runtime = "io.containerd.kata.v2"
        docker_cmd.extend(
            [
                "--cpus",
                "4",
                "--memory",
                "12g",
                "--security-opt",
                "seccomp=unconfined",
                "--security-opt",
                "apparmor=unconfined",
                "--security-opt",
                "systempaths=unconfined",
                "--cap-add",
                "ALL",
                "--device",
                "/dev/fuse",
                "--sysctl",
                "net.ipv4.ip_forward=1",
                "-v",
                "/dev/null:/dev/kmsg",
                "-v",
                f"{prefix}-docker:/var/lib/docker",
                "-v",
                "/tmp",
                "--tmpfs",
                "/run",
                "--tmpfs",
                "/var/run",
            ]
        )
        pre_start_script.extend(
            [
                "sudo bash -c 'mount -o remount,rw /sys/fs/cgroup || mount -t cgroup2 none /sys/fs/cgroup'",
                "pm2 start sudo --name docker --interpreter none -- dockerd",
            ]
        )

    if args.open_design:
        pre_start_script.append(
            "pm2 start mise --name open-design --cwd /opt/tools/open-design --interpreter none -- exec node@24 -- node apps/daemon/dist/cli.js --no-open"
        )
        docker_cmd.extend(["--publish", "127.0.0.1:7456:7456"])

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
            "-e",
            f"PROJECT_DIR={pwd}",
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
