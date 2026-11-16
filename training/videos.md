# Training sim videos (draft for review)

A short YouTube video for each sim step, picked 2026-11-16. Links open at the start time given. Nothing is wired into the
sims yet: this list gets reviewed first.

**How each pick was checked.** Nobody has watched these. "Transcript" means the spoken words were read and match the
step. "Chapters" means only the title, channel, description, and chapter list were checked (YouTube blocked transcript
reads partway through the search). Watch every "Chapters" pick before it goes in a sim.

**Where they play.** YouTube needs internet. They will not play on the lab network.

## SI bring-up sim (`si-bringup-sim.html`)

| Step | Video | Start | Length | Checked | Notes |
|---|---|---|---|---|---|
| The transfer drive arrives | [Verify SHA256 checksum on Linux](https://www.youtube.com/watch?v=uIIn6qVGOJQ&t=20s) (SavvyNik, 2023) | 0:20 | 4 min to watch | Transcript | Stop at 4:05 (MD5 part not needed). |
| Fault: the signature check fails | [Verify a download's digital signature (GPG)](https://www.youtube.com/watch?v=hpv9PyrUHPw) (Curtis Computing, 2026) | 0:00 | 5 min | Transcript | Opens with exactly our case: the hash matches but the file can still be fake. Skip 1:25–2:30 (Windows). New channel, few views. |
| What a PASS means | [What are digital signatures?](https://www.youtube.com/watch?v=s22eJ1eVLTU) (Computerphile, 2020) | 0:00 | 10 min | Transcript | The concept behind verify.sh: hash, then sign the hash. |
| Briefing / air gap | [What is an air gap?](https://www.youtube.com/watch?v=rh3yG8fsYA8) (Eye on Tech, 2022) | 0:00 | 2 min | Transcript | Why the lab has no internet. |
| Start the cluster, The join token, Join the other nodes | [Quick start: installing RKE2](https://www.youtube.com/watch?v=BDpafdbPyFc&t=128s) (Slap Ya Administrator, 2025) | 2:08 | 7 min | Chapters | Stop at 9:22 (the Rancher UI part isn't in our build). Online install, not air-gapped. |
| Join the other nodes | [RKE2 high availability explained](https://www.youtube.com/watch?v=Um_GVIL71xQ) (Clemenko, 2024) | 0:00 | 4 min | Chapters | Why three server nodes. |
| Fault: the driver won't build | [NVIDIA open GPU kernel modules: DKMS, Secure Boot](https://www.youtube.com/watch?v=ogyM4EDwxnw&t=209s) (Alex Hitt, 2026) | 3:29 | 4 min | Chapters | Weak pick: new channel, may be machine-made. Covers build environment, Secure Boot signing, DKMS. |
| Prepare gpu01 | [NVIDIA GPU Operator overview](https://www.youtube.com/watch?v=KER0dbfmAqQ&t=186s) (NVIDIA Developer, 2023) | 3:06 | 8 min | Chapters | Official NVIDIA. |
| Fault: a model fails its check | Reuse the SHA256 video above | | | | |
| Platform step | [Getting started with Zarf](https://www.youtube.com/watch?v=7X2znDbN4-E&t=315s) (Defense Unicorns, 2022) | 5:15 | 3 min | Chapters | Official. "Initializing Zarf" = our platform step. 2022, so commands may differ from today's Zarf. |
| Platform step (background) | [Solving air-gap problems with Zarf](https://www.youtube.com/watch?v=FxwbxzMTskw) (OpenSSF, 2024) | 0:00 | 24 min | Chapters | Talk by a Zarf maintainer. Optional, longer. |
| The TLS certificate | [SSL, TLS, HTTPS explained](https://www.youtube.com/watch?v=j9QmMEWmcfo) (ByteByteGo, 2022) | 0:00 | 5 min | Chapters | |
| The TLS certificate | [Root vs intermediate certificates](https://www.youtube.com/watch?v=l_ZbduoVQqs) (CyberArk, 2021) | 0:00 | 3 min | Chapters | Why the lab CA's chain matters. |
| Deploy the SI apps | [Walkthrough: deploying packages with Zarf](https://www.youtube.com/watch?v=7hDK4ew_bTo&t=139s) (Defense Unicorns, 2023) | 2:19 | 3 min | Chapters | Official. |
| What runs where | [Kubernetes explained in 6 minutes](https://www.youtube.com/watch?v=TlHvYWVUZyc) (ByteByteGo, 2023) | 0:00 | 6 min | Chapters | Nodes, pods, control plane. |
| Fault: a pod can't get its image | [What is ImagePullBackOff?](https://www.youtube.com/watch?v=1q7RLvwdkyo&t=15s) (Sysdig, 2023) | 0:15 | 2 min | Chapters | |
| The language model isn't ready | [Liveness vs readiness vs startup probes](https://www.youtube.com/watch?v=fqfieWP1jY4&t=71s) (Anton Putra, 2024) | 1:11 | 1 min | Chapters | Why Running isn't Ready. |
| The language model isn't ready | [What is vLLM?](https://www.youtube.com/watch?v=McLdlg5Gc9s) (IBM Technology, 2025) | 0:00 | 4 min | Chapters | What the model pods run. |
| First accounts and keys | [Open WebUI admin panel walkthrough](https://www.youtube.com/watch?v=4pIzLtUhJLM&t=20s) (The Personal AI Architecture, 2024) | 0:20 | 7 min | Chapters | Users, connections, document settings. The UI has changed since 2024. |
| First accounts and keys, Fault: document upload fails | [LiteLLM AI gateway: API keys](https://www.youtube.com/watch?v=Nk7qDiLHyuU&t=219s) (Paul Zuradzki, 2026) | 3:39 | 2 min | Chapters | Stop at 5:01. Shared keys and per-model scope. |
| Checks before hand-over | [Port forwarding in Kubernetes](https://www.youtube.com/watch?v=Ab3PjErW37M&t=52s) (Lukonde Mwila, 2021) | 0:52 | 2 min | Chapters | Stop at 2:37 (the rest is AWS setup). |
| Can I use it from Jupyter? | [The OpenAI API vs ChatGPT](https://www.youtube.com/watch?v=CI3wHdLJb_c) (Ardit Sulce, 2025) | 0:00 | 3 min | Chapters | Weak pick: a preview of a paid course. Explains chat page vs API. |
| A big table | [Why RAG fails with complex documents](https://www.youtube.com/watch?v=xc63tFIIfeA&t=115s) (IBM Technology, 2026) | 1:55 | 5 min | Chapters | Close, not exact: about complex documents, not tables. |
| Big documents in the chat page | [What is RAG?](https://www.youtube.com/watch?v=T-D1OfcDW1M) (IBM Technology, 2023) | 0:00 | 6 min | Chapters | |
| Big documents in the chat page | [Open WebUI knowledge bases: RAG and embeddings](https://www.youtube.com/watch?v=LmXaPUky_u4&t=518s) (Professor Patterns, 2025) | 8:38 | 4 min | Chapters | Chunk size and top-K, the settings in our values file. |
| A scanned report | [Optical character recognition (OCR)](https://www.youtube.com/watch?v=or8AcS6y1xg) (IBM Technology, 2022) | 0:00 | 6 min | Chapters | |
| Hand-over | None found | | | | |

## Rack 1 install sim (`rack1-install-sim.html`)

| Step | Video | Start | Length | Checked | Notes |
|---|---|---|---|---|---|
| Check every carton against the order | None found | | | | |
| Which airflow does sw01 need? | [Inside a data center rack](https://www.youtube.com/watch?v=-zwnwdOtt0o&t=442s) (NexLayer Tech, 2026) | 7:22 | 1 min | Chapters | Front-to-back airflow. Doesn't cover port-side intake vs exhaust. |
| Which NX-OS license goes with sw01? | [Smart Licensing on Nexus switches](https://www.youtube.com/watch?v=hrHdMyFhtlg&t=42s) (Cisco, 2022) | 0:42 | 3 min | Chapters | Official. Covers the offline methods an air-gapped lab needs. |
| Which way does rack 1 face? | [Hot aisle vs cold aisle containment](https://www.youtube.com/watch?v=qzTpqpHnRdU&t=49s) (MEP Academy, 2026) | 0:49 | 4 min | Chapters | |
| Is the rack grounded? | [Server rack grounding: test with a multimeter](https://www.youtube.com/watch?v=qTFricrhZjM&t=32s) (The IT Lab UK, 2025) | 0:32 | 3 min | Chapters | Home-lab setting, UK. Facilities owns the real bond. |
| Is the rack grounded? (background) | [Grounding and bonding: definitions](https://www.youtube.com/watch?v=2ZW63Pg0NCY&t=210s) (Eaton, 2022) | 3:30 | 2 min | Chapters | Two engineers, NEC terms. |
| Set the rail depth | [Rack and stack a full rack](https://www.youtube.com/watch?v=pLBYulLueQo&t=138s) (Custodian Data Centres, 2019) | 2:18 | 1.5 min | Chapters | Rails going in. Rail depth isn't covered on its own. |
| Label the PDUs | [Inside a data center rack](https://www.youtube.com/watch?v=-zwnwdOtt0o&t=284s) (NexLayer Tech, 2026) | 4:44 | 2 min | Chapters | Rack PDUs, then A and B feeds. |
| Install the GPUs | [Replace a GPU in a PowerEdge XE2420](https://www.youtube.com/watch?v=of37ToNVvrg&t=16s) (Dell Enterprise Support, 2020) | 0:16 | 3 min | Chapters | Official server GPU handling. Not our server model. |
| Install the GPUs | [Why 16-pin connectors melt](https://www.youtube.com/watch?v=Y36LMS5y34A&t=775s) (Gamers Nexus, 2024) | 12:55 | 4 min | Chapters | Stop at 16:36. Why "no gap" matters. Consumer cards, same connector. |
| Install the GPUs | [Ways to ground yourself](https://www.youtube.com/watch?v=akbuQeIlv9g) (Underground Tech, 2017) | 0:00 | 1 min | Chapters | ESD strap basics. |
| Rack the gear, bottom up | [Rack and stack a full rack](https://www.youtube.com/watch?v=pLBYulLueQo&t=225s) (Custodian Data Centres, 2019) | 3:45 | 2 min | Chapters | Mounting servers and switches. |
| Rack the gear (blanking) | [Airflow management in your racks](https://www.youtube.com/watch?v=2djlYvScCOc) (Legrand, 2025) | 0:00 | 6 min | Chapters | Blanking panels and air leaks. |
| Before any cord goes in | [Electrical lockout/tagout procedure](https://www.youtube.com/watch?v=HcvJ_Xp-ofo) (Safelyio, 2025) | 0:00 | 5 min | Chapters | |
| Plug in every cord | [Power connectors overview](https://www.youtube.com/watch?v=C0aLMOodVsg&t=22s) (ShowMeCables, 2017) | 0:22 | 1.5 min | Chapters | IEC C13/C14/C19/C20. |
| What does one circuit carry? | [Data center redundancy: N, N+1, 2N](https://www.youtube.com/watch?v=FWpWU9tiKs4&t=170s) (MEP Academy, 2026) | 2:50 | 2 min | Chapters | Why one feed takes the full load. |
| What does one circuit carry? | [Volts, amps, and watts explained](https://www.youtube.com/watch?v=mvuHsu8S6v8&t=62s) (Techquickie, 2016) | 1:02 | 3.5 min | Chapters | Stop at 4:23. The W / V = A math. |
| Run the network cables | [SFP, SFP28 and why you need DAC](https://www.youtube.com/watch?v=o8jL1lxdN4M) (Lawrence Systems, 2021) | 0:00 | 7 min | Chapters | |
| Run the network cables | [Singlemode vs multimode](https://www.youtube.com/watch?v=Ik4gH2kW-kE) (HUBER+SUHNER, 2025) | 0:00 | 3 min | Chapters | Our 100G uplinks run on multimode. |
| Dress the DACs | [Cable management best practices](https://www.youtube.com/watch?v=842q_agTtnQ) (CABLExpress, 2011) | 0:00 | 3 min | Chapters | Old. Covers velcro vs zip ties. |
| Power on, Feed test | [Data center redundancy: N, N+1, 2N](https://www.youtube.com/watch?v=FWpWU9tiKs4&t=280s) (MEP Academy, 2026) | 4:40 | 1 min | Chapters | Electrical redundancy. |
| First power-on checks | [What is a BMC?](https://www.youtube.com/watch?v=qWAsXQvJVkU&t=43s) (Professor Linux, 2024) | 0:43 | 7 min | Chapters | |
| First power-on checks | [Out-of-band management](https://www.youtube.com/watch?v=EQjF6RzKSy4&t=55s) (LookingPoint, 2018) | 0:55 | 3 min | Chapters | Why oob01 exists. |
| Set the gpu01 BIOS | [Device passthrough: IOMMU, SR-IOV](https://www.youtube.com/watch?v=_SRup11EJ04&t=80s) (XOR, 2026) | 1:20 | 3 min | Chapters | Weak pick: new channel, gaming opener. Clear chapters on IOMMU and SR-IOV. |
| Set the gpu01 BIOS | [Resizable BAR](https://www.youtube.com/watch?v=RqlDIyZvgNo&t=56s) (Linus Tech Tips, 2021) | 0:56 | 0.5 min | Chapters | Gaming setting. Stop at 1:18. |
| Validate | [Monitor and manage GPUs with nvidia-smi](https://www.youtube.com/watch?v=DHRLd9xDAbI&t=150s) (Liv4IT, 2024) | 2:30 | 5.5 min | Chapters | |
| Validate | [Test network speed with iPerf3](https://www.youtube.com/watch?v=kGaD6KwyihA&t=203s) (Learn Linux TV, 2026) | 3:23 | 8 min | Chapters | Skip the ad at 9:47. |
| Sign-off | None found | | | | |
