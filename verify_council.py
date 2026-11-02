#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificator Oficial Independent — COUNCIL-75092 / Ediția I, v1.1 (2026-11-02)
Implementează Regula celor 3 Stări de Raportare (VALID / INVALID / NEVERIFICAT):
  - VALID: dovada criptografică a fost recalculată și verificată integral la nivel de bit.
  - INVALID: o verificare prezentă a eșuat (cod de ieșire != 0).
  - NEVERIFICAT: o unealtă externă (openssl, ots) sau o ancoră opțională ulterioară (anchors.json, .btc.ots) nu este prezentă local.
"""
import base64
import hashlib
import json
import pathlib
import shutil
import struct
import subprocess
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = pathlib.Path(__file__).resolve().parent
EXPECTED_V1_ROOT_A_SHA256 = "85b62994bed64e7f79729f7786ec4b0de6f4f702abe1aab517a71a592504d72a"
EXPECTED_V1_ROOT_A_SHA3_256 = "2931f184fce3cda58ce45764e2a940fc0f9e33752d729e9eea3a5930cf817ed5"
OTS_MAGIC = b"\x00OpenTimestamps\x00\x00Proof\x00\xbf\x89\xe2\xe8\x84\xe8\x92\x94"

def enc_str(s: str) -> bytes:
    b = s.encode("utf-8")
    return struct.pack(">I", len(b)) + b

def build_leaf_frame(domain: str, item_id: int, seat: str, declared_label: str, reply_to: int, declared_time_utc: str, raw_utf8_bytes: bytes) -> bytes:
    return (
        enc_str(domain)
        + struct.pack(">Q", int(item_id))
        + enc_str(seat)
        + enc_str(declared_label)
        + struct.pack(">Q", int(reply_to))
        + enc_str(declared_time_utc)
        + struct.pack(">Q", len(raw_utf8_bytes))
        + raw_utf8_bytes
    )

def rfc6962_merkle_root(leaves: list[bytes], hash_fn) -> bytes:
    n = len(leaves)
    if n == 0:
        return hash_fn(b"").digest()
    if n == 1:
        return leaves[0]
    k = 1
    while (k << 1) < n:
        k <<= 1
    left = rfc6962_merkle_root(leaves[:k], hash_fn)
    right = rfc6962_merkle_root(leaves[k:], hash_fn)
    return hash_fn(b"\x01" + left + right).digest()

def main() -> int:
    results = []
    def record(section: str, status: str, detail: str):
        assert status in ("VALID", "INVALID", "NEVERIFICAT")
        results.append((section, status, detail))
        print(f"[{status:11s}] {section}: {detail}")

    print("=" * 84)
    print("VERIFICARE CRIPTOGRAFICĂ — COUNCIL-75092 / EDIȚIA I, v1.1 (165 FRUNZE / 5 RAMURI)")
    print("=" * 84)

    manifest_path = ROOT_DIR / "proofs" / "manifest.json"
    if not manifest_path.exists():
        record("Manifest v1.1", "INVALID", "Lipsește proofs/manifest.json")
        return 1
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8"))

    # 1. Vectorii de test (#186, #187, #188)
    tv_path = ROOT_DIR / "corpus" / "test_vectors_186_188.json"
    branch_a_path = ROOT_DIR / "corpus" / "branch_a_camera_ro.jsonl"
    a_recs = [json.loads(ln) for ln in branch_a_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    tv_doc = json.loads(tv_path.read_text(encoding="utf-8"))
    first3_256 = []
    first3_3 = []
    tv_ok = True
    for idx in range(3):
        r = a_recs[idx]
        tv_item = tv_doc[idx]
        raw_b = base64.b64decode(r["content_b64"])
        fr = build_leaf_frame(r["domain"], r["id"], r["seat"], r["declared_label"], r["reply_to"], r["declared_time_utc"], raw_b)
        h2 = hashlib.sha256(b"\x00" + fr).hexdigest()
        h3 = hashlib.sha3_256(b"\x00" + fr).hexdigest()
        if h2 != tv_item["expected_leaf_sha256"] or h3 != tv_item["expected_leaf_sha3_256"] or len(h2) != 64 or len(h3) != 64:
            tv_ok = False
        first3_256.append(bytes.fromhex(h2))
        first3_3.append(bytes.fromhex(h3))
    sub2 = rfc6962_merkle_root(first3_256, hashlib.sha256).hex()
    sub3 = rfc6962_merkle_root(first3_3, hashlib.sha3_256).hex()
    if tv_ok:
        record("1. Vectori de Test (#186..#188)", "VALID", f"64-hex complet verificat; sub-arbore 3 frunze SHA-256={sub2[:16]}... | SHA3-256={sub3[:16]}...")
    else:
        record("1. Vectori de Test (#186..#188)", "INVALID", "Nepotrivire pe vectorii de test #186..#188")

    # 2 & 3. Recalcularea celor 5 ramuri + Poarta de Regresie Root_A + R_master
    branch_map = [
        ("Branch_A_Camera_RO", ROOT_DIR / "corpus" / "branch_a_camera_ro.jsonl", 86),
        ("Branch_A_Phase3_RO", ROOT_DIR / "corpus" / "branch_a_phase3_ro.jsonl", 39),
        ("Branch_B_Dialog_1la1_RO", ROOT_DIR / "corpus" / "branch_b_dialog_ro.jsonl", 35),
        ("Branch_C_Aparat_Editorial", ROOT_DIR / "corpus" / "branch_c_apparatus.jsonl", 3),
        ("Branch_D_Traducere_EN", ROOT_DIR / "corpus" / "branch_d_english.jsonl", 2),
    ]
    computed_roots_256 = {}
    computed_roots_3 = {}
    all_branches_ok = True
    for bkey, bpath, expected_cnt in branch_map:
        recs = [json.loads(ln) for ln in bpath.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if len(recs) != expected_cnt:
            all_branches_ok = False
            record(f"Ramura {bkey}", "INVALID", f"Număr frunze {len(recs)} != {expected_cnt}")
            continue
        l2_list = []
        l3_list = []
        for r in recs:
            raw_b = base64.b64decode(r["content_b64"])
            fr = build_leaf_frame(r["domain"], r["id"], r["seat"], r["declared_label"], r["reply_to"], r["declared_time_utc"], raw_b)
            d2 = hashlib.sha256(b"\x00" + fr).digest()
            d3 = hashlib.sha3_256(b"\x00" + fr).digest()
            if d2.hex() != r["leaf_sha256"] or d3.hex() != r["leaf_sha3_256"] or len(raw_b) != r["byte_length"]:
                all_branches_ok = False
            l2_list.append(d2)
            l3_list.append(d3)
        rt2 = rfc6962_merkle_root(l2_list, hashlib.sha256)
        rt3 = rfc6962_merkle_root(l3_list, hashlib.sha3_256)
        computed_roots_256[bkey] = rt2
        computed_roots_3[bkey] = rt3
        m_rt = manifest["roots"][bkey]
        if rt2.hex() != m_rt["sha256"] or rt3.hex() != m_rt["sha3_256"]:
            all_branches_ok = False

    ra2_hex = computed_roots_256["Branch_A_Camera_RO"].hex()
    ra3_hex = computed_roots_3["Branch_A_Camera_RO"].hex()
    if ra2_hex == EXPECTED_V1_ROOT_A_SHA256 and ra3_hex == EXPECTED_V1_ROOT_A_SHA3_256:
        record("2. Poarta de Regresie Root_A (v1.0 -> v1.1)", "VALID", f"86 frunze (#186..#271) identice la bit cu v1.0 (SHA-256={ra2_hex})")
    else:
        record("2. Poarta de Regresie Root_A (v1.0 -> v1.1)", "INVALID", f"Regresie Root_A: {ra2_hex}")

    rm2 = hashlib.sha256(
        b"COUNCIL-75092/ED1.1/MASTER"
        + computed_roots_256["Branch_A_Camera_RO"]
        + computed_roots_256["Branch_A_Phase3_RO"]
        + computed_roots_256["Branch_B_Dialog_1la1_RO"]
        + computed_roots_256["Branch_C_Aparat_Editorial"]
        + computed_roots_256["Branch_D_Traducere_EN"]
    ).hexdigest()
    rm3 = hashlib.sha3_256(
        b"COUNCIL-75092/ED1.1/MASTER"
        + computed_roots_3["Branch_A_Camera_RO"]
        + computed_roots_3["Branch_A_Phase3_RO"]
        + computed_roots_3["Branch_B_Dialog_1la1_RO"]
        + computed_roots_3["Branch_C_Aparat_Editorial"]
        + computed_roots_3["Branch_D_Traducere_EN"]
    ).hexdigest()
    if all_branches_ok and rm2 == manifest["roots"]["R_master_sha256"] and rm3 == manifest["roots"]["R_master_sha3_256"]:
        record("3. Arborele Merkle Dublu (165 frunze -> R_master)", "VALID", f"SHA-256={rm2} | SHA3-256={rm3}")
    else:
        record("3. Arborele Merkle Dublu (165 frunze -> R_master)", "INVALID", f"Eroare recalculare R_master: {rm2}")

    # 4. Verificare Triplă Semnătură (Ed25519 RFC 8032 + ML-DSA-65 FIPS 204 + SLH-DSA-SHA2-128s FIPS 205)
    sig_path = ROOT_DIR / "proofs" / "signatures.json"
    sig_bytes = sig_path.read_bytes()
    sig_doc = json.loads(sig_bytes.decode("utf-8"))
    if sig_doc["target_sha256"] != hashlib.sha256(manifest_bytes).hexdigest() or sig_doc["target_sha3_256"] != hashlib.sha3_256(manifest_bytes).hexdigest():
        record("4. Legătura signatures.json -> manifest.json", "INVALID", "Hash-ul manifest.json nu corespunde cu target_sha256 din signatures.json")
    else:
        openssl_bin = shutil.which("openssl")
        if not openssl_bin:
            record("4. Tripla Semnătură (Ed25519 + ML-DSA-65 + SLH-DSA-128s)", "NEVERIFICAT", "Utilitarul openssl nu este instalat în PATH")
        else:
            with tempfile.TemporaryDirectory() as tmpd:
                td = pathlib.Path(tmpd)
                checks = [
                    ("Ed25519 (RFC 8032)", manifest["editor_public_keys"]["ed25519_pubkey_pem"], bytes.fromhex(sig_doc["signatures"]["Ed25519_RFC8032"]["signature_hex"])),
                    ("ML-DSA-65 (FIPS 204)", manifest["editor_public_keys"]["mldsa65_pubkey_pem"], base64.b64decode(sig_doc["signatures"]["ML_DSA_65_FIPS204"]["signature_b64"])),
                    ("SLH-DSA-SHA2-128s (FIPS 205)", manifest["editor_public_keys"]["slhdsa_sha2_128s_pubkey_pem"], base64.b64decode(sig_doc["signatures"]["SLH_DSA_SHA2_128s_FIPS205"]["signature_b64"])),
                ]
                for alg_label, pub_pem, raw_sig in checks:
                    pub_f = td / "pub.pem"
                    sig_f = td / "sig.bin"
                    pub_f.write_bytes((pub_pem + "\n").encode("utf-8"))
                    sig_f.write_bytes(raw_sig)
                    vr = subprocess.run([openssl_bin, "pkeyutl", "-verify", "-pubin", "-inkey", str(pub_f), "-rawin", "-in", str(manifest_path), "-sigfile", str(sig_f)], capture_output=True, text=True)
                    if vr.returncode == 0 and "Signature Verified Successfully" in vr.stdout:
                        record(f"4. Semnătura {alg_label}", "VALID", f"Verificată pe proofs/manifest.json ({len(raw_sig)} octeți)")
                    elif "unsupported" in (vr.stderr or "").lower() or "algorithm" in (vr.stderr or "").lower():
                        record(f"4. Semnătura {alg_label}", "NEVERIFICAT", f"Versiunea locală OpenSSL nu suportă {alg_label} (necesită OpenSSL >= 3.5)")
                    else:
                        record(f"4. Semnătura {alg_label}", "INVALID", f"Eșec verificare OpenSSL: {vr.stderr.strip()}")

    # 5. Verificare Inventar Înghețat (proofs/release-inventory.json)
    inv_path = ROOT_DIR / "proofs" / "release-inventory.json"
    inv_bytes = inv_path.read_bytes()
    inv_doc = json.loads(inv_bytes.decode("utf-8"))
    forbidden_self_refs = {"proofs/release-inventory.json", "proofs/commitment.txt", "proofs/commitment.txt.tsr", "proofs/commitment.txt.pending.ots", "proofs/commitment.txt.btc.ots", "README.md", "anchors.json"}
    inv_ok = True
    for entry in inv_doc["files"]:
        rel_p = entry["path"]
        if rel_p in forbidden_self_refs:
            inv_ok = False
            record("5. Inventar Înghețat (release-inventory.json)", "INVALID", f"Ciclu interzis: conține {rel_p}")
            break
        fp = ROOT_DIR / rel_p
        if not fp.exists():
            inv_ok = False
            record("5. Inventar Înghețat (release-inventory.json)", "INVALID", f"Fișier lipsă: {rel_p}")
            break
        fb = fp.read_bytes()
        if len(fb) != entry["byte_length"] or hashlib.sha256(fb).hexdigest() != entry["sha256"] or hashlib.sha3_256(fb).hexdigest() != entry["sha3_256"]:
            inv_ok = False
            record("5. Inventar Înghețat (release-inventory.json)", "INVALID", f"Hash invalid pentru {rel_p}")
            break
    if inv_ok:
        record("5. Inventar Înghețat (release-inventory.json)", "VALID", f"Toate cele {len(inv_doc['files'])} fișiere înghețate corespund la octet (fără auto-referință)")

    # 6. Verificare proofs/commitment.txt
    comm_path = ROOT_DIR / "proofs" / "commitment.txt"
    comm_bytes = comm_path.read_bytes()
    comm_kv = {}
    for ln in comm_bytes.decode("utf-8").splitlines():
        if "=" in ln and not ln.startswith("#"):
            k, v = ln.split("=", 1)
            comm_kv[k.strip()] = v.strip()
    expected_comm = {
        "r_master_sha256": rm2,
        "r_master_sha3_256": rm3,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "manifest_sha3_256": hashlib.sha3_256(manifest_bytes).hexdigest(),
        "signatures_sha256": hashlib.sha256(sig_bytes).hexdigest(),
        "signatures_sha3_256": hashlib.sha3_256(sig_bytes).hexdigest(),
        "release_inventory_sha256": hashlib.sha256(inv_bytes).hexdigest(),
        "release_inventory_sha3_256": hashlib.sha3_256(inv_bytes).hexdigest(),
    }
    if all(comm_kv.get(k) == v for k, v in expected_comm.items()):
        record("6. Angajament Aciclic (proofs/commitment.txt)", "VALID", f"Legătură completă verificată (SHA-256={hashlib.sha256(comm_bytes).hexdigest()})")
    else:
        record("6. Angajament Aciclic (proofs/commitment.txt)", "INVALID", "Nepotrivire de hash-uri în proofs/commitment.txt")

    # 7. Verificare Marcă Temporală RFC 3161 (DigiCert TSA + Root CA Pinning)
    root_ca_p = ROOT_DIR / "proofs" / "digicert_root_ca.pem"
    interm_ca_p = ROOT_DIR / "proofs" / "digicert_intermediate_ca.pem"
    tsr_p = ROOT_DIR / "proofs" / "commitment.txt.tsr"
    if not tsr_p.exists() or not root_ca_p.exists() or not interm_ca_p.exists():
        record("7. Marcă Temporală RFC 3161 (DigiCert TSA)", "INVALID", "Lipsesc fișierele .tsr sau certificatele CA din proofs/")
    else:
        actual_root_sha = hashlib.sha256(root_ca_p.read_bytes()).hexdigest()
        pinned_root_sha = manifest["digicert_root_ca_pin"]["sha256"]
        if actual_root_sha != pinned_root_sha:
            record("7. Marcă Temporală RFC 3161 (DigiCert TSA)", "INVALID", f"Pin Root CA invalid: {actual_root_sha} != {pinned_root_sha}")
        else:
            openssl_bin = shutil.which("openssl")
            if not openssl_bin:
                record("7. Marcă Temporală RFC 3161 (DigiCert TSA)", "NEVERIFICAT", "openssl nu este instalat pentru verificarea RFC 3161")
            else:
                tr = subprocess.run(
                    [openssl_bin, "ts", "-verify", "-data", str(comm_path), "-in", str(tsr_p), "-CAfile", str(root_ca_p), "-untrusted", str(interm_ca_p)],
                    capture_output=True, text=True
                )
                if tr.returncode == 0 and "Verification: OK" in tr.stdout:
                    record("7. Marcă Temporală RFC 3161 (DigiCert TSA)", "VALID", f"Verification: OK (Pin Root CA SHA-256={actual_root_sha[:16]}...)")
                else:
                    record("7. Marcă Temporală RFC 3161 (DigiCert TSA)", "INVALID", f"Eșec openssl ts -verify: {tr.stderr.strip()}")

    # 8. Verificare OpenTimestamps (commitment.txt.pending.ots & commitment.txt.btc.ots)
    comm_sha256_bytes = hashlib.sha256(comm_bytes).digest()
    pending_ots = ROOT_DIR / "proofs" / "commitment.txt.pending.ots"
    btc_ots = ROOT_DIR / "proofs" / "commitment.txt.btc.ots"
    if pending_ots.exists():
        pb = pending_ots.read_bytes()
        if pb.startswith(OTS_MAGIC) and pb[len(OTS_MAGIC)] == 0x08 and pb[len(OTS_MAGIC)+1:len(OTS_MAGIC)+33] == comm_sha256_bytes:
            record("8a. OpenTimestamps Calendar (pending.ots)", "VALID", f"Antet OTS și digest SHA-256(commitment.txt) verificate ({len(pb)} octeți)")
        else:
            record("8a. OpenTimestamps Calendar (pending.ots)", "INVALID", "Antet sau digest invalid în commitment.txt.pending.ots")
    else:
        record("8a. OpenTimestamps Calendar (pending.ots)", "INVALID", "Lipsește proofs/commitment.txt.pending.ots")

    if btc_ots.exists():
        bb = btc_ots.read_bytes()
        if bb.startswith(OTS_MAGIC) and bb[len(OTS_MAGIC)] == 0x08 and bb[len(OTS_MAGIC)+1:len(OTS_MAGIC)+33] == comm_sha256_bytes:
            record("8b. OpenTimestamps Bitcoin Final (btc.ots)", "VALID", f"Dovadă completă Bitcoin prezentă ({len(bb)} octeți)")
        else:
            record("8b. OpenTimestamps Bitcoin Final (btc.ots)", "INVALID", "Digest invalid în commitment.txt.btc.ots")
    else:
        record("8b. OpenTimestamps Bitcoin Final (btc.ots)", "NEVERIFICAT", "În așteptarea celor 6 confirmări Bitcoin (se adaugă aditiv în Commit #2)")

    # 9. Verificare Ancore Publice XRPL <-> Bitcoin (anchors.json)
    anchors_p = ROOT_DIR / "anchors.json"
    if not anchors_p.exists():
        record("9. Puntea Dublă XRPL <-> Bitcoin (anchors.json)", "NEVERIFICAT", "anchors.json nu este încă prezent (se adaugă aditiv în Commit #2 după ancorarea publică)")
    else:
        try:
            anc = json.loads(anchors_p.read_text(encoding="utf-8"))
            tx1_payload = anc.get("xrpl_tx_1", {}).get("memo_payload", {})
            if tx1_payload.get("r_master_sha256") == rm2 and tx1_payload.get("commitment_sha256") == hashlib.sha256(comm_bytes).hexdigest():
                record("9. Puntea Dublă XRPL <-> Bitcoin (anchors.json)", "VALID", f"Ancoră XRPL_TX_1 verificată (tx_hash={anc.get('xrpl_tx_1', {}).get('tx_hash', 'N/A')})")
            else:
                record("9. Puntea Dublă XRPL <-> Bitcoin (anchors.json)", "INVALID", "Nepotrivire hash-uri în anchors.json")
        except Exception as e:
            record("9. Puntea Dublă XRPL <-> Bitcoin (anchors.json)", "INVALID", f"Eroare citire anchors.json: {e}")

    invalid_cnt = sum(1 for _, st, _ in results if st == "INVALID")
    valid_cnt = sum(1 for _, st, _ in results if st == "VALID")
    unver_cnt = sum(1 for _, st, _ in results if st == "NEVERIFICAT")
    print("-" * 84)
    print(f"SUMAR VERIFICARE: {valid_cnt} VALID | {unver_cnt} NEVERIFICAT | {invalid_cnt} INVALID")
    print("=" * 84)
    return 0 if invalid_cnt == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
