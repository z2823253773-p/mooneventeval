# Attribution and data license

Dataset: **DESED_public_eval**. Authors: **Nicolas Turpault, Romain Serizel, Ankit Shah, Justin Salamon**.

- Dataset record and license declaration: https://zenodo.org/records/3588172 (DOI:10.5281/zenodo.3588172), **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
- License terms: https://creativecommons.org/licenses/by/4.0/ . Please retain attribution, this link, and the indication of changes when sharing these data or adaptations. No endorsement by the dataset authors is implied.
- Actual annotation bytes: https://github.com/turpaultn/DESED/blob/0686178dd218b431ef1606e5a2139df7c543b07b/data/real/metadata/eval/public.tsv . The complete 119,823-byte annotation table is preserved, losslessly compressed, as source/public-eval.tsv.gz. SHA-256 and exact selection are in SOURCE.json.

The CC BY 4.0 attribution applies to this annotation source, reference.tsv, both derived prediction TSVs, and the annotation-bearing example outputs. The repository's MIT code license does not relicense those data. The Python replay program is project code under MIT.

Changes: select the first two complete recordings (original physical lines2–12, 11events), retain their exact header/order/times/labels. Baseline predictions are a copy of that reference. Regressed predictions shift one Speech onset2.618→2.819, remove the final Dishes event, and append a duplicate of another Dishes event; exact construction is checked in reproduce.py. Predictions are developer-controlled fixtures, **not predictions of a real model**.

No audio is downloaded, copied or distributed. This is an annotation-ingestion demonstration, not a DCASE benchmark run, model performance claim, clinical data release or external user trial.
