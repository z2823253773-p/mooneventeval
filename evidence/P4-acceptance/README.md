# P4 risk-review acceptance

Run `python3 evidence/P4-acceptance/freeze.py` in a public clone with Python >=3.12 and Git. It verifies frozen files, archive SHA256/size/path safety/CRC, full local and two-job CI outputs, 233 source hashes at public commit e106a5d47, and13 product/4 original-reference report replays. The metadata-only source-package check is separately archived and is not claimed as a fresh full CI run. No network or checkout reset is performed.

local-final.zip preserves original candidate06ec1649b; remote-artifacts.zip is the actual successful run40467323131 download; metadata-package.zip rechecks the38-member package after replacing the README CI link. Source and actual receipts are verbatim; logs retain producer paths. Old frozen stages are unchanged.

Independent risk audit:0 Critical/1 presentation Important/2 state Minor, followed by author corrections and actual verification. It did not certify participant authorship, real adoption, complete ecosystem uniqueness, registration eligibility or acceptance. Partial charter retrieval and bounded related-repository search are described in rules-scope.json; missing content is not inferred.
