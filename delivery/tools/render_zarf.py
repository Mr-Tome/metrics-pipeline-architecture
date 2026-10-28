#!/usr/bin/env python3
"""Renders zarf/zarf.yaml.in into a concrete zarf.yaml.

usage: render_zarf.py TEMPLATE OUTPUT IMAGES_DIR

${VAR} placeholders are filled from the environment (versions.env is exported
by the caller). A line that is only ${IMAGES_NAME} is replaced by a YAML list of
the images in IMAGES_DIR/NAME.txt, at the same indent. Any unfilled placeholder
is an error, so a typo in versions.env cannot produce a half-rendered package.
"""
import os
import re
import string
import sys

template, output, images_dir = sys.argv[1:4]
out = []
for line in open(template):
    m = re.fullmatch(r"(\s*)\$\{IMAGES_([A-Z0-9_]+)\}\s*", line)
    if m:
        indent, name = m.groups()
        path = os.path.join(images_dir, name + ".txt")
        refs = [r.strip() for r in open(path) if r.strip() and not r.startswith("#")]
        if not refs:
            sys.exit(f"no images listed in {path}")
        out.extend(f'{indent}- "{r}"\n' for r in refs)
    else:
        out.append(string.Template(line).safe_substitute(os.environ))

text = "".join(out)
left = re.findall(r"\$\{[A-Z0-9_]+\}", text)
if left:
    sys.exit(f"unfilled placeholders in {template}: {sorted(set(left))}")
with open(output, "w") as f:
    f.write(text)
