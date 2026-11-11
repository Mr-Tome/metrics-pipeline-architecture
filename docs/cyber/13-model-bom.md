# 13. Model bill of materials (initial, for Cyber Security and program approval)

**Track:** Cyber Security ([package index and decision register](README.md)).
**Status:** Draft, 2026-11-11. Companion to the software BOM ([12](12-software-bom.md)).
**Scope:** every machine-learning model and model-related data file that phase 1 brings into the lab. That
includes the ones we deliver on purpose, the alternatives we are still choosing between, and the ones that come
along inside container images. Cyber decides which are allowed; nothing has been left off because we expected it
to be refused.

A software BOM says what code runs. A model BOM says what learned weights run, where they came from, what they
are licensed and approved for, and how we know the files are the ones the publisher released. Weights are not
code, but they decide what the system says, they can be very large opaque files, and some file formats can run
code when loaded. That is why they get their own list.

## 1. Models we deliver (bundle `models/`, through the model intake checks)

All three come from Hugging Face. At pull time, `30-pull-models.sh` turns `main` into a commit hash and records
it in `MODELS.txt`. The commits below are the current `main` on 2026-11-09, for reference.

| | M1 | M2 | M3 |
|---|---|---|---|
| **Model** | gpt-oss-120b | faster-whisper-large-v3 | snowflake-arctic-embed-l-v2.0 |
| **Job in the system** | Language model behind chat, Jupyter, VS Code, MATLAB | Speech-to-text (voice notes, chat-page microphone) | Embeddings for chat-page document search |
| **Publisher** | OpenAI | Systran (conversion of OpenAI's Whisper large-v3) | Snowflake |
| **Repository** | huggingface.co/openai/gpt-oss-120b | huggingface.co/Systran/faster-whisper-large-v3 | huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0 |
| **Commit (2026-11-09)** | `b5c939de8f754692c1647ca79fbf85e8c1e70f8a` | `edaa852ec7e145841d8ffdb056a99866b5f0a478` | `ac6544c8a46e00af67e330e85a9028c66b8cfd9a` |
| **Last changed upstream** | 2025-08-26 | 2023-11-23 | 2025-07-28 |
| **License** | Apache-2.0, plus OpenAI's gpt-oss usage policy (`USAGE_POLICY` file) | MIT | Apache-2.0 |
| **Lineage** | Trained by OpenAI; no base model | Weights of `openai/whisper-large-v3`, converted to CTranslate2 | Snowflake's own; multilingual retrieval model |
| **Size** | 116.8B parameters total (mixture of experts; about 5.1B active per token) | about 1.55B parameters | 568M parameters |
| **Precision** | MXFP4 (4-bit) expert weights, BF16 for the rest | FP16 | FP32 |
| **Format** | safetensors | CTranslate2 `model.bin` (flat binary, not pickle) | safetensors |
| **Files shipped** | 26 files, 65.3 GB | 7 files, 3.09 GB | 12 files, 2.29 GB |
| **Left out at pull** | `original/` and `metal/` copies (about 130 GB) | nothing | ONNX copies (8.3 GB) |
| **Code files in repository** | none (`.py`) | none | none |
| **Chat template** | `chat_template.jinja` (run by vLLM in a sandboxed template engine) | n/a | n/a |
| **Served by** | vLLM (A1), 3 copies, one GPU each | speaches (A4), one GPU. If S12 goes to vLLM, M5 or M6 replaces M2. | Text Embeddings Inference (A5), CPU |
| **Languages** | Mainly English | 99 languages | Multilingual |
| **Model card** | Repository README and OpenAI's gpt-oss model card | Repository README; Whisper large-v3 card | Repository README |
| **Approval** | Open ([decision register](README.md) S5) | Open (S5). Not pickle; format decision S20. | Open (S5) |

**M4: tokenizer vocabularies.** `o200k_base.tiktoken` and `cl100k_base.tiktoken`, from
openaipublic.blob.core.windows.net, checked against the SHA-256 values in the tiktoken library. They are word
lists, not weights. vLLM needs the first one for gpt-oss and would otherwise download it at startup.

**Training data.** None of the publishers release their full training data. Each model card describes it in
general terms. That is normal for open-weight models, and it is a question for program approval (S5), not
something we can close ourselves.

## 2. Models that come inside container images (not through the model intake)

The model intake (safetensors only, a checksum for every file) applies to the bundle's `models/` folder. These
come inside images instead, so the image scan and the Zarf SBOM list them only as files.

| ID | Model or data | Where | License | Used by us? |
|---|---|---|---|---|
| E1 | `sentence-transformers/all-MiniLM-L6-v2` (embedding model) | Open WebUI image (A3) | Apache-2.0 | No. We point document search at M3. |
| E2 | `TaylorAI/bge-micro-v2` (small embedding model) | Open WebUI image | MIT | No |
| E3 | `Systran/faster-whisper-base` (speech-to-text, CTranslate2 `model.bin`) | Open WebUI image | MIT | No. Speech goes to M2 through the gateway. |
| E4 | `cl100k_base` tokenizer vocabulary | Open WebUI image | MIT (tiktoken) | Yes, to count text length |
| E5 | Tesseract OCR language models: English, Italian, French, Spanish, German, Japanese, plus script detection | Tika image (A6), from Debian packages | Apache-2.0 | Yes, OCR on scanned PDFs |
| E6 | Anthropic tokenizer file and model price list (data) | LiteLLM image (A2) | MIT (LiteLLM) | Price list only (local copy, no download) |

E1 to E3 are copied into the image when Open WebUI builds it. They sit under `/app/backend/data/cache`, which
our chat-page volume covers at run time, so they are shipped but not used. Some of these repositories also hold
pickle-format copies. Which files are in the image will be confirmed from the image itself.

**Standard or slim image (decision S13, still open on our side).** Open WebUI publishes both, built from the same
code. The difference is what is inside.

| | Standard image (A3) | Slim image (A3s) |
|---|---|---|
| Built-in models E1 to E3 | Included, unused | Left out |
| Libraries to run models inside the chat page (PyTorch, transformers, sentence-transformers, faster-whisper, ONNX runtime) | Included, unused: our models run on vLLM and Text Embeddings Inference | Left out |
| Browser automation (Playwright) and storage clients we don't use | Included | Left out |
| Built-in vector store (Chroma) for uploaded documents | Included, and our current settings use it | **Not included.** Document vectors must go to PostgreSQL with pgvector (A8). |
| Effect on Cyber's review | Larger image, more packages for the scanner to report, model files that never pass the model intake | Smaller image, fewer packages, no hidden models |
| Effect on our work | None. This is what the sandbox plan is built around. | New settings to point the chat page at PostgreSQL ([11](../software/11-sandbox-bringup-plan.md), W23). It also puts the vectors under the database's three copies, instead of a single volume. |

The scan results from the first pull will show the size of the difference in packages and findings. That, plus a
sandbox run on PostgreSQL vectors, is what the choice should rest on.

## 3. Alternatives and later models we are asking about

Commits are the current `main` on 2026-11-11. "Can loading run code?" refers to the files we would ship.

| ID | Model | Why | Publisher, license | Format and size | Can loading run code? |
|---|---|---|---|---|---|
| M5 | `openai/whisper-large-v3-turbo`, commit `41f01f3f` | Speech-to-text on vLLM instead of speaches + M2 (S12). Faster, slightly less accurate than large-v3. | OpenAI, MIT | safetensors, 1.62 GB (809M parameters) | No |
| M6 | `openai/whisper-large-v3`, commit `06f233fe` | Same as M5, full-size model. These are the weights M2 was converted from. | OpenAI, Apache-2.0 | safetensors (1.55B parameters). The repository also has pickle copies; the pull leaves them out. | No |
| M7 | `BAAI/bge-m3`, commit `5617a9f6` | Widely used multilingual embedding model; alternative to M3. We don't need it, but it is the clearest example of a model published only in pickle form. | BAAI, MIT | pickle (`pytorch_model.bin`, plus two small `.pt` files) and ONNX. No safetensors. | **Yes** (pickle) |
| M8 | `BAAI/bge-reranker-v2-m3`, commit `953dc6f6` | Better document search ([11](../software/11-sandbox-bringup-plan.md), W20). Later, not the first bundle. | BAAI, Apache-2.0 | safetensors, 2.27 GB | No |
| | Cloudflare Clef (typed decision model, Qwen base) | Deferred ([decision register](README.md) S9) | Cloudflare, Apache-2.0 | Ships a Python file that runs at load time | **Yes** (Python code) |
| | Sandbox stand-in model (small instruct model) | Rehearsal only. **Never sealed into the lab bundle.** | to be named | safetensors | No |

## 4. File formats: where the line is, and why

**The line is not "safetensors versus everything else." It is "can loading this file run code chosen by
whoever made it."**

- **Pickle** (`.bin`, `.pt`, `.pth`, `.pkl`, `.ckpt` from PyTorch) is Python's general object format. A pickle
  file is a list of instructions that the loader carries out, and those instructions can import any Python
  module and call any function. So loading a pickle model is running a program the publisher wrote. This is not
  theoretical: malicious models that open a shell on load have been found on Hugging Face (JFrog, 2024), including
  ones built to slip past Hugging Face's own pickle scanner (ReversingLabs, 2025). PyTorch now loads in a
  restricted mode by default (`weights_only=True`), but CVE-2025-32434 showed code could still run in that mode
  in PyTorch 2.5.1 and earlier. Restricted loading reduces the risk; it doesn't remove it.
- **Safetensors** is a short JSON header (names, shapes, offsets) followed by raw numbers. The loader only reads
  numbers into memory; there is no instruction to follow. It was built for exactly this reason and has had an
  independent security audit (Trail of Bits, 2023).
- **CTranslate2** `model.bin` (M2, E3) is the same kind of thing as safetensors: a header, then named arrays of
  numbers, read by a C++ loader. The `.bin` extension is the only thing it shares with pickle. It does not need
  an exception under a "no code on load" rule. It only looked like one because our first check went by file
  extension.
- **Every format** can still have bugs in its loader (a malformed file crashing or corrupting memory). That risk
  is the same for all of them and is handled like any software vulnerability: patched loaders, scanning, and
  pulling only from the named publisher at a pinned commit.
- **No format** protects against a model that was trained to behave badly. That is covered by publisher,
  provenance, and program approval (S5), not by file checks.

**Options for Cyber (S20):**

| Option | What it allows | What it rules out |
|---|---|---|
| (a) No code on load (our recommendation) | safetensors, CTranslate2, tokenizer and config files | Pickle, and anything with Python that runs at load (M7, Clef) |
| (b) Safetensors only | safetensors, tokenizer and config files | Also M2 and the faster-whisper route (S12 would have to go to vLLM with M5 or M6) |
| (c) Also pickle, with controls | Everything in this document | Nothing. Controls would be: scan each pickle file (for example with `modelscan` or `picklescan`, which we would add to the bundle), load only in restricted mode, and if possible convert to safetensors on an isolated build machine. Converting breaks the match to the publisher's checksums, so the provenance record has to show the conversion. |

**How a model file is checked today:**

| Step | Check |
|---|---|
| Pull (build side) | Only the listed repository at a recorded commit. Pickle-format files are refused. M2's `model.bin` is accepted only if it starts with the CTranslate2 header. GGUF and ONNX copies are left out. SHA-256 recorded for every file. |
| Seal | Every file in `SHA256SUMS`, signed |
| Intake (lab) | `verify.sh` checks the signature and every checksum, and refuses any pickle-format file again |
| Load | No service sets `trust_remote_code`, so any Python in a model folder is never run |

**Proposed additions (S21):** refuse `.py` files at pull, so the bundle holds no model code at all; and run the
same model-file check over the container images (section 2), so a model can't come in that way unnoticed.

## 5. What the formal version will look like

For each sealed bundle, this list is regenerated from `MODELS.txt` and the per-model `SHA256SUMS`. If the Cyber
team wants a standard format, CycloneDX 1.6 has a machine-learning BOM (a component of type
`machine-learning-model` with a model card), and SPDX 3.0 has AI and Dataset profiles. Either can be generated
from the same files.
