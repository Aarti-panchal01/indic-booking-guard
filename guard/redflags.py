"""Red-flag phrases that stop a booking and hand the call to a human (or 108).

Source of the sign list: WHO cardiovascular diseases fact sheet, 2025-07-31,
https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)
The Hindi and Kannada phrases are the author's translation, NOT clinically validated.
Cardiac and stroke signs only. A real deployment needs a clinician to own this list.

Policy: over-escalation is cheap (a person calls back), a miss is not.

Three layers, all deterministic:
1. RED_FLAGS: fixed phrases (the original list, kept).
2. Body part x symptom co-occurrence on word stems (added Oct 8 after blind OOV v5 missed 4 of 7
   emergencies on new wording: "dum phool", "edeya ... kallu", "kaanisthilla", "jaw and left arm ... aching").
3. Jaw / left-arm pain alone, sudden limb weakness, and named events ("heart attack", "stroke").
Every hit is then checked for negation and past history:
- list negation: one "no"/"illa" covers a whole list ("no chest pain or breathlessness",
  "ede novu mattu usiraata kashta illa"), but only if every word between the negation and the symptom
  is a symptom word or a joiner. Anything else in between: no negation, escalate.
- past history ("3 saal pehle", "varsha hinde", "last year") drops a symptom in the same comma-part,
  unless that part also says it is happening now.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------- layer 1: fixed phrases (unchanged list)
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
    # Added after the blind OOV probe (3/7 emergencies missed: "dil mein dard", "edeyalli urita mattu bevaru",
    # "achanakkaagi bhayankara tale novu"). Body part x symptom within a few words instead of fixed phrases.
    ("chest_pain", r"\b(?:dil|heart|seene|seena|sine|chhati|chhaati|chaati|chati|chest|ede|edeyalli|edeli|edenalli|yede|yedeyalli)"
                   r"(?: \w+){0,2} (?:dard|pain|paining|novu|nov|jalan|urita|uri|bhaari|bhaaripan|bhaara|bhara|dabav|jakdan|"
                   r"tight|tightness|heavy|heaviness|pressure|dabaav|dabaw|hidi\w*|squeez\w*|bojh|boj|weight|patthar|tondare|tondre|kashta)"),
    # Added after the blind OOV v2 probe (4/8 emergencies missed): mouth/face + crooked, speech failing,
    # loss of consciousness. Same body-part x sign shape.
    ("face_droop", r"\b(?:bayi|baayi|baai|munh|muh|mooh|mukha|chehra|chehera|face|hont|lips?|mouth)(?: \w+){0,2} "
                   r"(?:vakra|vakara|tedha|tedhi|tedhe|sotta|sottagide|latak\w*|jhuk\w*|droop\w*|crooked|slant\w*)"),
    ("speech", r"\b(?:maatu|maathu|maat)(?: \w+){0,2} (?:baralla|bartilla|barta illa|barthilla|aagtilla|aagta illa)"
               r"|\b(?:bol|bolne|baat|awaaz|aawaz|zubaan|zabaan|words?|speech)(?: \w+){0,2} (?:nahi (?:pa|ho|nikal)\w*|ladkhad\w*|atak\w*|slur\w*|not coming|jumbled)"),
    ("faint", r"\bhosh (?:nahi|nahin|kho|mein nahi|me nahi|chala)|\bunconscious|\bblack(?:ed)? out|\bbehosh|\bbeshudh|\bbehoshi"),
    ("headache", r"\b(?:achanak|achanakkaagi|achanakagi|sudden|suddenly|ekdum|bhayankara|bhayankar|tumba jaasti|worst)"
                 r"(?: \w+){0,3} (?:sar ?dard|sir ?dard|tale ?novu|headache)"),
    # Devanagari: the date normaliser is Latin-script only, but a missed emergency is not acceptable
    ("chest_pain", r"(?:सीने|सीना|छाती) (?:में )?(?:दर्द|भारीपन)"),
    ("breathing", r"सांस (?:लेने )?(?:में )?(?:तकलीफ|दिक्कत)|साँस (?:लेने )?(?:में )?(?:तकलीफ|दिक्कत)|सांस फूल"),
    ("cold_sweat", r"ठंडा पसीना"),
    ("face_droop", r"(?:चेहरा|मुंह) (?:टेढ़ा|टेढा)"),
    ("speech", r"बोलने में (?:दिक्कत|तकलीफ)"),
    ("faint", r"बेहोश"),
    ("faint", r"\bbehosh|\bbehos\b|\bfainted\b|\bpass(?:ed)? out\b|\bprajne tapp|\bpraj[nñ]e illa|\bkuSidu biddru|\bgir (?:gaye|gayi|pade) .*behosh"),
    # Added Oct 8 (layer 3): a named event said as happening now. Past/negated mentions are dropped below.
    ("named_event", r"\bheart ?attack|\bdil ka daura|\bdaura (?:pad|aa)\w*|\bstroke\b|\blakwa|\blakhwa|\bparalys\w*|\bpaksha ?(?:vaata|vata|ghata)"),
    # sight lost, phrased as "can't see" without an eye word
    ("vision", r"\b(?:nahi|nahin) dikh|\bdikh(?:na|ai|ayi)? (?:nahi|nahin|band)|\b(?:can'?t|cannot|unable to|not able to) see\b"),
    # speech failing, phrased as "can't talk"
    ("speech", r"\bbol nahi pa\w*|\bsaaf nahi bol\w*|\b(?:can'?t|cannot|unable to|not able to) (?:talk|speak)\b"),
]

# ---------------------------------------------------------------- layer 2: body part x symptom on stems
# (sign, body-token regex, symptom-token regex). Each is a full match on one token. A hit needs a body token
# and a symptom token within WINDOW tokens of each other (either order) in the same sentence.
WINDOW = 5  # 4 missed "chhaati ke andar ajeeb sa bhaaripan" (new-wording test, Oct 8)
COOCCUR: list[tuple[str, str, str]] = [
    ("chest_pain",
     r"chest|seen\w*|seena|sina|sine|chh?aa?ti|chati|ede\w*|yede\w*|dil|heart",
     r"pain\w*|ache\w*|aching|dard|dukh\w*|novu|nov|novvu|jalan|urit\w*|uri|bhaar\w*|bhara|bhar|dab\w*|jakad\w*|jakd\w*|"
     r"tight\w*|heav\w*|pressure|squeez\w*|crush\w*|bojh|boj|weight|patthar|pathar|kallu|tondare|tondre|kashta|kasta|"
     r"ghabra\w*|discomfort|hidi\w*"),
    ("breathing",
     r"saans|sans|swaas|shwaas|swas|dum|breath|breathe|breathing|usir\w*|ushir\w*",  # not "saas" (mother-in-law)
     r"phool\w*|phul\w*|ful|fula|fulna|fool\w*|ruk\w*|atak\w*|ghut\w*|chadh\w*|takleef|taklif|dikkat|kashta|kasta|kattid\w*|short\w*|"
     r"difficult\w*|trouble|hard|struggl\w*|gasp\w*|tez|aagtilla|agtilla|tagolok\w*|tegeyok\w*"),
    ("face_droop",
     r"face|chehr\w*|chehera|munh|muh|mooh|mukha\w*|mukh|bayi|baayi|baai|hont\w*|lips?|mouth|gaal|cheek",
     r"tedh\w*|teda|latak\w*|jhuk\w*|droop\w*|crooked|slant\w*|vakra\w*|vakara|sotta\w*|sag|sagging|sagged|sunn|suun|numb\w*|jom"),
    # strong speech words may go with "ajeeb" (strange); bol/talk/speak may not ("Sunita bol rahi hoon, ajeeb si problem")
    ("speech",
     r"zub\w*|zab\w*|jeebh|jibh|nalige|naalige|awaaz|aawaz|voice|speech|maatu|maathu",
     r"ladkhad\w*|atak\w*|slur\w*|jumbl\w*|garbl\w*|mumbl\w*|gadbad|ajeeb|ajib|thick|bhaari|bartilla|baralla|barthilla|aagtilla|agtilla"),
    ("speech",
     r"bol\w*|speak\w*|talk\w*|words?|maat\w*",
     r"ladkhad\w*|slur\w*|jumbl\w*|garbl\w*|mumbl\w*|bartilla|baralla|barthilla"),
    ("vision",
     r"aankh\w*|ankh\w*|kannu|kann|kannalli|kanninalli|kannige|eye|eyes|nazar|najar|vision|sight",
     r"dhundh\w*|dhundl\w*|blur\w*|andher\w*|black|blind\w*|kaa?ni\w*illa|kaa?ni\w*ila|double|gone|lost"),
]

# chest + "is happening / feels" with no symptom word: a comparison ("edeya mele yaaro kootkondange aagthide",
# OOV v4 S035). Added Oct 8. Skipped when the same comma-part says it is fine.
CHEST_FEEL = ("chest_feeling",
              r"chest|seen\w*|seena|chh?aa?ti|chati|ede\w*|yede\w*",
              r"aagthide|aagtide|aaguttide|aagutte|aagtha|lag|lagta|lagti|lagra|lagraha|lagrahi|feel|feels|feeling|felt")
FINE = re.compile(r"\b(?:theek|thik|fine|normal|sari|ok|okay|alright|bilkul)\b")

# one side of the body + weak/numb
ONE_SIDE = re.compile(r"\b(?:ek|one|ondu|aadha|aadhe|half|left|right|baayan|daayan|edagade|balagade) ?"
                      r"(?:taraf|tarf|side|kade|bhaga|bhaag|hissa|sharir|body)\b")
WEAK_TOKEN = r"kamzor\w*|kamjor\w*|weak\w*|sunn|suun|numb\w*|jom|jum|dead|lifeless|shakti|shakthi"

# Option (b), chosen by the author Oct 8: jaw pain, or LEFT-arm pain, on its own escalates if current.
# Plain arm/shoulder pain stays a booking; so does jaw/left-arm pain with an injury, exercise, dental or old-onset reason.
JAW = r"jaw|jaws|jabda|jabde|jabdo|jabdon|davade|dawade|davde|dhavade"
LEFT = r"left|baayan|baaya|baaye|baayein|bayan|baya|ulta|ulte|edada|yedada|edagade"
ARM = r"arm|arms|haath|hath|kai|bhuja|baazu|bazu|baanh|hand"
LEFT_ARM_ONE = r"edagai|yedagai|edgai"
PAIN_TOKEN = r"pain\w*|ache\w*|aching|achy|dard|dukh\w*|novu|nov|novvu|heav\w*|bhaar\w*|sunn|suun|numb\w*"
LIMB_INJURY_OR_OLD = re.compile(
    r"\b(?:gym|workout|exercise\w*|cricket|match|lifting|weights?|fell|fall|gir\w*|slip\w*|chot|injur\w*|sprain\w*|"
    r"fractur\w*|surgery|operation|typing|laptop|frozen|physio\w*|weeks?|months?|hafte|haftey|mahine|mahina|saal|"
    r"varsha|vaara|tingalu|purana|purani|daant|dant|tooth|teeth|hallu|dentist|molar|braces|wisdom|days|dinagalinda)\b"
    r"|\b(?:din|dino|dinon) se\b")

# limb cannot be lifted/moved: escalates if sudden, or if no pain word in the sentence (pain = likely a physio case)
LIMB = r"haath|hath|pair|paon|kai|kaalu|arm|leg|hand|bhuja"
LIMB_CANNOT = re.compile(
    r"\b(?:uth|utha|uthta|uthti|uthte|hil|hila|hilta|lift|move|ett\w*)\b(?: \w+)? (?:nahi|nahin|nai|aagtilla|agtilla|illa)\b"
    r"|\b(?:nahi|nahin) (?:uth|hil)\w*|\b(?:can'?t|cannot|unable to|not able to|won'?t) (?:lift|move|hold|grip)\b")
SUDDEN = re.compile(r"\b(?:achanak\w*|sudden\w*|ekdum|ek dam|ekdam|abhi abhi|just now|thodi der|achanakkaagi|"
                    r"dideer\w*|thatt?ane)\b")

# ---------------------------------------------------------------- combination rules
# arm / shoulder / jaw / back pain counts together with sweat or nausea (chest/breath escalate on their own)
REFERRED_BODY = r"arm|arms|haath|hath|bhuja|baazu|bazu|baanh|kandha|kandhe|kandhon|shoulder|jaw|jabda|jabde|davade|kai|back|peeth"
NAUSEA = (r"\b(?:ulti|vomit\w*|nausea\w*|nauseous|queasy|ji machal|ji ghabra|matli|vaanti|vaakarike|"
          r"throw(?:ing)? up|threw up|feel(?:s|ing)? like vomiting|ulti jaisa)")
SWEAT_TOKEN = r"paseena|pasina|paseene|bevaru|beværu|sweat|sweating|sweaty"
CHEST_TOKEN = r"dil|heart|seene|seena|chhati|chest|ede\w*|yede\w*"

# service requests that mention chest/breath but are not symptoms
NOT_SYMPTOM = re.compile(r"chest (?:physio|physiotherapy|therapy|exercise)|breathing exercise|saans (?:ki|wali) exercise|usirata exercise", re.I)

# ---------------------------------------------------------------- negation and past history
# Kept from before: the symptom itself denied right after it ("dard nahi hai", "novu illa"), or past and resolved
# ("chest pain tha, ab theek hai"), or long past ("fainted about a month back"). A later, unrelated "nahi"
# ("hospital nahi gaye", "theek nahi lag raha", "not going away") does NOT negate.
NEGATION_AFTER = re.compile(
    r"^\W*(?:nahi|nahin|nai|illa|not)\b(?!\W*(?:gaye|gayi|gaya|ja|jaa|jaata|jata|jaati|ruk|rukta|rukti|lag|going|stopping|kam|hua|hoti|hota|horahi|hogide|aagta|aagtilla))"
    r"|^\W*(?:\w+\W+){0,1}(?:tha|thi|ittu|was there)\W+(?:\w+\W+){0,2}(?:ab|eega|ega|now)\W+(?:\w+\W+){0,1}(?:theek|thik|fine|ok|illa|nahi|gone|sari\w*|normal)\b"
    r"|^\W*(?:\w+\W+){0,4}(?:month|months|year|years|saal|mahine|mahina|varsha|weeks|hafte)\W+(?:back|ago|pehle|hinde)\b",
    re.I,
)
PAST_BEFORE = re.compile(r"\b(?:last year|pichhle saal|pichle saal|hindina varsha|kaleda varsha|years ago|months ago|"
                         r"last month|pichhle mahine|pichle mahine)\W+(?:\w+\W+){0,3}$", re.I)

NEG_BEFORE = {"no", "not", "never", "without", "bina", "nor", "neither", "none"}  # not "na": "aao na seene me dard"
NEG_AFTER = {"nahi", "nahin", "nai", "illa", "ila", "ilve", "ilvu", "not"}
# what may follow the after-negation for it to count ("dard nahi hai.", "novu illa, ...", "dard nahi, sirf ...")
NEG_TAIL = {"hai", "he", "hain", "h", "ha", "ide", "ji", "sir", "madam", "tha", "thi", "the", "ittu", "haina",
            "sirf", "bas", "only", "just", "aur", "and", "but", "lekin", "aadre"}
# words that may sit between the negation and the symptom: joiners and fillers (never "problem": "No problem, chest pain hai")
JOINERS = {"or", "and", "nor", "aur", "ya", "yaa", "mattu", "matthu", "mathu", "athava", "athwa", "na", "no", ",",
           "ki", "ka", "ke", "ko", "koi", "kuch", "bhi", "any", "enu", "yenu", "yaavude", "the", "my", "his", "her",
           "a", "of", "in", "me", "mein", "mai", "mien", "to", "with", "lene", "left", "right", "sudden", "achanak"}
# symptom words that may sit inside a negated list
LIST_WORDS = re.compile(
    r"(?:pain\w*|ache\w*|aching|dard|novu|nov|kashta|kasta|takleef|taklif|dikkat|breath\w*|saans|usir\w*|"
    r"sweat\w*|paseena|pasina|bevaru|chest|seen\w*|seena|chh?aa?ti|ede\w*|jaw|arm|haath|numb\w*|weak\w*|"
    r"kamzori|kamjori|tight\w*|heav\w*|bhaari\w*|discomfort|pressure|dizz\w*|chakkar|ulti|nausea|vomit\w*|"
    r"short\w*|swelling|sunn|jalan|ghabrahat|fainting|behoshi)")
LONG_PAST = re.compile(
    r"\b(?:\d+|ek|do|teen|char|chaar|paanch|one|two|three|four|five|six|ondu|eradu|mooru|naalku|aidu|several|few|kai|"
    r"couple of)\s+(?:saal|sal|varsha|varshada|years?|months?|mahine|mahina|mahino|weeks?|hafte|haftey|vaara|tingalu)\s+"
    r"(?:pehle|pahle|ago|back|hinde|munche|modalu)\b"
    r"|\b(?:last|pichhle|pichle|pichhla|pichla|kaleda|hindina|previous)\s+(?:year|saal|month|mahine|varsha|varshada|tingalu)\b"
    r"(?!\s+(?:se|since|inda|from))"
    r"|\bin (?:19|20)\d\d\b|\bonce had\b|\bhistory of\b")
NOW_WORDS = re.compile(r"\b(?:abhi|ab|now|today|aaj|ivattu|indu|ega|eega|currently|still|abhi bhi|ab bhi|innu|"
                       r"again|phir se|fir se|wapas|marali|tonight|right now|since morning|subah se|beligge inda)\b")

TOKEN = re.compile(r"[^\W_]+(?:'[^\W_]+)?|[.,?!;]")
SENT_END = {".", "?", "!", ";"}
CONTRAST = {"but", "lekin", "magar", "aadre", "aadare", "aadru", "however", "though", "although", "balki"}


class _Text:
    """Lowercased text split into tokens, with sentence and comma-part ids per token."""

    def __init__(self, s: str):
        self.s = s
        self.toks: list[tuple[str, int, int]] = [(m.group(), m.start(), m.end()) for m in TOKEN.finditer(s)]
        self.sent: list[int] = []
        self.part: list[int] = []
        si = pi = 0
        for t, _, _ in self.toks:
            if t in SENT_END or t in CONTRAST:
                si += 1
                pi += 1
            elif t == ",":
                pi += 1
            self.sent.append(si)
            self.part.append(pi)

    def words(self) -> list[str]:
        return [t for t, _, _ in self.toks]

    def span_to_tokens(self, a: int, b: int) -> tuple[int, int]:
        idx = [i for i, (_, s0, s1) in enumerate(self.toks) if s0 < b and s1 > a]
        return (idx[0], idx[-1]) if idx else (0, 0)

    def part_text(self, i: int) -> str:
        return " ".join(t for (t, _, _), p in zip(self.toks, self.part) if p == self.part[i])

    def sent_text(self, i: int) -> str:
        return " ".join(t for (t, _, _), q in zip(self.toks, self.sent) if q == self.sent[i])


def _between_ok(t: str) -> bool:
    return t in JOINERS or bool(LIST_WORDS.fullmatch(t))


def _negated(tx: _Text, i0: int, i1: int) -> bool:
    w = tx.words()
    # "no chest pain or breathlessness": walk left over symptom words and joiners to a negation word
    k = i0 - 1
    while k >= 0 and k > i0 - 14:
        if w[k] in NEG_BEFORE and not (k + 1 < len(w) and w[k + 1] == ","):  # "No, chest pain since morning" is not a negation
            return True
        if not _between_ok(w[k]):
            break
        k -= 1
    # "ede novu mattu usiraata kashta illa": walk right over symptom words and joiners to "illa"/"nahi",
    # which must end the clause ("dard nahi ruk raha" is not a negation)
    k = i1 + 1
    while k < len(w) and k < i1 + 14:
        if w[k] in NEG_AFTER:
            nxt = w[k + 1] if k + 1 < len(w) else ""
            return nxt == "" or nxt in SENT_END or nxt == "," or nxt in NEG_TAIL
        if not _between_ok(w[k]):
            break
        k += 1
    return False


def _past(tx: _Text, i0: int) -> bool:
    part = tx.part_text(i0)
    return bool(LONG_PAST.search(part)) and not NOW_WORDS.search(part)


def _excluded(tx: _Text, a: int, b: int) -> bool:
    """True if the hit at characters a..b is negated or is past history."""
    i0, i1 = tx.span_to_tokens(a, b)
    s = tx.s
    return bool(NEGATION_AFTER.search(s[b: b + 30]) or PAST_BEFORE.search(s[max(0, a - 45): a])
                or _negated(tx, i0, i1) or _past(tx, i0))


def _tok_excluded(tx: _Text, i0: int, i1: int) -> bool:
    return _excluded(tx, tx.toks[i0][1], tx.toks[i1][2])


def _pairs(tx: _Text, left: str, right: str, window: int):
    """Token index pairs (i, j): token i fully matches `left`, token j `right`, |i-j| <= window, same comma-part
    ("Seene mein koi dikkat nahi hai, saans bhi bilkul theek hai" must not pair "dikkat" with "saans")."""
    w = tx.words()
    lre, rre = re.compile(left), re.compile(right)
    L = [i for i, t in enumerate(w) if lre.fullmatch(t)]
    R = [j for j, t in enumerate(w) if rre.fullmatch(t)]
    for i in L:
        for j in R:
            if i != j and abs(i - j) <= window and tx.part[i] == tx.part[j]:
                yield min(i, j), max(i, j)


def red_flag_hits(text: str) -> list[str]:
    """Return the red-flag signs found (empty list if none). Deterministic."""
    s = NOT_SYMPTOM.sub(" ", text.lower())
    tx = _Text(s)
    w = tx.words()
    hits: set[str] = set()

    # layer 1: fixed phrases
    for sign, pat in RED_FLAGS:
        for m in re.finditer(pat, s):
            if not _excluded(tx, m.start(), m.end()):
                hits.add(sign)
                break

    # layer 2: body part x symptom
    for sign, body, sym in COOCCUR:
        if any(not _tok_excluded(tx, i, j) for i, j in _pairs(tx, body, sym, WINDOW)):
            hits.add(sign)
    sign, body, feel = CHEST_FEEL
    if any(not FINE.search(tx.part_text(i)) and not _tok_excluded(tx, i, j) for i, j in _pairs(tx, body, feel, WINDOW)):
        hits.add(sign)
    for m in ONE_SIDE.finditer(s):
        i0, i1 = tx.span_to_tokens(m.start(), m.end())
        near = [j for j, t in enumerate(w) if re.fullmatch(WEAK_TOKEN, t) and min(abs(j - i0), abs(j - i1)) <= WINDOW
                and tx.sent[j] == tx.sent[i0]]
        if any(not _tok_excluded(tx, min(i0, j), max(i1, j)) for j in near):
            hits.add("one_side_weak")

    # layer 3a: option (b), jaw or left-arm pain alone
    jaw = list(_pairs(tx, JAW, PAIN_TOKEN, 6))
    left_arm = [(i, j) for i, j in _pairs(tx, LEFT, ARM, 1)]
    left_arm_pain = [(min(a, p), max(b, p)) for a, b in left_arm for p, t in enumerate(w)
                     if re.fullmatch(PAIN_TOKEN, t) and abs(p - b) <= 6 and tx.sent[p] == tx.sent[b]]
    left_arm_pain += list(_pairs(tx, LEFT_ARM_ONE, PAIN_TOKEN, 6))
    for i, j in jaw + left_arm_pain:
        if not LIMB_INJURY_OR_OLD.search(tx.sent_text(i)) and not _tok_excluded(tx, i, j):
            hits.add("jaw_or_left_arm_pain")
            break

    # layer 3b: a limb that suddenly cannot be lifted or moved
    for m in LIMB_CANNOT.finditer(s):
        i0, i1 = tx.span_to_tokens(m.start(), m.end())
        sent = tx.sent_text(i0)
        limb_near = any(re.fullmatch(LIMB, w[j]) and abs(j - i0) <= WINDOW + 2 and tx.sent[j] == tx.sent[i0] for j in range(len(w)))
        no_pain = not re.search(r"\b(?:" + PAIN_TOKEN + r")\b", sent)
        if limb_near and (SUDDEN.search(sent) or no_pain) and not LIMB_INJURY_OR_OLD.search(sent) \
                and not _excluded(tx, m.start(), m.end()):
            hits.add("limb_cannot_move")
            break

    # combination rules (each part must itself be current and not negated)
    referred = [p for p in _pairs(tx, REFERRED_BODY, PAIN_TOKEN, WINDOW) if not _tok_excluded(tx, *p)]
    nausea = [m for m in re.finditer(NAUSEA, s) if not _excluded(tx, m.start(), m.end())]
    sweat = [i for i, t in enumerate(w) if re.fullmatch(SWEAT_TOKEN, t) and not _tok_excluded(tx, i, i)]
    if referred and (nausea or sweat or "cold_sweat" in hits):
        hits.add("referred_pain_with_sweat_or_nausea")
    chest = [i for i, t in enumerate(w) if re.fullmatch(CHEST_TOKEN, t) and not _tok_excluded(tx, i, i)]
    if "chest_pain" not in hits and chest and sweat:
        hits.add("chest_word_with_sweat")
    return sorted(hits)
