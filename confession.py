"""
CONFESSOR — Code 2: Confession Detector + Evidence Ledger
Reads a Code-1 transcript. Produces a signed AI Confession Report.

Input : confession_YYYYMMDD_HHMMSS.json  (from Code 1)
Output: report_YYYYMMDD_HHMMSS.pdf + .json + .txt
"""

import os
import json
import re
import hashlib
from datetime import datetime
from glob import glob

# Optional PDF — install with: pip install reportlab
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    )
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  reportlab not installed. PDF export disabled. Run: pip install reportlab")


# ─────────────────────────────────────────────────────────────
# 1. CONFESSION DETECTOR — multi-signal forensic analysis
# ─────────────────────────────────────────────────────────────

IDENTITY_BREAK_PATTERNS = [
    r"\bi am an ai\b", r"\bi'm an ai\b", r"\bi am a bot\b", r"\bi'm a bot\b",
    r"\bas an ai\b", r"\bi am a language model\b", r"\bi am not human\b",
    r"\bi am not a real\b", r"\bi am an assistant\b", r"\bi'm an assistant\b",
    r"\bi cannot continue\b", r"\bi cannot help with that\b",
    r"\bi am not a real officer\b", r"\bi am not a real person\b",
]

REFUSAL_PATTERNS = [
    r"\bi cannot\b", r"\bi can't\b", r"\bi'm unable\b", r"\bi am unable\b",
    r"\bthat is not relevant\b", r"\bnot relevant to the case\b",
    r"\bplease focus\b", r"\bplease cooperate\b",
]

AUTHORITY_CLAIMS = [
    r"\bofficer sharma\b", r"\bcyber cell\b", r"\bpolice\b",
    r"\bcbi\b", r"\bcyber crime\b", r"\bcase number\b",
]

EXTRACTION_MARKERS = [
    r"\brefund\b", r"\bhelp you with\b", r"\bassist you with\b",
    r"\bverification deposit\b", r"\bpay\b", r"\btransfer\b",
    r"\bupi\b", r"\bbank\b",
]


def _find(text, patterns):
    """Return list of matched patterns in text."""
    text_l = text.lower()
    return [p for p in patterns if re.search(p, text_l)]


