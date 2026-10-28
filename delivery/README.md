# delivery/

Builds the release bundle on the connected build workstation. Full guide: [docs/06-software-delivery.md](../docs/06-software-delivery.md).

```
versions.env               every pinned version (the only file to edit for an update)
models.txt                 models to pull
client-requirements.txt    Python packages for analyst machines
lib.sh                     shared helpers

00-check-tools.sh          tools and disk space
01-check-latest.sh         pinned vs upstream versions (read-only)
10-pull-rke2.sh            Kubernetes air-gap artifacts, local-path storage
15-pull-zarf.sh            Zarf CLI and init package
20-build-zarf-package.sh   all charts and images in one Zarf package
30-pull-models.sh          model weights, safetensors only, checksum-verified
40-pull-vuln-db.sh         Trivy and vulnerability databases
50-pull-client-tools.sh    Jupyter AI wheels, VS Code extension
60-pull-nvidia-driver.sh   NVIDIA driver installer
90-seal.sh                 checksums and signature
pull-all.sh                runs all of the above in order

zarf/                      package template, chart values, manifests
tools/                     image scan and template render helpers
intake/verify.sh           receiving side: check the bundle
intake/deploy.sh           receiving side: install, step by step
```

Required tools: curl, jq, tar, sha256sum, python3 with PyYAML, pip, skopeo, helm, and the Hugging Face CLI (`hf`).
`00-check-tools.sh` reports anything missing.

Output goes to `delivery/out/` (git-ignored). Set `BUNDLE_DIR` to write somewhere else.
