#!/usr/bin/env bash
# Scans every image in the Zarf package for known vulnerabilities, with the Trivy database pulled by
# 40-pull-vuln-db.sh, and puts the reports in the bundle (scanner/reports/).
#
#   SUMMARY.txt        one line per image: critical, high, medium, low counts
#   IMAGE-DIGESTS.txt  the digest of each image as scanned
#   <image>.json       full Trivy report
#
# Findings do not stop the build. Review SUMMARY.txt (and the ISSM, if required) before sealing.
# Trivy reads the images from their upstream registries by the same tags Zarf packaged in step 20,
# so run this right after step 20; IMAGE-DIGESTS.txt records exactly what was scanned.
source "$(dirname "$0")/lib.sh"
require python3

trivy="${BUNDLE_DIR}/scanner/bin/trivy"
cache="${BUNDLE_DIR}/scanner/trivy-cache"
images="${BUNDLE_DIR}/package/IMAGES.txt"
[[ -x "${trivy}" ]] || die "no trivy in the bundle; run 40-pull-vuln-db.sh first"
[[ -s "${images}" ]] || die "no package/IMAGES.txt; run 20-build-zarf-package.sh first"

out="${BUNDLE_DIR}/scanner/reports"
rm -rf "${out}"
mkdir -p "${out}"
while read -r ref; do
    [[ -n "${ref}" ]] || continue
    log "scanning ${ref}"
    "${trivy}" image --quiet --scanners vuln --platform "linux/${ARCH}" \
        --skip-db-update --skip-java-db-update --cache-dir "${cache}" \
        --format json --output "${out}/$(tr '/:@' '___' <<<"${ref}").json" "${ref}"
done < "${images}"
# Trivy caches image layer analysis next to its database. Keep the bundle to the database only.
rm -rf "${cache}/fanal"

python3 - "${out}" <<'EOF'
import glob, json, os, sys
out = sys.argv[1]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
rows, digests = [], []
for path in sorted(glob.glob(os.path.join(out, "*.json"))):
    report = json.load(open(path))
    name = report.get("ArtifactName", os.path.basename(path))
    counts = dict.fromkeys(levels, 0)
    for result in report.get("Results") or []:
        for vuln in result.get("Vulnerabilities") or []:
            if vuln.get("Severity") in counts:
                counts[vuln["Severity"]] += 1
    rows.append(f"{counts['CRITICAL']:>8} {counts['HIGH']:>6} {counts['MEDIUM']:>6} {counts['LOW']:>6}  {name}")
    for digest in (report.get("Metadata") or {}).get("RepoDigests") or [name + " (no digest reported)"]:
        digests.append(digest)
with open(os.path.join(out, "SUMMARY.txt"), "w") as f:
    f.write(f"{'CRITICAL':>8} {'HIGH':>6} {'MEDIUM':>6} {'LOW':>6}  IMAGE\n" + "\n".join(rows) + "\n")
with open(os.path.join(out, "IMAGE-DIGESTS.txt"), "w") as f:
    f.write("\n".join(sorted(set(digests))) + "\n")
print(open(os.path.join(out, "SUMMARY.txt")).read())
EOF

manifest scan "$(wc -l < "${images}") images scanned $(date -u +%Y-%m-%dT%H:%MZ), see scanner/reports/SUMMARY.txt"
log "scan reports in ${out}. Review SUMMARY.txt before sealing."
