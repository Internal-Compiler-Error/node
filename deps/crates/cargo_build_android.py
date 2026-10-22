#!/usr/bin/env python3

"""Invoke cargo for one GYP toolset when cross-compiling for Android.

GYP cannot set different variable values per toolset, so the host and target
toolsets both run this script with make's $(TOOLSET). Host tools such as
mksnapshot need the crates built for the build machine, while the device
binary needs them built for the Android Rust target. Each toolset gets its own
target directory, and the library ends up at <target_dir>/<profile>/.
"""

import os
import shutil
import subprocess
import sys


def main():
    # Arguments: <toolset> <android_rust_target> <target_dir> [cargo_args...]
    if len(sys.argv) < 4:
        print('Usage: cargo_build_android.py <toolset> <android_rust_target> '
              '<target_dir> [cargo_args...]', file=sys.stderr)
        sys.exit(1)

    toolset, rust_target, target_dir = sys.argv[1:4]
    cargo_args = sys.argv[4:]
    build_profile = 'release' if '--release' in cargo_args else 'debug'
    cargo = os.environ.get('CARGO', 'cargo')

    cmd = [cargo, 'rustc', '--target-dir', target_dir] + cargo_args
    if toolset == 'target':
        cmd += ['--target', rust_target]
    ret = subprocess.call(cmd)
    if ret != 0:
        if toolset == 'target':
            print(f'Building for {rust_target} failed. Is the Rust target '
                  f'installed? Try: rustup target add {rust_target}',
                  file=sys.stderr)
        sys.exit(ret)

    if toolset == 'target':
        # cargo puts cross-compiled output under <target_dir>/<triple>/.
        src = os.path.join(target_dir, rust_target, build_profile,
                           'libnode_crates.a')
        dst = os.path.join(target_dir, build_profile, 'libnode_crates.a')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)


if __name__ == '__main__':
    main()
