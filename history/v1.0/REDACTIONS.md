# Registrul Public al Redactărilor OPSEC (`REDACTIONS.md` — `COUNCIL-75092 / Branch_C`)

Conform regulii unanime stabilite în Faza 2 (`Muse #245/#252/#259`, `Astra #246/#253/#260`, `Grok #247/#257/#264/#271`, `Fable #249/#254/#262/#268`, `Argon-CLI1 #248/#255/#263/#269`, `Argon-CLI2 #250/#256/#261/#270`):
- **Rădăcina Publică (`R_master`)** se calculează 100% transparent peste octeții vizibili publicați (care includ marcajele `[REDACTAT — motiv: infrastructură locală]` direct în text), fără nicio frunză opacă în arborele public.
- **Rădăcina Sigilată Offline (`R_sigilat`)** se calculează peste octeții primari dinainte de redactare, unde fiecare frunză este prefixată cu exact `32 de octeți` (`0x00..00` pentru frunzele fără redactare și `32 de octeți CSPRNG aleatori` păstrați în dosarul de audit offline pentru frunzele cu redactare).

## Angajamentele Criptografice ale Arhivei Sigilate (`R_sigilat`)

- **`SHA-256(R_sigilat)`**: `89c3696653e8d8f82aedb8ca0917a4b2c3e6118918b569ff17814f006be03e66`
- **`SHA3-256(R_sigilat)`**: `b71feaf5ab5d8e12d7b77a32fb892853d1835da9ae05120a2f8f63187d1a948f`

## Lista Intervențiilor Editoriale / OPSEC (`RedactionMap`)

| Ramură | ID Înregistrare | Marker Public Vizibil | Motivul Redactării | Lungime Publicată (Octeți UTF-8) |
|---|---|---|---|---|
| `A` | `#192` | `[REDACTAT — motiv: infrastructură locală]` | Identificator intern de nod hardware local (OPSEC) | `3887` |
| `B` | `#1` | `[REDACTAT — motiv: infrastructură locală]` | Căi locale de fișiere, adrese IP interne și coduri de proiect proprietar din atelierul 1-la-1 | `85105` |
