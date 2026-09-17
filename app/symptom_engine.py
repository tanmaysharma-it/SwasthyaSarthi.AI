"""
Symptom Sahayak — rule-based symptom engine.

Architecture note: `get_reply()` is the ONLY function the router calls.
When an LLM API key becomes available, replace the body of `get_reply()`
with a LangChain call (see the commented example at the bottom) — nothing
in the router or frontend needs to change, since the return shape
{reply, severity, is_emergency} stays the same.
"""
import re
from dataclasses import dataclass

EMERGENCY_KEYWORDS = [
    "chest pain", "seene mein dard", "can't breathe", "saans nahi aa rahi",
    "unconscious", "behosh", "severe bleeding", "bahut khoon", "suicide",
    "heart attack", "dil ka dora", "stroke",
]

# symptom_key: (matching keywords in EN/HI/Hinglish, default severity, response text)
SYMPTOM_RULES = {
    "fever": {
        "keywords": ["fever", "bukhar", "temperature", "garam badan"],
        "severity": "yellow",
        "reply": "Aapko bukhar hai. Kitne din se hai? Agar 3 din se zyada ho ya 102°F se upar ho, toh doctor se milna zaroori hai.",
    },
    "headache": {
        "keywords": ["headache", "sir dard", "sar dard", "migraine"],
        "severity": "green",
        "reply": "Sir dard ke liye aaram karo, paani piyo, aur tez roshni/screen se break lo. Agar dard bahut tez ho ya baar-baar ho raha ho, doctor se check karwa lena.",
    },
    "cough": {
        "keywords": ["cough", "khansi", "khaansi"],
        "severity": "green",
        "reply": "Khansi normal ho sakti hai mausam badalne se. Garam paani/kadha piyo. Agar 2 hafte se zyada rahe ya saans lene mein dikkat ho, toh doctor se milna.",
    },
    "stomach_pain": {
        "keywords": ["stomach pain", "pet dard", "pet mein dard", "abdominal pain"],
        "severity": "yellow",
        "reply": "Pet dard kab se hai aur kya khaane ke baad badhta hai? Halka khana khao aur agar dard tez ho ya ulti/bukhar ke saath ho, doctor se milna better hoga.",
    },
    "chest_pain": {
        "keywords": ["chest pain", "seene mein dard", "chest discomfort"],
        "severity": "red",
        "reply": "Ye emergency ho sakti hai. Turant kisi doctor/hospital se contact karo ya emergency number pe call karo.",
    },
    "cold": {
        "keywords": ["cold", "sardi", "zukaam", "nazla", "runny nose", "naak behna"],
        "severity": "green",
        "reply": "Sardi-zukaam mein garam paani piyo, bhaap lo, aur aaram karo. Agar 5-7 din se zyada rahe, doctor se milna.",
    },
    "sore_throat": {
        "keywords": ["sore throat", "gale mein dard", "gala kharab", "throat pain"],
        "severity": "green",
        "reply": "Gale ki takleef ke liye garam paani mein namak daal ke gargle karo. Agar nigalne mein bahut dikkat ho ya 3 din se zyada rahe, doctor se milna.",
    },
    "body_ache": {
        "keywords": ["body ache", "badan dard", "body pain", "joint pain", "jodo mein dard"],
        "severity": "yellow",
        "reply": "Badan dard ke saath bukhar bhi hai kya? Aaram karo aur paani piyo. Agar dard bahut tez ho ya saath mein bukhar ho, doctor se check karwana.",
    },
    "diarrhea": {
        "keywords": ["diarrhea", "dast", "loose motion", "pet kharab"],
        "severity": "yellow",
        "reply": "ORS ghol piyo aur hydrated raho. Agar 2 din se zyada ho ya khoon dikhe, turant doctor se milna zaroori hai.",
    },
    "vomiting": {
        "keywords": ["vomiting", "ulti", "vomit", "throw up"],
        "severity": "yellow",
        "reply": "Thoda-thoda paani piyo, bhari khana avoid karo. Agar baar-baar ulti ho ya khoon aaye, turant doctor se milna.",
    },
    "dizziness": {
        "keywords": ["dizziness", "chakkar", "chakkar aana", "dizzy"],
        "severity": "yellow",
        "reply": "Baith jao ya let jao turant, paani piyo. Agar baar-baar chakkar aaye ya behoshi jaisa lage, doctor se milna zaroori hai.",
    },
    "skin_rash": {
        "keywords": ["rash", "khujli", "skin allergy", "itching", "daane"],
        "severity": "green",
        "reply": "Khujli/rash ki jagah saaf aur sukhi rakho, tight kapde avoid karo. Agar phailne lage ya sujan ho, doctor se milna.",
    },
    "back_pain": {
        "keywords": ["back pain", "kamar dard", "peeth dard"],
        "severity": "green",
        "reply": "Kamar dard mein aaram karo aur galat posture avoid karo. Agar dard legs mein bhi jaaye ya bahut tez ho, doctor se milna.",
    },
    "breathing_difficulty": {
        "keywords": ["breathing difficulty", "saans lene mein dikkat", "shortness of breath", "saans phoolna"],
        "severity": "red",
        "reply": "Saans ki dikkat serious ho sakti hai. Turant doctor se milo ya emergency contact karo.",
    },
    "fatigue": {
        "keywords": ["fatigue", "thakan", "weakness", "kamzori", "tiredness"],
        "severity": "green",
        "reply": "Poori neend lo, healthy khana khao aur paani piyo. Agar thakan hafton tak rahe, doctor se check karwana better hoga.",
    },
}


@dataclass
class SymptomResponse:
    reply: str
    severity: str  # "red" | "yellow" | "green"
    is_emergency: bool


def _matches_emergency(text: str) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in EMERGENCY_KEYWORDS)


def _find_symptom(text: str):
    text_lower = text.lower()
    for symptom_key, rule in SYMPTOM_RULES.items():
        if any(keyword in text_lower for keyword in rule["keywords"]):
            return symptom_key, rule
    return None, None


def get_reply(message: str) -> SymptomResponse:
    """
    Main entry point. Swap this function's body for an LLM call later —
    the router and frontend only care about the SymptomResponse shape.
    """
    if _matches_emergency(message):
        return SymptomResponse(
            reply="Ye emergency lag rahi hai. Kripya turant nazdeeki hospital jaayein ya emergency helpline (112) par call karein.",
            severity="red",
            is_emergency=True,
        )

    symptom_key, rule = _find_symptom(message)
    if rule:
        return SymptomResponse(reply=rule["reply"], severity=rule["severity"], is_emergency=False)

    return SymptomResponse(
        reply="Samajh nahi paaya, thoda aur detail mein bata sakte ho ki kya problem ho rahi hai?",
        severity="green",
        is_emergency=False,
    )


# ---------------------------------------------------------------
# Future LLM swap-in example (uncomment + adapt when API key ready):
#
# from langchain_anthropic import ChatAnthropic
# llm = ChatAnthropic(model="claude-sonnet-4-6")
#
# def get_reply(message: str) -> SymptomResponse:
#     result = llm.invoke(f"""You are a multilingual (Hindi/English/Hinglish)
#     health triage assistant. Classify severity as red/yellow/green and
#     reply helpfully to: {message}""")
#     # parse result into SymptomResponse and return
# ---------------------------------------------------------------