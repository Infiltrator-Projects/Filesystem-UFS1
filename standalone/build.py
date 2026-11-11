#!/usr/bin/env python3
"""Standalone one-filesystem build adapter, matching the FAT/OFS Python release API."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "standalone/config.json").read_text())
REPO, NAME, PDF, ABI = (CONFIG[k] for k in ("repository", "module", "pdf", "abi"))
PDF = Path(PDF)
KIND = CONFIG["build_system"]
ENGINE = CONFIG.get("backend_revision")
SLUG = REPO.lower()
PACKAGE = "infiltrator-" + SLUG
if (not re.fullmatch(r"Filesystem-[A-Za-z0-9]+", REPO) or
    not re.fullmatch(r"[A-Z0-9]+\.so", NAME) or
    not re.fullmatch(r"docs/[A-Za-z0-9]+\.pdf", PDF.as_posix()) or
    not re.fullmatch(r"infiltrator_filesystem_[a-z0-9_]+", ABI) or
    KIND not in ("cmake", "make") or
    (ENGINE and not re.fullmatch(r"[0-9a-f]{40}", ENGINE))):
    raise RuntimeError("Invalid filesystem build identity")

def run(args):
    subprocess.run([str(x) for x in args], check=True)

def install_deps():
    packages = ("build-essential", "binutils", "cmake", "git", "pkg-config",
                "libssl-dev", "libsqlite3-dev", "dpkg-dev")
    missing = [p for p in packages if subprocess.run(
        ["dpkg-query", "-W", "-f=$" + "{Status}", p], capture_output=True,
        text=True).stdout.strip() != "install ok installed"]
    tools = ("cc", "c++", "make", "cmake", "git", "readelf", "nm",
             "dpkg-deb", "dpkg-query", "pkg-config", "ctest")
    if missing or any(shutil.which(cmd) is None for cmd in tools):
        prefix = [] if os.geteuid() == 0 else ["sudo"]
        apt = [*prefix, "apt-get", "-o", "DPkg::Lock::Timeout=-1"]
        run([*apt, "update"])
        run([*apt, "install", "-y", "--no-install-recommends", *packages])

# The UFS1 driver pins Libraries/Common in CMake. Embed that exact source
# with every RUN so installing UFS1 never fetches external driver source.
COMMON_REVISION = "4c92c8dcd7e03afd4bab3105e143dbabd72c8adc"
COMMON_ROOT = ROOT / "backend-common"

def prepare_release_source():
    if COMMON_ROOT.exists():
        if (COMMON_ROOT / "SOURCE-REVISION").is_file() and (
                COMMON_ROOT / "SOURCE-REVISION").read_text().strip() == COMMON_REVISION:
            return
        raise RuntimeError("Unverified bundled Libraries/Common source")
    run(["git", "clone", "-q", "https://github.com/Infiltrator-Projects/Libraries.git", COMMON_ROOT])
    run(["git", "-C", COMMON_ROOT, "checkout", "-q", COMMON_REVISION])
    revision = subprocess.check_output(["git", "-C", COMMON_ROOT,
                                        "rev-parse", "HEAD"], text=True).strip()
    if revision != COMMON_REVISION:
        raise RuntimeError("Pinned Libraries/Common source revision mismatch")
    (COMMON_ROOT / "SOURCE-REVISION").write_text(COMMON_REVISION + "\n")

def embedded_source_files():
    if not COMMON_ROOT.is_dir() or not (
            COMMON_ROOT / "SOURCE-REVISION").is_file() or (
            COMMON_ROOT / "SOURCE-REVISION").read_text().strip() != COMMON_REVISION:
        raise RuntimeError("Required pinned Libraries/Common source is absent")
    return [p.relative_to(ROOT) for p in COMMON_ROOT.rglob("*") if p.is_file()
            and not p.is_symlink() and
            not {".git", "build", "dist", "__pycache__"}.intersection(p.parts)]

def source_root():
    if not (COMMON_ROOT / "SOURCE-REVISION").is_file() or (
            COMMON_ROOT / "SOURCE-REVISION").read_text().strip() != COMMON_REVISION:
        raise RuntimeError("UFS1 RUN requires embedded pinned Libraries/Common source")
    return ROOT

def dependencies(module):
    symbols = subprocess.check_output(["readelf", "-d", str(module)], text=True)
    libs = set(re.findall(r"Shared library: \[([^\]]+)\]", symbols))
    mapping = {"libc.so.6": None, "libpthread.so.0": None, "libm.so.6": None,
               "ld-linux-x86-64.so.2": None, "libcrypto.so.3": "libssl3t64 | libssl3",
               "libsqlite3.so.0": "libsqlite3-0", "libstdc++.so.6": "libstdc++6",
               "libgcc_s.so.1": "libgcc-s1"}
    if libs - set(mapping):
        raise RuntimeError("Unexpected external filesystem runtime dependencies: " +
                           repr(sorted(libs - set(mapping))))
    return ", ".join(["libc6"] + sorted({mapping[k] for k in libs if mapping[k]}))

def inspect(module):
    if module.name != NAME or not module.is_file() or module.is_symlink():
        raise RuntimeError("Missing correctly named filesystem SO")
    header = subprocess.check_output(["readelf", "-h", str(module)], text=True)
    if "DYN (Shared object file)" not in header or "Advanced Micro Devices X86-64" not in header:
        raise RuntimeError("Not an x86-64 shared object")
    symbols = subprocess.check_output(["nm", "-D", str(module)], text=True)
    if ABI not in [row.split()[-1] for row in symbols.splitlines() if row.split()]:
        raise RuntimeError("Missing exact filesystem ABI " + ABI)
    dependencies(module)

def test(module, workspace=None):
    # CTest / make test are run for every pass by build(); this rechecks the installed bytes.
    inspect(module)

def build(profile, module):
    if profile not in ("portable", "aggressive"):
        raise RuntimeError("Invalid filesystem build profile")
    flags = (["-O2", "-march=x86-64", "-mtune=generic"] if profile == "portable"
             else ["-O3", "-march=native", "-mtune=native", "-flto", "-fprofile-use"])
    module.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=SLUG + "-build-") as temporary:
        dest = Path(temporary) / "build"
        dest.mkdir()
        root = source_root()
        if KIND == "make":
            mk = ["make", "-C", root, "OUT=" + str(dest)]
            base = "-std=c11 -Wall -Wextra -Werror "
            if profile == "portable":
                run([*mk, "CFLAGS=" + base + " ".join(flags), "test"])
            else:
                pg = dest / "profiles"
                pg.mkdir()
                run([*mk, "PROFILE_TRAIN=1", "CFLAGS=" + base +
                     "-O3 -march=native -mtune=native -flto -fprofile-generate=" + str(pg), "test"])
                if not any(p.stat().st_size for p in pg.rglob("*.gcda")):
                    raise RuntimeError("PGO training did not exercise filesystem code")
                for file in (NAME, "ext2-test"):
                    (dest / file).unlink(missing_ok=True)
                run([*mk, "CFLAGS=" + base + "-O3 -march=native -mtune=native -flto " +
                     "-fprofile-use=" + str(pg) + " -fprofile-correction -Wno-missing-profile",
                     "test"])
        else:
            extra = (["-DIFS_EXT_BUILD_LEGACY_MULTIFORMAT_TEST_MODULES=ON"]
                     if ENGINE else [])
            def configure(cflags, ldflags=""):
                run(["cmake", "-S", root, "-B", dest, "-DBUILD_TESTING=ON",
                     "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_C_FLAGS_RELEASE=" + cflags,
                     "-DCMAKE_CXX_FLAGS_RELEASE=" + cflags,
                     "-DCMAKE_SHARED_LINKER_FLAGS=" + ldflags,
                     "-DFETCHCONTENT_SOURCE_DIR_INFILTRATR_COMMON=" + str(COMMON_ROOT),
                     *extra])
            if profile == "portable":
                configure("-O2 -march=x86-64 -mtune=generic -DNDEBUG")
                run(["cmake", "--build", dest, "--parallel", "2"])
                run(["ctest", "--test-dir", dest, "--output-on-failure"])
            else:
                pg = dest / "profiles"
                pg.mkdir()
                base = "-O3 -march=native -mtune=native -flto -DNDEBUG"
                gen = "-fprofile-generate=" + str(pg)
                use = "-fprofile-use=" + str(pg) + " -fprofile-correction -Wno-missing-profile"
                configure(base + " " + gen, gen)
                run(["cmake", "--build", dest, "--parallel", "2"])
                run(["ctest", "--test-dir", dest, "--output-on-failure"])
                if not any(p.is_file() and p.stat().st_size for p in pg.rglob("*.gcda")):
                    raise RuntimeError("No measured PGO data for native filesystem")
                configure(base + " " + use, "-fprofile-use=" + str(pg))
                run(["cmake", "--build", dest, "--clean-first", "--parallel", "2"])
                run(["ctest", "--test-dir", dest, "--output-on-failure"])
        inspect(dest / NAME)
        shutil.copyfile(dest / NAME, module)
        inspect(module)
    return flags

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("portable", "aggressive"), default="portable")
    parser.add_argument("--output", type=Path, default=ROOT / "build" / NAME)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    install_deps()
    flags = build(args.profile, args.output.resolve())
    if args.check:
        test(args.output.resolve())
    print("QUALIFIED", NAME, args.profile, " ".join(flags))

if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"Build failed: {exc}")
