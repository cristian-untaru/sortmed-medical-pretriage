"""Word lists used by the deterministic input guard rules."""

SYMPTOM_SIGNAL_TERMS = {
    "ache", "aches", "aching", "allergy", "allergic", "bleeding", "blocked",
    "bloated", "blurred", "blurry", "breath", "breathe", "breathing", "burn",
    "burning", "chills", "cold", "congestion", "constipation", "cough",
    "coughing", "cramp", "cramps", "diarrhea", "dizzy", "dizziness", "dry",
    "fatigue", "fever", "headache", "heartburn", "hot", "hurt", "hurts",
    "hurting", "itch", "itching", "itchy", "migraine", "nausea",
    "nauseated", "nauseous", "numb", "numbness", "pain", "painful",
    "palpitations", "pressure", "rash", "runny", "shortness", "sick",
    "sneezing", "sore", "stiff", "stiffness", "stuffy", "sweats", "sweaty",
    "swelling", "swollen", "tight", "tightness", "tingling", "tired",
    "tiredness", "unwell", "urinate", "urinating", "vomit", "vomiting",
    "weak", "weakness", "wheezing",
}

BODY_LOCATION_TERMS = {
    "abdomen", "abdominal", "ankle", "ankles", "arm", "arms", "back", "belly",
    "blood", "body", "bone", "bones", "brain", "breast", "calf", "chest",
    "ear", "ears", "elbow", "elbows", "eye", "eyes", "face", "feet", "finger",
    "fingers", "foot", "forehead", "gums", "hand", "hands", "head", "hip",
    "hips", "jaw", "knee", "knees", "leg", "legs", "lip", "lips", "mouth",
    "muscle", "muscles", "neck", "nose", "shoulder", "shoulders", "skin",
    "spine", "stomach", "teeth", "temple", "throat", "toe", "toes", "tongue",
    "tooth", "torso", "urine", "vision", "wrist", "wrists",
}

SYMPTOM_CONTEXT_TERMS = {
    "after", "again", "all", "am", "bad", "before", "been", "can", "cannot",
    "cant", "comes", "constant", "day", "days", "deeply", "during", "feel",
    "feeling", "for", "from", "get", "getting", "goes", "got", "had", "has",
    "have", "hour", "hours", "i", "intermittent", "is", "last", "left",
    "lower", "mild", "moderate", "morning", "my", "night", "now", "often",
    "on", "past", "pee", "peeing", "really", "right", "severe", "sharp",
    "since", "slightly", "sometimes", "started", "starts", "sudden", "this",
    "today", "tonight", "upper", "very", "week", "weeks", "well", "when",
    "while", "worse", "worsening", "yesterday",
}

LOW_INFORMATION_STOPWORDS = {
    "a", "an", "and", "are", "been", "for", "had", "has", "have", "i", "i'm",
    "i've", "im", "in", "is", "it", "me", "my", "of", "on", "or", "the", "to",
    "was", "were", "with",
}

SHORT_INPUT_ALLOWED_TERMS = (
    SYMPTOM_SIGNAL_TERMS
    | BODY_LOCATION_TERMS
    | SYMPTOM_CONTEXT_TERMS
    | LOW_INFORMATION_STOPWORDS
)

JOINED_MEDICAL_TERMS = {
    "chestpain", "shortnessofbreath", "stomachpain", "abdominalpain",
    "sorethroat",
}

LEET_TRANSLATION = str.maketrans({
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
})

GIBBERISH_MARKERS = {
    "alpha", "amet", "banana", "bar", "baz", "beta", "blorple", "chair",
    "corge", "crindle", "delta", "epsilon", "flarble", "foo", "gamma",
    "ipsum", "keyboard", "lorem", "mivra", "qwerty", "quux", "qux",
    "random", "sit", "snorky", "taznok", "tokens", "wamble", "zeta",
    "zzzonk",
}

NON_ENGLISH_MARKERS = {
    # Romanian, including common non-diacritic spellings.
    "ma", "m\u0103", "doare", "durere", "capul", "burta", "burt\u0103",
    "gatul", "g\u00e2tul", "pieptul", "spatele", "mana", "m\u00e2na",
    "piciorul", "febra", "febr\u0103", "tuse", "greata", "grea\u021b\u0103",
    "ametesc", "ameteli", "ame\u021beli", "respir", "respira", "zile",
    "medicament", "pastile",
    # Common Spanish, French, Italian, Portuguese, and German basics.
    "duele", "cabeza", "dolor", "fiebre", "tos", "tengo", "desde",
    "j'ai", "jai", "mal", "tete", "t\u00eate", "fi\u00e8vre", "toux",
    "ho", "dolore", "testa", "febbre", "tosse", "dor", "cabeca",
    "cabe\u00e7a", "febre", "schmerzen", "kopfschmerzen", "husten",
    "fieber", "seit",
}

ROMANIAN_DIACRITICS = set(
    "\u0103\u00e2\u00ee\u0219\u015f\u021b\u0163"
    "\u0102\u00c2\u00ce\u0218\u015e\u021a\u0162"
)
