# CLOCK
### Cognitive Layer for Objective Call Kognition

> A real-time decision engine that helps victims of AI voice scams
> break out of emotional hijacking before they send money.

---

## The Problem

Modern scams no longer rely on bad grammar or obvious lies.
They rely on **emotional hijacking**.

A victim receives a call. The voice sounds *exactly* like their child,
their grandchild, or their boss — crying, panicking, begging for money.
The brain shuts down. Logic stops. The scammer wins.

Three things make this possible today:

1. **Audio Deception** — AI voice cloning is now indistinguishable from real voices.
2. **Number Spoofing** — Caller ID can be faked to look like a family member's phone.
3. **The Isolation Wall** — Victims are told "don't hang up or they'll get hurt,"
   preventing them from verifying the truth with anyone else.

Existing tools try to detect fake audio. That is a losing race —
scammers change their voice tech every few months.

---

## Our Approach

We shift the defense **from audio analysis to behavioral analysis.**

Scammers can change their voice. They cannot change their behavior.
They *must* create urgency. They *must* demand untraceable payment.
They *must* isolate the victim.

CLOCK watches for those behaviors — and then fights back.

---

## What CLOCK Does

CLOCK is a lightweight dashboard with two halves:

### 1. The Shield — Real-Time Objectivity
The victim (or a family member) feeds the call text into CLOCK.
The system acts as a calm observer and produces a **Threat Level Index** —
a clear percentage that says "this is 90% likely a scam" — based purely on
behavioral red flags, not on voice.

### 2. The Sword — CONFESSOR Engine
Once a threat is confirmed, CLOCK doesn't just warn — it engages.
An adversarial AI begins a structured interrogation of the scammer,
using contradiction traps and reverse Turing tests to force the bot
to break character. When it does, CLOCK records an **AI Confession Report**.

---

## The Three Tools

| Tool | Purpose |
|---|---|
| **Threat Level Index** | Offloads the panic. Gives the user a clear, objective risk score. |
| **Behavioral Pattern Matcher** | Flags urgency, payment demand, and isolation in red. |
| **Out-of-Band Verification** | Breaks the Isolation Wall by prompting a safe-word check on a separate channel. |

---

## Tech Stack

- **Frontend:** Streamlit
- **LLM:** Groq — Llama 3.3 70B (interrogation + classification)
- **Transcription:** Groq — Whisper Large v3 Turbo (optional)
- **Storage:** Local SQLite + SHA-256 hashed transcripts
- **Export:** Auto-generated PDF Confession Report

---

## What CLOCK Is Not

- It is **not** a voice deepfake detector.
- It is **not** a replacement for reporting to authorities.
- It is **not** a general-purpose scam filter.

It is a **decision engine for one specific moment** — the moment a victim
is being pressured to act against their own interest.