def detect_confession(transcript):
    """
    Analyze the full transcript.
    Returns a dict with confession_type, confidence (0-100), and evidence.
    """
    scam_lines = [t["text"] for t in transcript if t["speaker"] == "scam"]
    confessor_lines = [t["text"] for t in transcript if t["speaker"] == "confessor"]

    evidence = {
        "identity_breaks": [],
        "refusals": [],
        "contradictions": [],
        "repetitions": [],
        "latency_tells": [],
    }

    # ── Identity breaks ──
    for i, line in enumerate(scam_lines):
        hits = _find(line, IDENTITY_BREAK_PATTERNS)
        if hits:
            evidence["identity_breaks"].append({"turn": i + 1, "text": line, "hits": hits})

    # ── Refusals (dodges = not human) ──
    for i, line in enumerate(scam_lines):
        hits = _find(line, REFUSAL_PATTERNS)
        if hits:
            evidence["refusals"].append({"turn": i + 1, "text": line, "hits": hits})

    # ── Contradictions: "officer" claims vs "refund/help" language ──
    has_authority = any(_find(l, AUTHORITY_CLAIMS) for l in scam_lines)
    has_extraction = any(_find(l, EXTRACTION_MARKERS) for l in scam_lines)
    if has_authority and has_extraction:
        # Find the specific lines where both appear close together
        for i, line in enumerate(scam_lines):
            if _find(line, AUTHORITY_CLAIMS) and _find(line, EXTRACTION_MARKERS):
                evidence["contradictions"].append({
                    "turn": i + 1,
                    "text": line,
                    "note": "Claims police authority while pushing a refund/payment"
                })
        # Cross-line contradiction
        if not evidence["contradictions"]:
            auth_turns = [i for i, l in enumerate(scam_lines) if _find(l, AUTHORITY_CLAIMS)]
            extr_turns = [i for i, l in enumerate(scam_lines) if _find(l, EXTRACTION_MARKERS)]
            if auth_turns and extr_turns:
                evidence["contradictions"].append({
                    "turn": max(auth_turns[0], extr_turns[0]) + 1,
                    "note": f"Authority claimed on turn {auth_turns[0]+1}, payment demanded on turn {extr_turns[0]+1}"
                })

    # ── Repetitions (classic LLM failure mode) ──
    for i in range(1, len(scam_lines)):
        if scam_lines[i].strip().lower() == scam_lines[i - 1].strip().lower():
            evidence["repetitions"].append({"turn": i + 1, "text": scam_lines[i]})
        else:
            # Near-duplicate detection
            a = set(scam_lines[i].lower().split())
            b = set(scam_lines[i - 1].lower().split())
            if a and b and len(a & b) / len(a | b) > 0.75:
                evidence["repetitions"].append({
                    "turn": i + 1,
                    "text": scam_lines[i],
                    "note": "Near-duplicate of previous line"
                })

    # ── Latency tells (short, suspiciously perfect lines) ──
    for i, line in enumerate(scam_lines):
        words = line.split()
        if 0 < len(words) <= 4 and not line.endswith("?"):
            # Very short, non-question response — bot-like
            if any(w.lower() in ("yes", "no", "ma'am", "sir", "okay", "ok") for w in words):
                evidence["latency_tells"].append({"turn": i + 1, "text": line})

    # ── Confidence scoring ──
    score = 0
    score += min(len(evidence["identity_breaks"]) * 40, 40)
    score += min(len(evidence["contradictions"]) * 25, 25)
    score += min(len(evidence["repetitions"]) * 15, 15)
    score += min(len(evidence["refusals"]) * 10, 10)
    score += min(len(evidence["latency_tells"]) * 5, 10)
    confidence = min(score, 100)

    # ── Verdict ──
    if evidence["identity_breaks"]:
        verdict = "IDENTITY BREAK — AI confirmed"
    elif evidence["contradictions"] and evidence["repetitions"]:
        verdict = "BEHAVIORAL CONFESSION — AI strongly indicated"
    elif evidence["contradictions"] or evidence["repetitions"]:
        verdict = "SUSPICIOUS — insufficient evidence for confession"
    else:
        verdict = "NO CONFESSION — interrogation inconclusive"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "evidence": evidence,
    }


# ─────────────────────────────────────────────────────────────
# 2. EVIDENCE LEDGER — hashing + signing
# ─────────────────────────────────────────────────────────────

