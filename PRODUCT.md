# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Two audiences share the same screens, with different permissions, and future UI work serves both equally:

- **Documentalists at cooperating centers**: librarians and indexers across the BIREME network, identified by their cooperating-center code. They catalog information sources day to day: bibliographic records (LILACS/LILDBI), internet resources (LIS), events (DirEve), multimedia, legislation (LeisRef), educational resources (OER), and institutions (DirIns).
- **BIREME editors**: central staff who review, approve, and maintain quality across every center's records. They also manage the DeCS thesaurus, control tables, suggestions, error reports, and reports.

Access is role-based per service (for example `LILDBI`, `LIS`, `DirEve`, `TesauroDeCS`), with editor (`edi`) levels and an advanced user type. What a user sees depends on their roles and center code.

## Product Purpose

FI-ADMIN (Information Sources Administration) is BIREME/PAHO/WHO's administration interface and API for the information sources that feed the Virtual Health Library (VHL/BVS). It is where the network creates, indexes, reviews, and publishes source records. The API then exposes those records to VHL portals and search. Success means complete, standards-conformant records that reach the VHL with as little friction and rework as possible.

## Positioning

FI-ADMIN is the shared cataloging back-office of a cooperative network. Many cooperating centers, one central editorial authority, and one set of shared methodologies (LILACS, DeCS) all work in the same records. A generic CMS or catalog tool cannot copy that combination of distributed authorship, center-scoped permissions, and conformance to BIREME's methodologies.

## Operating Context

- Long, field-dense cataloging forms, filled in record by record and often in batches, using controlled vocabularies (DeCS descriptors) and methodology-defined fields.
- Records go through review and status workflows between center and central editors, with deduplication, change logs, suggestions, and error reports.
- Users work in English, Portuguese, or Spanish depending on their country.

## Capabilities and Constraints

- **Server-rendered Django**: Django templates with jQuery and Bootstrap 2-era front-end assets (`src/templates/`, `src/static/`). Keep this architecture. No SPA rewrite.
- **Trilingual EN / PT-BR / ES**: all UI copy goes through Django i18n (`src/locale/`). Portuguese and Spanish are first-class languages, and layouts must fit their longer strings.
- **Data-standards fidelity**: forms map to LILACS/BIREME methodology fields (including ISIS-style subfields and DeCS descriptors). UI work must not simplify, merge, or drop methodology fields for visual convenience.
- **Role-gated navigation**: menu items and actions appear according to service roles and the center code. UI changes must preserve this gating.
- The REST API (`src/api/`) is a product surface for downstream VHL systems, separate from the admin UI.

## Brand Commitments

- The BIREME/PAHO/WHO institutional identity is mandatory: the language-specific BIREME logo in the footer (`src/static/image/logo-bireme-{lang}.png`) and the links to BIREME's Terms and Privacy policies.
- The product name is "FI-ADMIN".

## Evidence on Hand

- Data-model diagrams: `docs/models.png` and `docs/biblioref.png`. Thesaurus docs: `docs/thesaurus/`.
- No user research, usage metrics, or testimonials are recorded in the repository. Do not invent any.

## Product Principles

1. **Record integrity over convenience.** Conformance to the methodology is the product. The UI helps users get it right and never hides required structure.
2. **Equal footing for three languages.** A screen is only finished when it works in EN, PT-BR, and ES.
3. **Fit both roles without forking the UI.** Center documentalists and BIREME editors use the same screens, and permissions shape what each one sees.
4. **Evolve the incumbent stack.** Improve inside server-rendered Django rather than replacing it.

## Accessibility & Inclusion

No formal standard is mandated. Follow sensible best practice: keyboard operability, labelled form fields, and sufficient contrast.
