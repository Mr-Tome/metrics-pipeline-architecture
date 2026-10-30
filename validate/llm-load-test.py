#!/usr/bin/env python3
"""Load test for the AI gateway. Python standard library only, so it runs on any lab machine.

Sends N users' worth of streaming chat requests at once and reports time-to-first-token and
tokens per second. The BOM plans for 10 simultaneous requests at 50 users (Assumptions C8).

usage:
  llm-load-test.py --url https://api.lab.example/v1 --key sk-... --users 10 --rounds 3
  llm-load-test.py ... --ca /path/to/lab-ca.pem      (lab CA for HTTPS)
"""
import argparse
import json
import ssl
import statistics
import threading
import time
import urllib.request

PROMPT = ("Summarize, in about 300 words, how a test conductor should log anomalies during a "
          "system-level test event, and what fields each log entry should include.")


def one_request(args, ctx, results):
    body = json.dumps({
        "model": args.model, "stream": True, "max_tokens": args.max_tokens,
        "messages": [{"role": "user", "content": PROMPT}],
    }).encode()
    req = urllib.request.Request(args.url.rstrip("/") + "/chat/completions", data=body, headers={
        "Authorization": f"Bearer {args.key}", "Content-Type": "application/json"})
    start = time.monotonic()
    first = None
    chunks = 0
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=300) as resp:
            for raw in resp:
                line = raw.decode().strip()
                if not line.startswith("data:") or line.endswith("[DONE]"):
                    continue
                delta = json.loads(line[5:])["choices"][0].get("delta", {})
                if delta.get("content") or delta.get("reasoning_content"):
                    first = first or time.monotonic()
                    chunks += 1
        end = time.monotonic()
        results.append({"ttft": (first or end) - start, "total": end - start,
                        "tps": chunks / max(end - (first or end), 1e-6)})
    except Exception as exc:  # report and keep going; one failure should not hide the others
        results.append({"error": str(exc)})


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", required=True, help="gateway base URL ending in /v1")
    p.add_argument("--key", required=True, help="LiteLLM key (deploy.sh user-key <name>)")
    p.add_argument("--model", default="gpt-oss-120b")
    p.add_argument("--users", type=int, default=4)
    p.add_argument("--rounds", type=int, default=3)
    p.add_argument("--max-tokens", type=int, default=400)
    p.add_argument("--ca", help="CA bundle for the gateway certificate")
    args = p.parse_args()
    ctx = ssl.create_default_context(cafile=args.ca)

    results = []
    for r in range(args.rounds):
        threads = [threading.Thread(target=one_request, args=(args, ctx, results)) for _ in range(args.users)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print(f"round {r + 1}/{args.rounds} done")

    ok = [x for x in results if "ttft" in x]
    errors = [x["error"] for x in results if "error" in x]
    if ok:
        ttft = sorted(x["ttft"] for x in ok)
        print(f"\nrequests: {len(ok)} ok, {len(errors)} failed, {args.users} at a time")
        print(f"time to first token: median {statistics.median(ttft):.2f} s, worst {ttft[-1]:.2f} s")
        print(f"stream rate per user: median {statistics.median(x['tps'] for x in ok):.1f} chunks/s")
        print("target: first token under about 2 s at the planned peak")
    for e in errors[:5]:
        print("error:", e)
    raise SystemExit(1 if errors or not ok else 0)


if __name__ == "__main__":
    main()
