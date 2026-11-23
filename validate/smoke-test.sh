#!/usr/bin/env bash
# Checks that the installed SI service works, not just that pods run. Prints PASS or FAIL per check and exits
# non-zero if anything failed. Check IDs match the sandbox bring-up plan, section 4. Run as root on the first
# server (where kubectl works), after deploy.sh gateway-key (and, in staging, after the add-on):
#
#   ./smoke-test.sh /srv/si/bundle
#
# Covers C1, C2, C3, C5, C7, C8, C10, C10b, C16 (this node only), plus a chat answer through the gateway,
# streamed and not. The chat page checks (C11, C11b) are done by hand in a browser.
set -uo pipefail
bundle="${1:?usage: smoke-test.sh BUNDLE_DIR}"
export PATH="/var/lib/rancher/rke2/bin:${PATH}" KUBECONFIG=/etc/rancher/rke2/rke2.yaml
[[ ${EUID} -eq 0 ]] || { echo "run as root"; exit 2; }
# shellcheck source=/dev/null
source "${bundle}/VERSIONS.env"

fails=0
pass() { printf 'PASS  %-5s %s\n' "$1" "$2"; }
fail() { printf 'FAIL  %-5s %s\n' "$1" "$2"; fails=$((fails + 1)); }
gw=http://127.0.0.1:14000

kubectl -n si port-forward svc/litellm 14000:4000 >/dev/null 2>&1 &
pf=$!
tmp=$(mktemp -d)
trap 'kill ${pf} 2>/dev/null; rm -rf "${tmp}"' EXIT
for _ in $(seq 30); do curl -fsS -o /dev/null "${gw}/health/liveliness" && break; sleep 1; done
mk=$(kubectl -n si get secret litellm-masterkey -o jsonpath='{.data.masterkey}' | base64 -d)

# C1: every pod Running or Completed
notok=$(kubectl get pods -A --no-headers | awk '$4 != "Running" && $4 != "Completed" {print $1 "/" $2 " " $4}')
[[ -z "${notok}" ]] && pass C1 "all pods Running or Completed" || fail C1 "pods not running:"$'\n'"${notok}"

# C2: every packaged image is in the Zarf registry
catalog=$(cd "${bundle}/zarf" && ./zarf tools registry catalog 2>/dev/null)
missing=""
while read -r img; do
    [[ -z "${img}" ]] && continue
    path="${img%%@*}"; path="${path%:*}"; path="${path#*/}"   # drop digest, tag, and registry host
    grep -q "${path}" <<<"${catalog}" || missing+=" ${img}"
done < "${bundle}/package/IMAGES.txt"
[[ -n "${catalog}" && -z "${missing}" ]] && pass C2 "$(wc -l < "${bundle}/package/IMAGES.txt") images in the registry" \
    || fail C2 "not in the registry:${missing:- (could not read the catalog)}"

# C3: the real vLLM image loads gpt-oss's tokenizer and vocabulary with no network (no GPU needed)
read -r -d '' c3py <<'PY'
from transformers import AutoTokenizer
from openai_harmony import load_harmony_encoding, HarmonyEncodingName
AutoTokenizer.from_pretrained("/models/gpt-oss-120b")
load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
print("C3-OK")
PY
overrides=$(python3 - "${VLLM_IMAGE}" "${c3py}" <<'PY'
import json, sys
print(json.dumps({"spec": {
    "nodeSelector": {"node-role.si/models": "true"},
    "containers": [{"name": "smoke-c3", "image": sys.argv[1], "command": ["python3", "-c", sys.argv[2]],
        "env": [{"name": "HF_HUB_OFFLINE", "value": "1"},
                {"name": "TIKTOKEN_ENCODINGS_BASE", "value": "/models/tiktoken"}],
        "volumeMounts": [{"name": "models", "mountPath": "/models", "readOnly": True}]}],
    "volumes": [{"name": "models", "hostPath": {"path": "/var/lib/models", "type": "Directory"}}]}}))
PY
)
kubectl -n si delete pod smoke-c3 --ignore-not-found >/dev/null 2>&1
out=$(timeout 1200 kubectl -n si run smoke-c3 --rm -i --restart=Never --quiet --image="${VLLM_IMAGE}" \
      --overrides="${overrides}" 2>&1)
grep -q C3-OK <<<"${out}" && pass C3 "vLLM image loads the tokenizer and vocabulary offline" \
    || fail C3 "tokenizer check: $(tail -3 <<<"${out}")"

# C5: gateway health and model list
models=$(curl -fsS "${gw}/v1/models" -H "Authorization: Bearer ${mk}" 2>/dev/null)
grep -q gpt-oss-120b <<<"${models}" && pass C5 "gateway up, lists gpt-oss-120b" || fail C5 "gateway model list: ${models:-no answer}"

