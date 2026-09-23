# GH-200 Day 1 cheatsheet

Everything from Day 1 on one page. Keep it open in a second tab.
Every snippet here is valid and copy-pasteable.

A few sections are marked **Day 2**. They are here so the page is complete, and
because you may want them if you finish the capstone early. You do not need them
for today.

---

## The shape of a workflow

```yaml
name: What shows in the Actions tab     # not the file name

on:                                     # what starts it
  pull_request:
    branches: [main]

jobs:                                   # one or more jobs
  build:                                # <- this is the JOB ID, remember it
    runs-on: ubuntu-latest              # which machine
    steps:                              # in order, top to bottom
      - run: echo "hello"
```

The file must live at **`.github/workflows/anything.yml`**. Both parts, plural
on `workflows`. Anywhere else and GitHub never looks at it.

**Two spaces to indent. Never tabs.**

---

## Triggers, the `on:` block

```yaml
on:
  push:
    branches: [main]                    # only pushes to main
  pull_request:
    branches: [main]                    # PRs that target main
  workflow_dispatch:                    # a Run workflow button
  schedule:
    - cron: '0 6 * * *'                 # 06:00 UTC daily, always UTC
```

Shorthand for "every push to any branch", fine for learning, too broad for real
work:

```yaml
on: [push]
```

> The **Run workflow** button only appears once the file is on your **default
> branch**. If it is missing, that is why.

---

## Jobs

### They run in parallel by default

```yaml
jobs:
  one:
    runs-on: ubuntu-latest
    steps:
      - run: echo "A"
  two:                                  # starts at the same time as one
    runs-on: ubuntu-latest
    steps:
      - run: echo "B"
```

### Making one wait

```yaml
jobs:
  two:
    needs: one                          # or needs: [one, other]
```

`needs` controls **when**, not **what is shared**. Each job is a brand new
machine, so files do not travel between jobs. Nothing on disk survives.

### Running the same job several times

```yaml
jobs:
  check:
    strategy:
      fail-fast: false                  # do NOT cancel the others on first red
      matrix:
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}           # <- use the matrix value here
    steps:
      - run: echo "on ${{ matrix.os }}"
```

Each entry becomes its own job, named `check (ubuntu-latest)` and
`check (windows-latest)`. **Remember that name, branch protection needs it.**

---

## Steps: `run` versus `uses`

```yaml
steps:
  - run: echo "a shell command on the runner"

  - name: A readable label            # optional but do it
    run: |
      echo "several"
      echo "lines"

  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
    # ^ somebody else's packaged action, pinned to a commit SHA

  - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97  # v7.0.0
    with:                               # inputs to the action
      python-version: '3.12'
```

> Until `checkout` runs, **none of your files are on the machine.** If your
> script cannot find itself, that is why.

---

## Runners

```yaml
runs-on: ubuntu-latest     # Linux, what you want 95% of the time
runs-on: windows-latest
runs-on: macos-latest
runs-on: ubuntu-24.04      # pin the version when a surprise upgrade would hurt
```

A fresh virtual machine per job, thrown away when the job ends.

---

## Contexts: reading facts inside a workflow
> **Day 2.** Here so you have it, and for the last requirement of the capstone.
> Not something you were taught today, so do not worry if it looks unfamiliar.


Anything inside `${{ }}` is an expression.

| Expression | What you get |
|---|---|
| `${{ github.actor }}` | Who triggered it |
| `${{ github.ref_name }}` | Branch or tag name |
| `${{ github.head_ref }}` | The PR's source branch (only on `pull_request`) |
| `${{ github.sha }}` | The commit |
| `${{ github.repository }}` | `owner/repo` |
| `${{ github.event_name }}` | `push`, `pull_request`, ... |
| `${{ matrix.os }}` | The current matrix value |
| `${{ needs.build.result }}` | Another job's outcome |
| `${{ runner.os }}` | `Linux`, `Windows`, `macOS` |

**A typo evaluates to an empty string and the run carries on.** No error, no
warning. If something prints blank, check your spelling first.

Dump everything to find a field name:

```yaml
- run: echo '${{ toJSON(github) }}'
```

---

## Variables and secrets
> **Day 2.** Here so you have it, and for the last requirement of the capstone.
> Not something you were taught today, so do not worry if it looks unfamiliar.


| | Where you set it | How you read it | In the logs |
|---|---|---|---|
| `env` | In the workflow file | `${{ env.NAME }}` or `$NAME` | shown |
| `vars` | Settings, Secrets and variables | `${{ vars.NAME }}` | **shown, not masked** |
| `secrets` | Settings, Secrets and variables | `${{ secrets.NAME }}` | masked |

```yaml
env:
  GREETING: hello                       # workflow-wide

jobs:
  demo:
    runs-on: ubuntu-latest
    env:
      SCOPE: job-level                  # job-wide
    steps:
      - run: echo "$GREETING from $SCOPE"
```

Only put real credentials in `secrets`. An account ID in `vars` will appear in
plain text in any log you paste into a ticket.

---

## Conditions: `if:`

```yaml
jobs:
  deploy:
    if: ${{ github.ref == 'refs/heads/main' }}
```

**Single quotes for strings.** Double quotes are not valid inside `${{ }}`.

### Status functions
> **Day 2.** Here so you have it, and for the last requirement of the capstone.
> Not something you were taught today, so do not worry if it looks unfamiliar.


| Function | Runs when |
|---|---|
| `success()` | Everything before passed. **This is the invisible default.** |
| `failure()` | Something before failed |
| `always()` | Always, including after a cancel |
| `cancelled()` | The run was cancelled |

