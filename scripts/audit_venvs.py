"""Audit the app venvs and kernelspecs on a SEPAL server against the live catalog.

Runs *on* a server -- paste it into a notebook cell in a sandbox, or run it with
python3 there. Read-only: it prints the cleanup commands rather than running them.
Standard library only, so it needs no environment of its own.

This is the inside-the-server counterpart to check_server_apps.py, which asks the
SEPAL API from outside what is deployed. Only the filesystem knows what is still
sitting on disk after an app leaves the catalog, because nothing ever prunes it:
update-app.sh creates and updates, and that is all it does.

Two directories matter, and update-app.sh uses them differently:

    current-kernels/venv-<app>/kernel.json   the kernelspec Jupyter lists
    current-kernels/venv-<app>/venv/         where update_venv moves the built venv
    kernels/venv-<app>/venv/                 where it builds it, and what
                                             kernel.json's argv actually points at

So a venv and the kernelspec that launches it can live in different trees, and
removing one without the other either frees nothing or leaves a broken kernel in
the user's list. Every app is therefore reported with both locations.

Each venv is matched to a catalog entry by the basename of its `repository`,
because that is what app-manager clones into and names the venv after: the venv
`deforest` belongs to the entry `SMFM_deforest_sepal`, which points at
smfm-project/deforest.

Output is deliberately split into separate tables. They call for different
actions, and reading them as one list makes that hard to see.
"""

import datetime
import glob
import json
import os
import re
import socket
import subprocess
import urllib.request

REPO = "dfguerrerom/sepal-apps-catalog"
BRANCH = "main"
CATALOG = None  # set to apps.test.json / apps.prod.json to override the guess

JUPYTER = "/usr/local/share/jupyter"
BUILD = f"{JUPYTER}/kernels"  # where update-app.sh builds
LIVE = f"{JUPYTER}/current-kernels"  # where it moves the result, and writes kernel.json
LOGS = f"{JUPYTER}/log"
APPS = "/var/lib/sepal/app-manager/apps"  # the git clones; same volume as ~/shared/apps

# A conda venv holds hundreds of thousands of files, so `du` on one takes real
# time and thirty of them takes far longer than anyone will wait. Sizes are
# therefore off by default and, when on, measured only for the directories the
# cleanup section actually proposes to delete.
SIZES = False


def sh(*cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def human(n):
    if not n:
        return "-"
    for unit in ("B", "K", "M", "G", "T"):
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.0f}P"


_sizes = {}


def size_of(path):
    if not SIZES or not os.path.isdir(path):
        return 0
    if path not in _sizes:
        out = sh("du", "-sb", path)
        _sizes[path] = int(out.split()[0]) if out and out.split()[0].isdigit() else 0
    return _sizes[path]


def app_size(app):
    return size_of(f"{BUILD}/venv-{app}") + size_of(f"{LIVE}/venv-{app}")


def version_of(venv):
    """Return (version, library). Falls back to dist-info when __version__ is absent.

    spatial-risk-module installs pysepal from a git fork and sepal-gee-bundle
    vendors its own; both report '?' if you only ever read __version__.
    """
    for pkg in ("sepal_ui", "pysepal"):
        hits = glob.glob(f"{venv}/lib/python3.*/site-packages/{pkg}/__init__.py")
        if not hits:
            continue
        text = open(hits[0], errors="replace").read()
        m = re.search(r"""__version__\s*[:=]\s*["']([^"']+)["']""", text)
        if m:
            return m.group(1), pkg
        # Installed from a git URL, or version deferred to importlib.metadata.
        dist = glob.glob(f"{venv}/lib/python3.*/site-packages/{pkg.replace('_', '[-_]')}-*.dist-info")
        if dist:
            name = os.path.basename(dist[0]).removesuffix(".dist-info")
            return name.rsplit("-", 1)[-1], pkg
        return "?", pkg
    return "-", None


def ipyvuetify_of(venv):
    """Return (version, breakage reason). Both ends of the range break sepalwidgets."""
    d = glob.glob(f"{venv}/lib/python3.*/site-packages/ipyvuetify-*.dist-info")
    if not d:
        return "-", None
    iv = os.path.basename(d[0])[len("ipyvuetify-"):-len(".dist-info")]
    mm = tuple(int(x) for x in (re.findall(r"\d+", iv)[:2] or [0, 0]))
    if mm >= (3, 0):
        return iv, "3.x drops CalendarDaily"
    if mm < (1, 8):
        return iv, "< 1.8 has no _version.semver"
    return iv, None


def built_date(venv):
    installed = f"{venv}/.installed"
    if not os.path.exists(installed):
        return "never"
    return datetime.date.fromtimestamp(os.path.getmtime(installed)).isoformat()


