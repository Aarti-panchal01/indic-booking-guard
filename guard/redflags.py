"""Red-flag phrases that stop a booking and hand the call to a human (or 108).

Source of the sign list: WHO cardiovascular diseases fact sheet, 2025-07-31,
https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)
The Hindi and Kannada phrases are the author's translation, NOT clinically validated.
Cardiac and stroke signs only. A real deployment needs a clinician to own this list.

Policy: over-escalation is cheap (a person calls back), a miss is not. Negation handling
is deliberately narrow, so some negated phrases still escalate.
"""
from __future__ import annotations

import re

# Each entry: (sign, regex). Matched on lowercased text.
RED_FLAGS: list[tuple[str, str]] = [
    # chest pain / discomfort
    ("chest_pain", r"\bchest (?:pain|me dard|mein dard|mai dard|discomfort|tightness|heavy|heaviness|pressure)"),
    ("chest_pain", r"\b(?:seene|seena|sine|seeney|chhati|chaati|chhaati|chati|chest) (?:me|mein|mai|mien)? ?(?:dard|bhaari|bhaaripan|bhaaripan|jakdan|dabav|pain)"),
    ("chest_pain", r"\bpain in (?:my |his |her |the )?chest"),
    ("chest_pain", r"\b(?:ede|edeli|edenalli|yede|yedeli) ?(?:novu|nov|bhaara|bhara|ollage novu)"),
    # breathing
    ("breathing", r"\bsaans (?:lene )?(?:me|mein|mai)? ?(?:takleef|taklif|dikkat|problem|nahi aa)"),
    ("breathing", r"\bsaans (?:phool|ful|fool|ruk|atak)"),
    ("breathing", r"\b(?:difficulty|trouble|problem) breathing\b|\b(?:can'?t|cannot|not able to) breathe|\bbreathless|short(?:ness)? of breath"),
    ("breathing", r"\busir(?:u|aata|ata|ado|aadoke|adoke)? ?(?:kattide|kattid|kashta|kasta|aagtilla|aagta illa|agtilla)"),
    # cold sweat
    ("cold_sweat", r"\b(?:thanda|thandi|thanda sa|thande) (?:paseena|pasina|paseene)|\bcold sweat|\btann?a bevaru"),
    # stroke
    ("face_droop", r"\b(?:chehra|chehera|munh|muh|mooh|face) (?:tedha|tera|tedhaa|teda|latak|droop)|\bface (?:is )?drooping|\bmukha (?:sottagide|sotta|vakra|onde kade)"),
    ("one_side_weak", r"\b(?:haath|hath|pair|chehra|face) (?:me |mein )?(?:sunn|sun ho|suun)|\bek (?:taraf|side|tarf) (?:kamzori|kamjori|sunn|weak)|\bone side (?:weak|numb)|\bsudden(?:ly)? (?:weak|numb)"),
    ("one_side_weak", r"\b(?:kai|kaalu|mukha) jom|\bondu kade (?:shakti|shakthi) (?:illa|hogide)"),
    ("speech", r"\bbolne (?:me|mein|mai) (?:dikkat|takleef|problem)|\bzabaan (?:ladkhada|ladkhadaa|lad khada)|\bslurred speech|\bcan'?t speak|\bmaatad(?:oke|ok|alu) (?:aagtilla|agtilla|aagta illa|aagtha illa)"),
    ("vision", r"\bachanak (?:dikhna|dikhai) band|\bsudden(?:ly)? (?:can'?t see|blurr?ed vision|vision loss)|\bkann?u kaanistilla"),
    ("headache", r"\b(?:bahut )?tez sa?i?r ?dard|\bsevere headache|\btumba tale ?novu|\bjor(?:dar)? sar dard"),
    # Devanagari: the date normaliser is Latin-script only, but a missed emergency is not acceptable
    ("chest_pain", r"(?:सीने|सीना|छाती) (?:में )?(?:दर्द|भारीपन)"),
    ("breathing", r"सांस (?:लेने )?(?:में )?(?:तकलीफ|दिक्कत)|साँस (?:लेने )?(?:में )?(?:तकलीफ|दिक्कत)|सांस फूल"),
    ("cold_sweat", r"ठंडा पसीना"),
    ("face_droop", r"(?:चेहरा|मुंह) (?:टेढ़ा|टेढा)"),
    ("speech", r"बोलने में (?:दिक्कत|तकलीफ)"),
    ("faint", r"बेहोश"),
    ("faint", r"\bbehosh|\bbehos\b|\bfainted\b|\bpass(?:ed)? out\b|\bprajne tapp|\bpraj[nñ]e illa|\bkuSidu biddru|\bgir (?:gaye|gayi|pade) .*behosh"),
]

# arm / shoulder / jaw / back pain only counts together with sweat or nausea (chest/breath already escalate on their own)
REFERRED_PAIN = r"\b(?:left )?(?:arm|haath|hath|bhuja|baazu|bazu|baanh|kandha|kandhe|kandhon|shoulder|jaw|jabda|jabde|davade|kai) (?:me |mein |mai )?(?:pain|dard|novu)|\b(?:pain|dard|novu) in (?:the |my |his |her )?(?:left )?(?:arm|shoulder|jaw)"
NAUSEA = r"\b(?:ulti|vomit|vomiting|nausea|ji machal|vaanti|vaakarike)"

# service requests that mention chest/breath but are not symptoms
NOT_SYMPTOM = re.compile(r"chest (?:physio|physiotherapy|therapy|exercise)|breathing exercise|saans (?:ki|wali) exercise|usirata exercise", re.I)
# Negation only when the symptom itself is denied right after it ("dard nahi hai", "novu illa"),
# or reported as past and resolved ("chest pain tha, ab theek hai"). A later, unrelated
# "nahi"/"theek" ("hospital nahi gaye", "theek nahi lag raha", "not going away") does NOT negate.
NEGATION_AFTER = re.compile(
    r"^\W*(?:nahi|nahin|nai|illa|not)\b(?!\W*(?:gaye|gayi|gaya|ja|jaa|jaata|jata|jaati|ruk|rukta|rukti|lag|going|stopping|kam|hua|hoti|hota|horahi|hogide|aagta|aagtilla))"
    r"|^\W*(?:\w+\W+){0,1}(?:tha|thi|ittu|was there)\W+(?:\w+\W+){0,2}(?:ab|eega|now)\W+(?:\w+\W+){0,1}(?:theek|thik|fine|ok|illa|nahi|gone)\b",
    re.I,
)
NEGATION_BEFORE = re.compile(r"\b(?:no|not|never|koi|without|bina)\W+(?:\w+\W+){0,1}$", re.I)


def red_flag_hits(text: str) -> list[str]:
    """Return the red-flag signs found (empty list if none). Deterministic."""
    s = text.lower()
    s = NOT_SYMPTOM.sub(" ", s)
    hits: list[str] = []
    for sign, pat in RED_FLAGS:
        for m in re.finditer(pat, s):
            after = s[m.end(): m.end() + 30]
            before = s[max(0, m.start() - 20): m.start()]
            if NEGATION_AFTER.search(after) or NEGATION_BEFORE.search(before):
                continue
            hits.append(sign)
            break
    if re.search(REFERRED_PAIN, s) and (re.search(NAUSEA, s) or "cold_sweat" in hits):
        hits.append("referred_pain_with_sweat_or_nausea")
    return sorted(set(hits))
