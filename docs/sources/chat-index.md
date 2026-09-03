# Imported chat index

Imported: 2026-08-26

These summaries identify useful decisions and provenance. The PDFs contain model suggestions, not automatically accepted requirements.

## [GPT — HDA](<chats/GPT [ N ] HDA.pdf>)

Role: most useful chronological source for the recent Houdini implementation.

Adopted or confirmed:

- one hero, one `neuromat` HDA, JSON-driven material state;
- UV projection is sufficient for this phase;
- COPS/MaterialX masks for variation, dirt, wear, and bump;
- fixed studio lighting and baked AO/curvature;
- HDA-owned bump safety cap;
- finish HDA before TOP/camera automation;
- current stochastic bump should become finer and substantially lower amplitude.

Latest historical checkpoint:

- The stochastic result looked like broad melted blobs.
- Proposed next test: frequencies around `noise_scale × 40` and `× 160`, octaves `2 / 1`, weights `0.85 / 0.15`, and very small bump height/cap.
- `iron_brushed_scratched` was being used to view stochastic work even though its final branch should be directional.

Important risk:

- The conversation identified Apprentice watermarks as unacceptable for the final dataset. Current project files are `.hipnc`/`.hdanc`, and observed development renders are watermarked.

## [GPT — Generate Materials](<chats/GPT [ N ] Generate Materials.pdf>)

Role: evolution and review of the current material generator and semantic-label system.

Adopted or confirmed:

- deterministic material construction and hash-based procedural seeds;
- controlled template families selected by semantic mode;
- compact semantic parts are assembled into shallow wording variation;
- no uncontrolled framing, style drift, or physics-changing synonyms;
- validation should detect repetition, punctuation problems, and contradictions;
- same source and seed should generate the same labels.

Discrepancy at import time (resolved 2026-09-02):

- The imported stress JSON contained `with with`, showing that adjacent duplicate-word validation and existing-label QA were incomplete at the time. The production generator and library have since been corrected; see the canonical label specification.

## [Gemini — Material Generator](<chats/gemini [ N ] Material Generator.pdf>)

Role: early design evolution of the material dictionaries, schema, HDA driving, and render outputs.

Adopted or confirmed:

- structured base × finish × condition × color generation;
- MaterialX/Karma target;
- deterministic seeds;
- representative stress subset;
- AO and curvature both contribute to condition masks;
- direct handling for transmission, thin-wall, and dispersion fields;
- raw appearance/geometry AOVs are useful even though the model target is final RGB.

Superseded or unreliable:

- older 135/1,980 material estimates;
- `has_k` as a central metal switch;
- various unverified MaterialX parameter-range claims;
- any recommendation contradicted by the current generator or HDA.

## [Gemini — Look Dev in COPS](<chats/gemini [ N ] Look Dev in COPS.pdf>)

Role: early manual variation-map and lighting look-dev.

Adopted or confirmed:

- variation is subtle material identity, not AO/dirt;
- large and small procedural scales should avoid visible tiling;
- reflective materials require an environment to read correctly;
- use a controlled, reduced-strength studio HDRI rather than flat lighting for final look-dev;
- keep lighting fixed during dataset generation.

Historical tuning values in this chat are visual experiments, not universal production constants.

## [Gemini — NEURON](<chats/gemini [ N E U R O N ].pdf>)

Role: broad project ideation and the origin of the longer-term Neuron vision.

Adopted or confirmed:

- learn generative AI through a constrained synthetic-data project;
- finish the UV-based Material Hero rather than perfecting projection;
- use the first milestone as a path toward a prompt-driven 3D application;
- persistent neural assets and scene composition remain future research.

Superseded or speculative:

- product/model claims unrelated to the implemented repository;
- proposed architectures presented without experiments;
- older project state before dirt, wear, and the current HDA.

## How to import another chat

For each new conversation, record:

- source filename and import date;
- topics;
- user decisions;
- implementation facts that were subsequently verified;
- unresolved questions;
- suggestions that are speculative, rejected, or superseded.

Do not copy a chat’s recommendations directly into canonical specifications without checking current artifacts and confirming the decision.
