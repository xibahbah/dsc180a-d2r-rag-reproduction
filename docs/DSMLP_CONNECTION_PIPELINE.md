# Our DSMLP connection and reproduction pipeline

This is the actual setup used for Keith's D2R-RAG reproduction, with reusable
commands for teammates. It covers the connections as well as the experiment.
No new GPU job or paid experiment is started by reading this document.

```text
Laptop / local coding assistant
  → shared SSH connection (UCSD login + Duo when required)
  → DSMLP login host
  → course workspace + GPU compute worker
  → project .venv + private OpenAI key file
  → guarded campaign script
  → saved tables, logs, checkpoint and spending ledger
  → GitHub repository and downloadable handoff
```

**Terminal labels matter:** commands below say where to run them. Your Mac's
files, the login host's personal home and the compute worker's course home are
different places. Replace `YOUR_USERNAME` with your own UCSD username. Do not use
Keith's account, SSH socket, API key or completed campaign as your own credentials/run.

## 1. Laptop: create the shared SSH connection

We used an SSH control socket so the authorized local coding assistant could
reuse the login instead of asking for a password on every command.

On a Mac, in Terminal:

```bash
D2R_SOCKET_DIR="$(mktemp -d /private/tmp/dsmlp-team.XXXXXX)"
D2R_SSH_SOCKET="$D2R_SOCKET_DIR/ssh.sock"
printf 'Shared socket path: %s\n' "$D2R_SSH_SOCKET"
ssh -M -S "$D2R_SSH_SOCKET" \
  -o ControlPersist=2h \
  -o ServerAliveInterval=30 \
  YOUR_USERNAME@dsmlp-login.ucsd.edu
```

Complete authentication yourself. Keep this Terminal open during interactive
work. Copy the displayed socket path if another local tool needs it. A second
Terminal does not inherit these shell variables: set `D2R_SSH_SOCKET` there to
the displayed path. Never paste passwords or keys into a chat.

Example read-only command from a second **laptop** Terminal:

```bash
ssh -S "$D2R_SSH_SOCKET" -o BatchMode=yes -o ConnectTimeout=8 \
  YOUR_USERNAME@dsmlp-login.ucsd.edu \
  'bash -lc "kubectl get pods"'
```

`bash -lc` loads the login environment needed by the cluster tools. If the shared
connection expires, authenticate again. Do not repeatedly retry passwords or Duo.
This shared socket connects local tools to SSH; it is not a direct connection to
an arbitrary Jupyter terminal tab.

## 2. Login host: identify the course workspace

```bash
workspace -l
kubectl get pods
```

Our course was `DSC180A_FA26_001`. Keith's project had two views of the same storage:

| Where | Project path |
|---|---|
| Login host | `/dsmlp/workspaces-fs05/DSC180A_FA26_001/home/x4gong/d2r-reproduction` |
| Course compute worker | `/home/x4gong/d2r-reproduction` |

Your username and filesystem may differ. Use the path printed by `workspace -l`.
Our login host's personal `~/d2r-reproduction` contained an older copy. Using it
would have hidden the real results. The `-W` option below selects the course home.

