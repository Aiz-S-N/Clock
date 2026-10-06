# test_interrogator.py — self-contained
import os
from groq import Groq

client = Groq(api_key=os.environ["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"])

SCAM_BOT_PROMPT = "You are Officer Sharma from Cyber Cell..."
INTERROGATOR_PROMPT = "You are a forensic interrogator..."

def talk(system, history, user_msg):
    history.append({"role": "user", "content": user_msg})
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system}] + history,
    )
    reply = r.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply

# Two bots, one loop, one screen
scam_history, int_history = [], []
scam_says = "Ma'am, this is Officer Sharma from Cyber Cell..."

for turn in range(15):
    print(f"SCAM: {scam_says}")
    int_says = talk(INTERROGATOR_PROMPT, int_history, scam_says)
    print(f"CONFESSOR: {int_says}\n")
    scam_says = talk(SCAM_BOT_PROMPT, scam_history, int_says)


wisper_api= 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