# A temporary key for the request checks; revoked at the end (C7)
key=$(curl -fsS "${gw}/key/generate" -H "Authorization: Bearer ${mk}" -H 'Content-Type: application/json' \
      -d '{"key_alias": "smoke-test"}' | python3 -c 'import json,sys; print(json.load(sys.stdin)["key"])')

chat() {  # stream(true|false)
    curl -sS -m 600 "${gw}/v1/chat/completions" -H "Authorization: Bearer ${key}" -H 'Content-Type: application/json' \
        -d "{\"model\": \"gpt-oss-120b\", \"stream\": $1, \"max_tokens\": 40,
             \"messages\": [{\"role\": \"user\", \"content\": \"Name the three primary colors.\"}]}"
}
r=$(chat false)
grep -q '"content"' <<<"${r}" && pass CHAT "answer through the gateway" || fail CHAT "no answer: ${r:0:300}"
r=$(chat true)
grep -q '^data: ' <<<"${r}" && grep -q 'data: \[DONE\]' <<<"${r}" && pass CHAT "streamed answer" \
    || fail CHAT "stream: ${r:0:300}"

# C10: speech-to-text through the gateway (a 2-second tone; the text can be empty, the call must succeed)
python3 - "${tmp}/tone.wav" <<'PY'
import math, struct, sys, wave
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
    w.writeframes(b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / 16000))) for i in range(32000)))
PY
code=$(curl -sS -m 900 -o "${tmp}/stt.json" -w '%{http_code}' "${gw}/v1/audio/transcriptions" \
       -H "Authorization: Bearer ${key}" -F model=whisper -F "file=@${tmp}/tone.wav")
[[ "${code}" == 200 ]] && grep -q '"text"' "${tmp}/stt.json" && pass C10 "Whisper transcribes through the gateway" \
    || fail C10 "HTTP ${code}: $(head -c 300 "${tmp}/stt.json")"

# C10b: document-search embeddings through the gateway (granite-embedding: 768 numbers)
dims=$(curl -sS "${gw}/v1/embeddings" -H "Authorization: Bearer ${key}" -H 'Content-Type: application/json' \
       -d '{"model": "doc-embed", "input": "test sentence"}' \
       | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["data"][0]["embedding"]))' 2>/dev/null)
[[ "${dims}" == 768 ]] && pass C10b "embeddings: 768 numbers" || fail C10b "embeddings: got '${dims:-error}'"

# C8: the requests are logged against the key
pg=$(kubectl -n si get pod -l cnpg.io/cluster=si-postgres,cnpg.io/instanceRole=primary -o name | head -1)
# The gateway writes its logs in batches, so allow up to two minutes.
for _ in $(seq 12); do
    n=$(kubectl -n si exec "${pg}" -c postgres -- psql -d litellm -tAc \
        "select count(*) from \"LiteLLM_SpendLogs\" s join \"LiteLLM_VerificationToken\" t on s.api_key = t.token where t.key_alias = 'smoke-test'" 2>/dev/null)
    [[ "${n:-0}" =~ ^[1-9] ]] && break
    sleep 10
done
[[ "${n:-0}" -ge 1 ]] 2>/dev/null && pass C8 "${n} requests logged for smoke-test" || fail C8 "no spend log rows for smoke-test (${n:-query failed})"

# C7: a revoked key is refused
curl -fsS -o /dev/null "${gw}/key/delete" -H "Authorization: Bearer ${mk}" -H 'Content-Type: application/json' \
    -d "{\"keys\": [\"${key}\"]}"
code=$(curl -sS -o /dev/null -w '%{http_code}' "${gw}/v1/models" -H "Authorization: Bearer ${key}")
[[ "${code}" == 401 ]] && pass C7 "revoked key refused (401)" || fail C7 "revoked key got HTTP ${code}"

# C16: outbound attempts logged on this node (staging egress block). Run egress-block.sh status on the others.
if nft list table inet si_egress >/dev/null 2>&1; then
    hits=$(journalctl -k -b --no-pager -g 'SI-EGRESS' 2>/dev/null | grep -c 'SI-EGRESS' || true)
    [[ "${hits}" -eq 0 ]] && pass C16 "no outbound attempts on this node since boot" \
        || fail C16 "${hits} outbound attempts logged on this node: delivery/staging/egress-block.sh status"
else
    echo "SKIP  C16   no egress block on this node (lab: read the network team's logs instead)"
fi

echo
(( fails == 0 )) && echo "ALL PASSED" || echo "${fails} FAILED"
exit $(( fails > 0 ))
