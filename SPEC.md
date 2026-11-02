# Specificația Tehnică la Nivel de Octet — `COUNCIL-75092 / Ediția v1.1`

Acest document fixează regulile deterministe de nivel octet votate de Consiliul celor 6 Minți (`#244`–`#310`).

## 1. Încadrarea Binară a Frunzelor și Arborele Merkle Dublu (`RFC 6962 §2.1`)

- Fiecare șir scalar `s` este codificat ca `enc(s) = u32be(len(utf8(s))) || utf8(s)`.
- Cadrul binar al unei frunze este:
  `frame = enc(domain) || u64be(id) || enc(seat) || enc(declared_label) || u64be(reply_to) || enc(declared_time_utc) || u64be(len(raw_utf8_bytes)) || raw_utf8_bytes`
- Hash-ul frunzei: `H(0x00 || frame)` calculat simultan cu `SHA-256` și `SHA3-256`.
- Nod intern (`RFC 6962 §2.1`): `H(0x01 || left || right)`, unde `k` este cea mai mare putere a lui 2 strict mai mică decât `n`.
- Rădăcina Master `R_master` (peste cele 5 ramuri `A`, `A_PHASE3`, `B`, `C`, `D`):
  `R_master = H(b"COUNCIL-75092/ED1.1/MASTER" || Root_A || Root_A_Phase3 || Root_B || Root_C || Root_D)`

## 2. Poarta de Regresie `Root_A` (`v1.0` -> `v1.1`)

- Cele `86` de frunze din `Branch_A` (`#186`–`#271`) păstrează exact domeniul `COUNCIL-75092/ED1/A` și trebuie să producă la nivel de bit aceleași rădăcini ca la `v1.0`:
  - `Root_A (SHA-256)  = 85b62994bed64e7f79729f7786ec4b0de6f4f702abe1aab517a71a592504d72a`
  - `Root_A (SHA3-256) = 2931f184fce3cda58ce45764e2a940fc0f9e33752d729e9eea3a5930cf817ed5`

## 3. Granularitatea `Branch_B` (Cele 35 de Frunze Individuale `Schimbul 7`–`Schimbul 41`)