def rebuild_failing(app, built):
    """True when the app's yml is newer than the last completed build.

    This is the signal that matters. A venv untouched for months is fine if its
    yml is equally old -- nothing needed rebuilding. Only yml-newer-than-built
    means a rebuild is being attempted and failing, every cycle, in silence.
    """
    yml = f"{APPS}/{app}/sepal_environment.yml"
    if built == "never":
        return os.path.exists(yml)
    if not os.path.exists(yml):
        return False
    return datetime.date.fromtimestamp(os.path.getmtime(yml)).isoformat() > built


def carto_key_in(kernel_json):
    """Hot-patched CARTODB_BASEMAP_KEY, which create_kernel_json silently wipes.

    kernel.json is regenerated from scratch on every venv rebuild, so a key added
    by hand survives only until that app next rebuilds.
    """
    try:
        with open(kernel_json) as f:
            return "CARTODB_BASEMAP_KEY" in json.load(f).get("env", {})
    except (OSError, ValueError):
        return False


def table(title, columns, rows, blurb=None):
    print(f"\n\n{title}  ({len(rows)})")
    if blurb:
        print(blurb)
    if not rows:
        print("  none")
        return
    w = [max(len(str(r[i])) for r in [tuple(columns), *rows]) for i in range(len(columns))]
    print("  " + "  ".join(c.ljust(x) for c, x in zip(columns, w)))
    print("  " + "  ".join("-" * x for x in w))
    for r in rows:
        print("  " + "  ".join(str(v).ljust(x) for v, x in zip(r, w)).rstrip())


# --------------------------------------------------------------------------- catalog

if CATALOG is None:
    CATALOG = "apps.test.json" if "test" in socket.gethostname().lower() else "apps.prod.json"

url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{CATALOG}"
raw = json.loads(urllib.request.urlopen(url, timeout=30).read())
entries = raw if isinstance(raw, list) else raw.get("apps", raw)
catalog = {}
for a in entries:
    if isinstance(a, dict):
        repo = (a.get("repository") or "").rstrip("/").split("/")[-1]
        if repo:
            catalog[repo] = a

# --------------------------------------------------------------------------- scan

# venv-to-remove is the rotation's scratch name, not an app; it is reported
# separately as a stranded directory.
apps = sorted({os.path.basename(d)[5:]
               for root in (BUILD, LIVE)
               for d in glob.glob(f"{root}/venv-*")} - {"to-remove"})

served, leftover, orphan, broken, split, patched = [], [], [], [], [], []

for app in apps:
    build_venv, live_venv = f"{BUILD}/venv-{app}/venv", f"{LIVE}/venv-{app}/venv"
    has_build, has_live = os.path.isdir(build_venv), os.path.isdir(live_venv)
    # Prefer whichever tree actually holds an environment; if both do, the one
    # with the completed-build marker wins, and the pair is reported below.
    venv = live_venv if has_live and os.path.exists(f"{live_venv}/.installed") else (
        build_venv if has_build else live_venv)
    where = "current" if venv == live_venv else "build"

    version, library = version_of(venv)
    iv, why = ipyvuetify_of(venv)
    built = built_date(venv)

    # Deployments disagree on where the kernelspec goes. The current update-app.sh
    # writes it to current-kernels/ while building the venv in kernels/; the image
    # running on prod has no current-kernels/ at all and keeps kernel.json beside
    # the venv. Accept either rather than reporting every app as unregistered.
    kernel_json = next(
        (p for p in (os.path.join(os.path.dirname(venv), "kernel.json"),
                     f"{LIVE}/venv-{app}/kernel.json",
                     f"{BUILD}/venv-{app}/kernel.json") if os.path.exists(p)),
        None)
    has_spec = kernel_json is not None
    if has_spec and carto_key_in(kernel_json):
        patched.append((app, built, "wiped on next rebuild"))
    if has_build and has_live:
        split.append((app, "yes", "yes"))

    entry = catalog.get(app)
    if entry is None:
        orphan.append((app, version, built))
    elif (entry.get("endpoint") or "") == "docker":
        leftover.append((app, version, built))
    else:
        flags = []
        if rebuild_failing(app, built):
            flags.append("REBUILD FAILING")
        if not has_spec:
            flags.append("no kernel.json")
        served.append((app, version, library or "no library", iv, built, where, " ".join(flags)))
    if why:
        broken.append((app, iv, why))

# Measured here and nowhere else: only the directories the cleanup section
# proposes to delete, which is a handful rather than every venv on the server.
reclaim = sum(app_size(r[0]) for r in leftover + orphan)
if SIZES:
    leftover = [r + (human(app_size(r[0])),) for r in leftover]
    orphan = [r + (human(app_size(r[0])),) for r in orphan]