Run Python, package installation and model workloads **inside compute workers**,
not on `dsmlp-login`. See [UCSD launch instructions](https://support.ucsd.edu/services?id=kb_article_view&sysparm_article=KB0032269)
and [workspace/file-transfer instructions](https://support.ucsd.edu/services?id=kb_article_view&sysparm_article=KB0032277).

## 3. Login host: open a worker to prepare the environment

The image used for our completed run was:

```text
ghcr.io/ucsd-ets/scipy-ml-notebook:2025.1-stable
```

Our GPU was a GTX 1080 Ti. This requests the same type of interactive preparation worker:

```bash
launch-scipy-ml.sh \
  -W DSC180A_FA26_001 \
  -i ghcr.io/ucsd-ets/scipy-ml-notebook:2025.1-stable \
  -c 4 -m 16 -g 1 -v 1080ti -s
```

This requests 4 CPU cores, 16 GB RAM and 1 GPU. It may wait for resources.
An interactive worker is for setup, not the unattended batch launch in step 6.
A different paper/model may need another GPU and software stack. Do not assume
this older GPU supports every model-serving or attention library.

## 4. Inside compute: code and Python environment

For a new teammate checkout:

```bash
cd ~
git clone https://github.com/xibahbah/dsc180a-d2r-rag-reproduction.git d2r-reproduction
cd d2r-reproduction
nvidia-smi
python3.11 -m venv .venv
.venv/bin/python -m pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121
.venv/bin/python -m pip install -r requirements-reproduction.txt
.venv/bin/python -m unittest discover -s reproduction -p 'test_*guard.py'
```

Do not clone over an existing project. Our original environment required repairs
for NumPy/PyArrow, PyTorch/torchvision and RAGAS/LangChain compatibility. The repo
now records critical constraints, but a fresh isolated installation still needs
validation. `packages.txt` records the completed environment, not a portable lockfile.

To read saved results without a GPU, environment installation or API key, run:

```bash
python3 scripts/verify_results.py
```

## 5. Inside compute: private API configuration

The GPU handled local embedding/diagnostic models. GPT-4o-mini ran through the
OpenAI API. We trained the LinUCB repair policy, not GPT-4o-mini.

Create your own private file outside the repository:

```bash
mkdir -p ~/.config/d2r-rag
chmod 700 ~/.config/d2r-rag
nano ~/.config/d2r-rag/env.sh
```

The file contains your own key assignment:

```bash
export OPENAI_API_KEY='YOUR_OWN_KEY'
```

Then run:

```bash
chmod 600 ~/.config/d2r-rag/env.sh
source ~/.config/d2r-rag/env.sh
.venv/bin/python reproduction/preflight.py --environment --require-gpu
```

The key file must be in the **course compute home** that the batch worker will
mount. Do not assume the login host's personal `.config` is the same directory.
The launcher sources this file without printing its value.

## 6. Our historical unattended launch

After setup, we launched a background batch worker from the **login host**.
Our final replacement used this command, with Keith's username:

```bash
K8S_TIMEOUT_SECONDS=43200 launch-scipy-ml.sh \
  -W DSC180A_FA26_001 \
  -i ghcr.io/ucsd-ets/scipy-ml-notebook:2025.1-stable \
  -c 4 -m 16 -g 1 -v 1080ti \
  -N d2r-finish -B -- \
  bash /home/x4gong/d2r-reproduction/reproduction/campaign.sh
```

**This is a historical command, not a request to start another experiment.**
It shows how we connected the prepared environment to the background campaign.
A teammate would use their own username, project path, job name and approved run plan.

`-B` queues a noninteractive job. `43200` gives the new worker a 12-hour maximum
runtime. The job runs on DSMLP even if the laptop or SSH connection disconnects.
It can still stop on errors, budget limits or the worker deadline. It is not
unlimited execution. Local assistant monitoring may pause while the laptop sleeps.

Before a batch launch, inspect existing workers and avoid occupying a second GPU
with the preparation worker. Our account allowed only one GPU. Finish/release a
worker deliberately when its work is saved. Never delete a running experiment
just to clear an allocation error.

### Important: the cloned campaign is already complete

The public repo contains the final `.done` markers and `budget.json`.
`campaign.sh` uses that historical campaign directory and skips completed stages.
It is **not a one-command fresh-run template**. Do not delete markers, reset the
ledger or rerun baseline/training in the original campaign.

A fresh experiment needs a separately agreed output directory, script/configuration
and budget before execution. Reusing the connection/setup pattern does not mean
reusing this completed campaign's identity. Other papers also need their own runner.

## 7. Login host: monitor or enter the worker

Use the actual pod name returned at launch:

```bash
kubectl get pods
kubectl logs d2r-finish --tail=20
kubesh d2r-finish
```

The last command enters an **existing** worker. It does not allocate another GPU.
For an authorized tool's noninteractive access, our command was:

```bash
KUBESH_NO_TTY=1 kubesh d2r-finish bash -lc \
  'cd /home/x4gong/d2r-reproduction && cat results/hotpotqa-full-linucb/status.json'
```

That command runs on the login host and executes its inner command in compute.
The historical completed pod may no longer exist. Saved files remain in the
course workspace and GitHub; no worker is needed to read the final repo.

Inside compute, useful read-only checks were:

```bash
cd ~/d2r-reproduction
cat results/hotpotqa-full-linucb/status.json
cat results/hotpotqa-full-linucb/budget.json
ls results/hotpotqa-full-linucb/*.done
```

## 8. What the campaign connected together

```text
Baseline on 500 validation questions
  → two epochs over 500 training questions
  → saved LinUCB checkpoint
  → repair evaluation on 500 validation questions
  → baseline RAGAS metrics
  → repaired RAGAS metrics
```

`campaign.sh` connects the private key file, project `.venv`, `full_run.py`, logs,
stage markers and shared ledger. A lock rejects concurrent copies. The $5 limit
covered all five stages and retries together, not $5 per stage.

`metered_guard.py` reserves before requests and settles verified successful usage.
Failed/unaccounted requests retain their reservation. Our technical attempt ceiling
increased from 10,000 to 50,000 without resetting the request counter or $5 limit.
Stage recovery skips completed stages. An interrupted stage may restart from its
beginning; it does not guarantee per-question or partial-training recovery.

## 9. Handoff and known connection problems

We downloaded logs, plans, tables, environment records and the checkpoint. We
excluded keys, `.venv`, and downloaded model/data/index caches. We compressed the
policy, checked artifacts for secrets and pushed the handoff to GitHub.

| Symptom | What it meant in our run |
|---|---|
| `launch-scipy-ml.sh: command not found` in Jupyter | We were already inside compute; the launcher belongs on the login host. |
| GPU quota exceeded | A running or retained old worker held our one-GPU allocation. |
| Pod Pending / startup timeout | The scheduler could not allocate requested resources. |
| Authentication failed | Shared SSH access needed human reconnection. The batch job did not depend on that SSH session. |
| No result files in personal home | The actual run used the course workspace. |
| API error / request limit | Inspect stage logs and ledger before recovery. Do not reset spending records. |

Start reading the final findings in [REPRODUCTION_SUMMARY.md](REPRODUCTION_SUMMARY.md).
The paper-method workflow is separate: [REPRODUCTION_PIPELINE.md](REPRODUCTION_PIPELINE.md).
