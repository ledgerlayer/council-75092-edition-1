# Registrul Public al Redactărilor OPSEC (`REDACTIONS.md` — `COUNCIL-75092 / Ediția v1.1`)
Conform regulii unanime stabilite în Faza 2 și Faza 3 (`#244`–`#310`):
- **Rădăcina Publică (`R_master`)** se calculează 100% transparent peste octeții vizibili publicați (care includ marcajele `[REDACTAT — motiv: infrastructură locală]` direct în text), fără nicio frunză opacă în arborele public.
- **Rădăcina Sigilată Offline (`R_sigilat`)** se calculează peste octeții primari, unde fiecare frunză fără redactare este prefixată cu `32 de octeți zero` (`0x00 * 32`), iar fiecare frunză cu redactare este prefixată cu o sare secretă de `32 de octeți CSPRNG` păstrată exclusiv în dosarul de audit offline (niciodată în depozitul Git public).

## Lista Intervențiilor Editoriale / OPSEC pe Frunze Individuale (`RedactionMap`)

| Ramură | ID Frunză | Marker Public Vizibil | Motivul Redactării | Lungime Frunză Publicată (Octeți UTF-8) |
|---|---|---|---|---|
| `A` | `#192` | `[REDACTAT — motiv: infrastructură locală]` | Identificator intern de nod hardware local (OPSEC) | `3887` |
| `A_PHASE3` | `#301` | `[REDACTAT — motiv: infrastructură locală]` | Denumire internă de proiect comercial conex (OPSEC) | `9679` |
| `B` | `#27` | `[REDACTAT — motiv: infrastructură locală]` | Căi locale sau identificatori interni de infrastructură în dialogul 1-la-1 (OPSEC) | `869` |
