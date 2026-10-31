#!/usr/bin/env python3
"""Small SSH/rsync interface to UCSD's container launcher; no local dependencies."""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def execute(command, dry_run):
    print(shlex.join(command), flush=True)
    if not dry_run:
        subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print commands without connecting")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("connect", "sync", "check", "setup", "status", "fetch"):
        sub.add_parser(name)
    run = sub.add_parser("run")
    run.add_argument("stage", choices=["smoke", "baseline", "train", "repair", "metrics", "metrics-repaired"])
    logs = sub.add_parser("logs")
    logs.add_argument("pod", help="Pod name printed by the launcher/status command")
    args = parser.parse_args()
    config = json.loads((ROOT / "dsmlp.json").read_text())
    host, remote = config["host"], config["remote_dir"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+@[A-Za-z0-9.-]+", host):
        parser.error("Invalid SSH host")
    # Deliberately use a simple folder under the remote home directory.
    if not re.fullmatch(r"[A-Za-z0-9_-]+", remote):
        parser.error("remote_dir must be a single folder name under your home directory")
    ssh = ["ssh", host]
    if args.command == "connect":
        execute(ssh, args.dry_run)
    elif args.command == "sync":
        execute(ssh + [shlex.join(["mkdir", "-p", remote])], args.dry_run)
        execute(["rsync", "-az", "--exclude=.git/", "--exclude=.venv/",
                 "--exclude=__pycache__/", "--exclude=.env", "--exclude=.env.*",
                 "--exclude=secrets/", "--exclude=results/", "--exclude=files_*/",
                 "--exclude=wiki-pages/", "--exclude=*.zip", str(ROOT) + "/",
                 host + ":" + remote + "/"], args.dry_run)
    elif args.command in ("check", "setup", "run"):
        stage = args.stage if args.command == "run" else args.command
        gpu_count = int(config["gpus"]) if stage in ("smoke", "baseline", "train", "repair", "metrics", "metrics-repaired") else 0
        launcher = ["launch-scipy-ml.sh", "-c", str(int(config["cpus"])),
                    "-m", str(int(config["memory_gb"])), "-g", str(gpu_count),
                    "-B", "--", "bash", remote + "/reproduction/job.sh", stage]
        execute(ssh + [shlex.join(launcher)], args.dry_run)
    elif args.command == "status":
        execute(ssh + ["kubectl get pods"], args.dry_run)
    elif args.command == "logs":
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*", args.pod):
            parser.error("Invalid pod name")
        execute(ssh + [shlex.join(["kubectl", "logs", "-f", args.pod])], args.dry_run)
    elif args.command == "fetch":
        execute(["rsync", "-az", host + ":" + remote + "/results/", str(ROOT / "results") + "/"], args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)
