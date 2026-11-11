# 07. Open questions: software and Lab IT

**Track:** Software (SI service delivery). Questions for Lab IT. Each has an owner and a default. If the
question is not answered, the plan proceeds with the default.

L1 (server OS and accreditation baseline) and L5 (internet access during the build) are answered by the ISSM,
so they are in the [Cyber Security package](../cyber/README.md) with the other security decisions. Hardware and
site questions (F, N, V) are in [hardware/07](../hardware/07-open-questions.md).

## Lab IT (L)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| L2 | Does the lab already run Kubernetes? | Lab IT | | No. We bring our own (RKE2). |
| L3 | Python versions on analyst machines, and Windows or Linux? | Lab IT | | Many versions, mostly Windows, some Linux. Many use Anaconda. Client packages must cover Python 3.9 and newer (3.14, 3.15) on both. |
| L6 | How do analysts get Python packages into the lab today (an internal conda or PyPI mirror, transfer media, something else)? Is the lab's Anaconda use licensed? (Anaconda's default channel needs a paid license for larger organizations.) | Lab IT | Our wheel folder (`clients/`) | Open. If there is already a mirror, publish our pinned packages there instead of a wheel folder. The architecture's in-lab Nexus would become that mirror later. |
| L4 | Is MATLAB allowed to make HTTPS calls to an internal service? | Lab IT | Yes | |