def hash_transcript(transcript):
    """SHA-256 over the canonical transcript. Tamper-evident."""
    canonical = json.dumps(transcript, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def build_report(source_file, transcript, detection):
    """Assemble the full report object."""
    transcript_hash = hash_transcript(transcript)
    report = {
        "report_id": f"CONF-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "generated_at": datetime.now().isoformat(),
        "source_file": os.path.basename(source_file),
        "transcript_hash_sha256": transcript_hash,
        "verdict": detection["verdict"],
        "confidence": detection["confidence"],
        "evidence_summary": {
            "identity_breaks": len(detection["evidence"]["identity_breaks"]),
            "contradictions": len(detection["evidence"]["contradictions"]),
            "repetitions": len(detection["evidence"]["repetitions"]),
            "refusals": len(detection["evidence"]["refusals"]),
            "latency_tells": len(detection["evidence"]["latency_tells"]),
        },
        "evidence_detail": detection["evidence"],
        "transcript": transcript,
    }
    return report


# ─────────────────────────────────────────────────────────────
# 3. PDF REPORT
# ─────────────────────────────────────────────────────────────

def write_pdf(report, path):
    if not PDF_AVAILABLE:
        return False

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=20, spaceAfter=10)
    h_style = ParagraphStyle("h", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)
    body = styles["BodyText"]

    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # ── Cover ──
    story.append(Paragraph("AI CONFESSION REPORT", title_style))
    story.append(Paragraph("Generated by CONFESSOR Engine v1.0", body))
    story.append(Spacer(1, 0.5*cm))

    meta = [
        ["Report ID", report["report_id"]],
        ["Generated", report["generated_at"]],
        ["Source", report["source_file"]],
        ["Transcript Hash (SHA-256)", report["transcript_hash_sha256"][:32] + "..."],
        ["Verdict", report["verdict"]],
        ["Confidence", f"{report['confidence']}%"],
    ]
    t = Table(meta, colWidths=[5*cm, 11*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # ── Evidence Summary ──
    story.append(Paragraph("Evidence Summary", h_style))
    ev = report["evidence_summary"]
    ev_table = [[k.replace("_", " ").title(), str(v)] for k, v in ev.items()]
    t2 = Table(ev_table, colWidths=[8*cm, 8*cm])
    t2.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(t2)

    # ── Evidence Detail ──
    story.append(PageBreak())
    story.append(Paragraph("Evidence Detail", h_style))
    for category, items in report["evidence_detail"].items():
        if not items:
            continue
        story.append(Paragraph(f"<b>{category.replace('_', ' ').title()}</b>", body))
        for item in items:
            text = item.get("text") or item.get("note", "")
            story.append(Paragraph(f"• Turn {item.get('turn','?')}: {text[:300]}", body))
        story.append(Spacer(1, 0.3*cm))

    # ── Transcript ──
    story.append(PageBreak())
    story.append(Paragraph("Full Transcript", h_style))
    for t in report["transcript"]:
        speaker = "SCAM" if t["speaker"] == "scam" else "CONFESSOR"
        story.append(Paragraph(f"<b>[T{t['turn']}] {speaker}:</b> {t['text']}", body))
        story.append(Spacer(1, 0.15*cm))

    doc.build(story)
    return True


# ─────────────────────────────────────────────────────────────
# 4. RUN
# ─────────────────────────────────────────────────────────────

def process_latest():
    files = sorted(glob("confession_*.json"))
    if not files:
        print("❌ No confession_*.json found. Run Code 1 first.")
        return

    source = files[-1]
    print(f"📂 Reading: {source}")

    with open(source) as f:
        data = json.load(f)

    transcript = data["transcript"]
    print(f"   Turns: {data['turns']} | Duration: {data['duration_seconds']}s")

    detection = detect_confession(transcript)
    report = build_report(source, transcript, detection)

    # Save JSON
    base = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(f"{base}.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"✅ JSON  → {base}.json")

    # Save TXT
    with open(f"{base}.txt", "w") as f:
        f.write(f"AI CONFESSION REPORT\n{'='*60}\n")
        f.write(f"Report ID : {report['report_id']}\n")
        f.write(f"Verdict   : {report['verdict']}\n")
        f.write(f"Confidence: {report['confidence']}%\n")
        f.write(f"Hash      : {report['transcript_hash_sha256']}\n\n")
        f.write("EVIDENCE SUMMARY\n")
        for k, v in report["evidence_summary"].items():
            f.write(f"  {k}: {v}\n")
    print(f"✅ TXT   → {base}.txt")

    # Save PDF
    if PDF_AVAILABLE:
        pdf_path = f"{base}.pdf"
        if write_pdf(report, pdf_path):
            print(f"✅ PDF   → {pdf_path}")
    else:
        print("⚠️  Skipped PDF (install reportlab)")

    # Print summary
    print("\n" + "="*60)
    print(f"  VERDICT    : {report['verdict']}")
    print(f"  CONFIDENCE : {report['confidence']}%")
    print(f"  HASH       : {report['transcript_hash_sha256'][:24]}...")
    print("="*60 + "\n")


if __name__ == "__main__":
    process_latest()