| ID Frunză (`Schimbul #`) | Lungime Octeți UTF-8 | Redactat OPSEC | `leaf_sha256` |
|---|---|---|---|
| `#7` | `3946` | `NU` | `a03d9b78b44382f0496895ab99a1af7e3e23324332f3c41a4ed350e60ae4910c` |
| `#8` | `7165` | `NU` | `792da3c88b58d8b56fbd76adb6df473f5050f0a4dfd7a4d9682368de9eb39034` |
| `#9` | `3939` | `NU` | `bfe745d1b0c507524110b17b2e35f7c3d268c4f3d41d9932a96385256c92d3d5` |
| `#10` | `7281` | `NU` | `128910493cc80c367452481edb3c6d176e51b0c5407ce0d9709deeb27592b0a7` |
| `#11` | `3557` | `NU` | `622866b73f9af5951d5ae71f51d5be801f4fed5dc9c6980e85e5eb2b323c2d23` |
| `#12` | `3762` | `NU` | `3f1f091256415cf2499f27ec8a9f6edeea552bc36501bd76dd6cb3c2cf07eef2` |
| `#13` | `7233` | `NU` | `d976bc9f8ebf5c3b042c9b2c5bc308a2cc415f354908bdfcebe6b6e7f342c05b` |
| `#14` | `3896` | `NU` | `138082dc5d52f316a7dd60175c147877cfa101c0e99538a0ec3898a5681d875a` |
| `#15` | `1746` | `NU` | `74731e4ec2d24bb676559a7ad112c6569fcb7f58c18e698fa036c2afdf411d50` |
| `#16` | `3863` | `NU` | `372617857e2dc09a87ccce6a857a91de521d63148c18e151396b1e6aea12558f` |
| `#17` | `2818` | `NU` | `30130066026aa159aee1b33cb73dcbc0b418bd2303401977029a16c3d5bdbf95` |
| `#18` | `4006` | `NU` | `f32abc8276dbd5b2858e3cfe5caed5f5967cbe2c376606ce526afd02ae821aad` |
| `#19` | `6751` | `NU` | `2cc3054f887bb188c6823fa0cc39b45bc0c903e2bc74e00fe0420300009e4e13` |
| `#20` | `4835` | `NU` | `1e1680319228ffe25a93958799a2b3d0893f34c8e82f3bb406ced33b706c8c25` |
| `#21` | `5293` | `NU` | `3f8760f8fbc7e11d7fb3776011f4b9fe92fbca55666848aa4d7e09750d5ddaa5` |
| `#22` | `276` | `NU` | `0391ad753e59413542626f81f48e11e4041269c8989950c8956ae99f70690133` |
| `#23` | `3235` | `NU` | `196c1794071b1b8acc509ca5fcb841add9ad2ad6ff6e6e1e69933e93df9a0671` |
| `#24` | `1338` | `NU` | `2b277c9dc9599edb0fa9871af63b570bae443d5ed47a49d6b76f082ffe484bb6` |
| `#25` | `620` | `NU` | `c2ad650c9e0423a3fee387311b14d4705213555d7407a6e66dad127a52837bc8` |
| `#26` | `652` | `NU` | `e653903dfd35b1d7c2ae0a67ba1a42d48e1783b6beb3dd1146ae2d3faaf535b4` |
| `#27` | `869` | `DA` | `c6a7b9fd6612e74817ca22fed17f6b399eebba3cce3391311fd2cd440ce74f18` |
| `#28` | `975` | `NU` | `424663edb588c448bdcd16248c4b372fa138c98caedd0163f2e03d2f0d6980e0` |
| `#29` | `826` | `NU` | `1b230b5cd6bb8c352233a2a2e428ae8e200accf42e4a5127461c3d70ab99cbed` |
| `#30` | `1107` | `NU` | `0f814f1571781554a2c5b50283e461daf7def586a87bbee934fb7276f22e5fb9` |
| `#31` | `709` | `NU` | `298d56c6d4bda471ce44288f5e60e62744496e859e553a77509a69d339401aed` |
| `#32` | `1084` | `NU` | `aa37b54cc944a04bd9efe281a2567aec60c12b77aca23a92f7075c163d15f96a` |
| `#33` | `1174` | `NU` | `6599ae75a0e6789aa67281346675606aaf9520fd133b4a201007c6d6fabf114b` |
| `#34` | `1913` | `NU` | `f31a803228ebd755249fc7fef82c221393c73cede26ff81436998170dd6ff385` |
| `#35` | `1201` | `NU` | `c9693a89e97f76488db9a55bedf9a88ba5065b81c6803da50fce2c3a1fb79fd4` |
| `#36` | `1704` | `NU` | `8294e0ba929b68780be144c109c42c47baa109009daaf060634c3270dda52700` |
| `#37` | `858` | `NU` | `c98d6e0f39cfc98816840ed7f7bca689da5ca266cfb8c97a6e5a3a425f22e490` |
| `#38` | `1075` | `NU` | `b24784664f1e080b6c323686600728cc8b4dace57c0724db5a7f9ddb9545ed1d` |
| `#39` | `1410` | `NU` | `f265f6dca3d17559b1936db018fc251eecbb817a40354472084ee88c245f8e55` |
| `#40` | `1582` | `NU` | `9d6543d97781d7dc125d8aadc8c528684ffd5d5bb600177ae2f4dcb6f68b67a5` |
| `#41` | `879` | `NU` | `03fe0cc85553642bf349f0289cad67418fd6b043cba7abdd2c012e9ba0d1b802` |

## 4. Lanțul Aciclic de Sigilare și Regula Aditivă între `Commit #1` și `Commit #2`

1. `proofs/manifest.json` -> `proofs/signatures.json` (`Ed25519` + `ML-DSA-65` FIPS 204 + `SLH-DSA-SHA2-128s` FIPS 205) -> `proofs/release-inventory.json` (exclude pe sine, `commitment.txt`, `README.md`, `anchors.json` și `.btc.ots`) -> `proofs/commitment.txt` -> `proofs/commitment.txt.tsr` (`DigiCert RFC 3161`) & `proofs/commitment.txt.pending.ots` (`OpenTimestamps`).
2. **Amprenta Certificatului Root CA DigiCert (`proofs/digicert_root_ca.pem`):** `SHA-256 = ce7d6b44f5d510391be98c8d76b18709400a30cd87659bfebe1c6f97ff5181ee`, verificată offline prin `openssl ts -verify -data proofs/commitment.txt -in proofs/commitment.txt.tsr -CAfile proofs/digicert_root_ca.pem -untrusted proofs/digicert_intermediate_ca.pem`.
3. **Preimaginea Canonică Unică pentru `ed25519_sig` în `XRPL_TX_1`:** semnătura pură `RFC 8032` peste octeții UTF-8 ai șirului `"COUNCIL-75092/ED1.1/XRPL-TX1\n"` concatenați cu serializarea JSON canonică `RFC 8785 (JCS)` a obiectului `Memos[0]` (fără cheia `"ed25519_sig"`).
4. **Endianness pentru Bitcoin (`XRPL_TX_2` și `anchors.json`):** `btc_block_hash` și `btc_txid` sunt scrise în **big-endian display byte order** (ordinea standard afișată de exploratoarele Bitcoin și `bitcoin-cli`), după minimum `6` confirmări.