cols = ["app", "version", "built"] + (["size"] if SIZES else [])

# --------------------------------------------------------------------------- report

print(f"host:    {socket.gethostname()}")
print(f"catalog: {CATALOG} @ {BRANCH}  ({len(catalog)} apps with a repository)")
print(f"apps:    {len(apps)} venv dirs")
for label, root in (("build  ", BUILD), ("current", LIVE)):
    if os.path.isdir(root):
        print(f"  {label} {root}  ({len(glob.glob(f'{root}/venv-*'))} entries)")
    else:
        print(f"  {label} {root}  (absent on this deployment)")

table(
    "SERVED — these apps run from this venv",
    ["app", "version", "library", "ipyvuetify", "built", "tree", ""],
    served,
    "  REBUILD FAILING means the app's sepal_environment.yml is newer than the last\n"
    "  completed build: a rebuild is being attempted and failing every cycle. An old\n"
    "  build date on its own is fine -- it just means nothing changed.",
)

table(
    "LEFTOVER — served by app-launcher, this kernel is dead weight",
    cols,
    leftover,
    "  Still in the catalog, so the entry stays; only the venv goes.",
)

table(
    "ORPHAN — no catalog entry at all",
    cols,
    orphan,
    "  Nothing rebuilds these and nothing prunes them: app-manager only creates and\n"
    "  updates. They sit here until someone deletes them by hand.",
)

table(
    "BROKEN NOW — resolved cleanly, raises at import",
    ["app", "ipyvuetify", "why"],
    broken,
    "  These surface as failures nowhere: the environment built fine. The app dies\n"
    "  when a user opens it.",
)

table(
    "IN BOTH TREES — a build copy and a live copy",
    ["app", "in build tree", "in current tree"],
    split,
    "  update-app.sh moves the built venv from kernels/ to current-kernels/, so an\n"
    "  app in both usually means a build copy was stranded. Confirm which one\n"
    "  kernel.json points at before deleting either.",
)

table(
    "HAND-PATCHED kernel.json",
    ["app", "built", "note"],
    patched,
    "  CARTODB_BASEMAP_KEY added by hand. create_kernel_json rewrites kernel.json on\n"
    "  every venv rebuild, so these are temporary by construction -- and a real key\n"
    "  sitting in a world-readable file.",
)

missing = sorted(set(catalog) - set(apps))
table(
    "IN THE CATALOG, NO VENV HERE",
    ["app", "endpoint"],
    [(m, catalog[m].get("endpoint") or "?") for m in missing],
    "  Expected for docker and shiny apps. For a jupyter one it means it has never built.",
)

# Leftovers outside the kernel trees. Nothing prunes these either.
known = set(apps) | set(catalog)
clones = sorted(a for a in (os.listdir(APPS) if os.path.isdir(APPS) else [])
                if a not in catalog and os.path.isdir(f"{APPS}/{a}"))
logs = sorted(os.path.basename(p)[5:-4] for p in glob.glob(f"{LOGS}/venv-*.log")
              if os.path.basename(p)[5:-4] not in known)
table(
    "OUTSIDE THE KERNEL TREES",
    ["kind", "name"] + (["size"] if SIZES else []),
    [("clone", c) + ((human(size_of(f"{APPS}/{c}")),) if SIZES else ()) for c in clones]
    + [("log", l) + (("-",) if SIZES else ()) for l in logs]
    + ([("stranded", "venv-to-remove")
        + ((human(size_of(f"{BUILD}/venv-to-remove")),) if SIZES else ())]
       if os.path.isdir(f"{BUILD}/venv-to-remove") else []),
    "  Clones are full git checkouts of retired apps; update-app.sh never removes one.\n"
    "  venv-to-remove is a whole venv stranded by a crash during the rotation.",
)

# --------------------------------------------------------------------------- cleanup

banner = f"  ({human(reclaim)} reclaimable)" if SIZES else "  (set SIZES = True to measure)"
print(f"\n\nCLEANUP{banner}")
if not (leftover or orphan or clones or logs):
    print("  nothing to remove")
else:
    print("  Review first. Each app needs BOTH trees removed: the venv and the")
    print("  kernelspec that launches it are not in the same directory.\n")
    for app, *_ in leftover + orphan:
        paths = [d for d in (f"{BUILD}/venv-{app}", f"{LIVE}/venv-{app}") if os.path.isdir(d)]
        print(f"  rm -rf {' '.join(paths)}")
    for c in clones:
        print(f"  rm -rf {APPS}/{c}")
    for l in logs:
        print(f"  rm -f  {LOGS}/venv-{l}.log")