```yaml
  report:
    needs: [build, test]
    if: always()                        # runs even when build or test failed
    runs-on: ubuntu-latest
```

> A job with `needs:` and **no** `if:` is **skipped** when its dependency fails.
> That is the default `success()` doing its job. Override it with `if: always()`.

---

## Writing a summary a human can read
> **Day 2.** Here so you have it, and for the last requirement of the capstone.
> Not something you were taught today, so do not worry if it looks unfamiliar.


`$GITHUB_STEP_SUMMARY` is a file. Anything you append renders as Markdown on the
run page.

```yaml
- name: Write the verdict
  run: |
    {
      echo "### Result"
      echo ""
      echo "| Job | Outcome |"
      echo "|---|---|"
      echo "| build | ${{ needs.build.result }} |"
    } >> "$GITHUB_STEP_SUMMARY"
```

**`>>` appends. `>` overwrites.** Use `>` and you will only ever see your last
line.

---

## Pinning actions

```yaml
- uses: actions/checkout@main     # a branch: changes with every commit
- uses: actions/checkout@v7       # a tag: can be MOVED to different code
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
  #                     ^ a commit SHA: cannot change. Use this.
```

To find the SHA: open the action's repo, go to **Releases**, pick the version,
copy the full 40 character hash. Put the version in a trailing comment.

---

## Reading a red run, in order

1. **The red X in the job list** on the left. That names the job that broke.
2. **The annotations** at the top of the run page. GitHub lifts the errors out
   of the log for you.
3. In the log, `Process completed with exit code 1` is the **symptom**. The
   **cause is the line above it**.
4. Only then, read the log properly.

`Set up job` is the step GitHub adds. It lists the runner image and every action
version pulled. Start there when something is mysteriously missing.

---

## Making a check actually block a merge

The workflow **reports**. It does not **enforce**. To stop a merge:

**Settings** → **Rules** or **Branches** → add a rule on `main` → require a
status check to pass.

Two things that catch everybody:

- The name you pick is the **job** name, not the workflow name. From a matrix it
  is `check (ubuntu-latest)`, not `check`.
- The check only appears in that list **after it has run at least once**.

---

## Quick reference: the whole thing

```yaml
name: PR gate

on:
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  facts:
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ github.actor }} on ${{ github.head_ref }}"

  check:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
      - run: echo "checking on ${{ matrix.os }}"

  report:
    needs: [facts, check]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - run: echo "| check | ${{ needs.check.result }} |" >> "$GITHUB_STEP_SUMMARY"
```

---

## When it will not run at all

| Symptom | Cause |
|---|---|
| Nothing happens on push | File is not in `.github/workflows/` |
| Nothing happens on push | `on:` does not match what you did |
| Workflow shows as the file path, not its name | YAML is invalid, or `name:` is missing |
| Run workflow button missing | File is not on your default branch yet |
| No Actions tab at all | Actions is disabled in Settings |
| Weird YAML error you cannot see | A tab character, or odd indentation |


---

# Day 2 additions

The full Day 2 cheatsheet is the last five pages of `GH-200-Day-2-slides.pdf`.
These are the parts people asked about most.

## From a sentence to a file

1. Write the sentence: **when, where, how many, what steps, who enforces**.
2. Draw one box per answer.
3. One key per box: `on`, `runs-on`, `strategy`, `steps`. Box 5 is **Settings, Rules**.
4. Save as `.github/workflows/name.yml` on a branch, open a pull request.
5. Read the run: did it run when, where, and as many times as you expected?

## Passing a value to another job

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      build_id: ${{ steps.build_step.outputs.build_id }}   # 3. the job publishes it
    steps:
      - id: build_step                                       # 2. the step needs an id
        run: echo "build_id=$RANDOM" >> "$GITHUB_OUTPUT"     # 1. the step writes it
  deploy:
    needs: build                                             # 4. needs gives access
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.build_id }}"
```

`build_step` and `build_id` are names **you** chose. GitHub has no idea what a
build ID is. They only have to match where they are set and where they are read.

## Reading a chain

Left to right, like a folder path. At each dot ask "which one?"

| Chain | Say it as |
|---|---|
| `steps.build_step.outputs.build_id` | the step with id build_step, its output build_id |
| `needs.build.outputs.build_id` | the job I need called build, its published output build_id |
| `needs.build.result` | did the job build succeed, fail, or get skipped |
| `matrix.os` | this copy's value of os |
| `github.event.pull_request.title` | the event, the pull request, its title (untrusted text) |

## Two dollar signs

| | `${{ x }}` | `$X` |
|---|---|---|
| Who reads it | GitHub, before the step runs | The shell, while it runs |
| Sees | Contexts: github, steps, needs, vars, secrets | Environment variables |
| Wrong name | Empty string, no error | Empty string, no error |

Untrusted text (titles, branch names, commit messages) goes through `env:` and
is read as `$X`, never pasted into `run:` with `${{ }}`.

## Where to click

| You want to | Go to |
|---|---|
| Add a secret | Settings, Secrets and variables, Actions, New repository secret |
| Add a variable | Same page, Variables tab |
| Gate a deploy on a person | Settings, Environments, New environment, Required reviewers |
| Block red merges | Settings, Rules, New branch ruleset, Require status checks to pass |
| Limit which actions run | Settings, Actions, General |

## Quote these in YAML

`'3.10'` (or it becomes 3.1), cron strings like `'0 2 * * *'`, anything starting
with `*` or `@`.
