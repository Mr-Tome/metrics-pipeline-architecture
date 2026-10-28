#!/usr/bin/env python3
"""Lists every container image referenced by rendered Kubernetes YAML (helm template output).

Reads YAML on stdin, prints one image reference per line, sorted and unique.

Finds three shapes:
  image: repo/name:tag                       plain pod specs
  {repository: r, image: n, version: v}      NVIDIA ClusterPolicy operands
  {repository: r/n, tag: t}                  common chart values style
Sections with `enabled: false` are skipped, so disabled operands (for example the
GPU Operator driver container when the host driver is used) are not pulled.
"""
import re
import sys

import yaml

REF = re.compile(r"^[a-z0-9][a-z0-9.\-]*(:[0-9]+)?(/[a-z0-9._\-]+)+(:[\w.\-]+|@sha256:[0-9a-f]{64})$")


def walk(node, found):
    if isinstance(node, dict):
        if node.get("enabled") is False:
            return
        repo, img, ver, tag = (node.get(k) for k in ("repository", "image", "version", "tag"))
        if isinstance(repo, str) and isinstance(img, str) and ver:
            found.add(f"{repo.rstrip('/')}/{img}:{ver}")
        elif isinstance(repo, str) and "/" in repo and tag:
            found.add(f"{repo}:{tag}")
        for key, val in node.items():
            if key == "image" and isinstance(val, str) and REF.match(val):
                found.add(val)
            else:
                walk(val, found)
    elif isinstance(node, list):
        for item in node:
            walk(item, found)


def main():
    found = set()
    for doc in yaml.safe_load_all(sys.stdin):
        walk(doc, found)
    for ref in sorted(found):
        print(ref)


if __name__ == "__main__":
    main()
