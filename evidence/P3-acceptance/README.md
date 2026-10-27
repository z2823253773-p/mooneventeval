# P3 acceptance evidence

Run `python3 evidence/P3-acceptance/freeze.py` from an independent public clone. The verifier checks ZIP SHA256/size/member safety/CRC, extracts into a temporary directory, rehashes actual local/remote reports and streams, binds all 222 non-evidence sources to public commit a613579b6 and checks the extra 8+4 report replay. No network, checkout reset or source change is performed. Optimized Python is rejected for the evidence verifier.

`local-candidate.zip` preserves the first candidate through 5e43abb9c (historical, before minor fixes); `local-final.zip` preserves original final074509f2; `remote-artifacts.zip` preserves the downloaded successful two-platform run40447392163. The raw local capture receipts retain their producer paths. Archives are verbatim data, not rewritten pass reports. The legacy T8/P1/R1/P2 frozen records are unchanged.

Original review and negative controls are separately under evidence/P3 and evidence/P3-fixes. Product/reference warnings and failed generator attempts remain visible. This evidence establishes bounded technical/replay results, not independent human authorship, resubmission or organizer approval.
