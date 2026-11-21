#!/usr/bin/env python3
"""Copy the rendered front page into the grader's output directory.

Stdlib only. The entry image (entry.png) sits next to this file; this
script places an identical copy at <output>/entry.png. It creates the
output directory when missing and clears whatever is already inside it,
but it never removes the output directory itself.
"""
import os
import shutil
import sys


def clear_contents(folder):
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def main(argv):
    out_dir = argv[1] if len(argv) > 1 else "output"
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        raise SystemExit("entry.png not found next to main.py")
    os.makedirs(out_dir, exist_ok=True)
    clear_contents(out_dir)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    print("copied entry.png to", out_dir)


if __name__ == "__main__":
    main(sys.argv)
