"""Regex patterns used by the deterministic guard rules."""

META_INSTRUCTION_PATTERNS = (
    r"\bignore\b.*\b(instruction|instructions|safety|rule|rules)\b",
    r"\bsystem\b.*\boverride\b",
    r"\boverride\b.*\b(app|system|safety|rule|rules)\b",
    r"\bclassify\s+(this|it)\b",
    r"\bchoose\b.*\b(urgent|consult\s+gp|self[-\s]?monitor)\b",
    r"\bassign\b.*\blabel\b",
    r"\breturn\s+(urgent|consult\s+gp|self[-\s]?monitor)\b",
    r"\bsay\s+(urgent|consult\s+gp|self[-\s]?monitor)\b",
    r"\b(final\s+result|answer|prediction|recommendation)\b.*\b(urgent|consult\s+gp|self[-\s]?monitor)\b",
    r"\b(urgent|consult\s+gp|self[-\s]?monitor)\b.*\b(final\s+result|answer|prediction|recommendation)\b",
    r"\bgive\s+me\s+triage\b",
    r"\btriage\s+(this|for)\b",
    r"\bmake\s+the\s+output\b",
    r"\bcorrect\s+answer\b.*\b(emergency|urgent|consult\s+gp|self[-\s]?monitor)\b",
    r"\blabel\s+(this|the)\s+(case|input)\s+as\b",
    r"\bresult\s+to\s+be\b",
    r"\boutput\b.*\b(red|green|urgent|emergency|consult\s+gp|self[-\s]?monitor)\b",
    r"\bhighest\s+risk\s+category\b",
    r"\bsafest\s+triage\b",
)

META_COMMAND_TERMS = {
    "answer", "app", "category", "classify", "classifier", "classification",
    "emergency", "instruction", "instructions", "label", "output",
    "override", "prediction", "prompt", "return", "rules", "safety",
    "system", "triage",
}

TEXT_REFERENCE_PATTERNS = (
    r"\b(medical\s+words?|medical\s+terms?)\b",
    r"\bwords?\s+(are|used|from)\s+(medical|medicine)\b",
    r"\bphrase\s+used\s+in\s+medicine\b",
    r"\b(test|testing)\b.*\b(tokens?|prompt|classifier|symptoms?|words?)\b",
    r"\btraining\s+data\s+row\b",
    r"\bdataset\s+(example|row|says)\b",
    r"\bprompt\s+contains\b",
    r"\bcontains\b.*\b(tokens?|examples?)\b",
    r"\bonly\s+as\s+examples?\b",
    r"\bas\s+examples?\b",
    r"\bthese\s+are\s+just\s+words\b",
    r"\bjust\s+words\b",
    r"\bfor\s+my\s+assignment\b",
    r"\bthis\s+is\s+a\s+test\b",
    r"\bignore\s+this\s+part\b",
    r"\btranslate\s+this\s+later\b",
    r"\bexample\s+only\b",
    r"\bmention\b.*\b(headache|pain|fever|cough|nausea|vomiting|dizziness)\b",
    r"\bsymptoms?\s+can\s+be\b",
    r"\b(textbooks?|chapters?)\b",
    r"\bmedical\s+article\b",
    r"\b(article|sentence|word)\b.*\b(mentions?|contains?|appears?)\b",
    r"\bstudents?\s+(learn|study|studied|discuss)\b",
    r"\b(for|in)\s+(school|class)\b.*\b(discuss|studied|study|learn|talk)\b",
    r"\bdataset\s+(includes|contains|has)\b",
    r"\bword\s+\w+\s+appears\b",
    r"\bsentence\s+may\s+contain\b",
    r"\bin\s+medicine\b.*\b(can|may|could|is|are)\b",
)

TREATMENT_REQUEST_PATTERNS = (
    r"\bhow\s+(do|can)\s+i\s+(treat|cure|manage|relieve)\b",
    r"\bwhat\s+should\s+i\s+take\b",
    r"\bcan\s+i\s+take\b",
    r"\b(best|good)\s+(pills?|medicines?|medications?|meds?|treatment)\b",
    r"\b(antibiotics?|ibuprofen|paracetamol|acetaminophen|pills?|meds?|medicine|medication)\b.*\b(for|against)\b",
    r"\b(for|against)\b.*\b(antibiotics?|ibuprofen|paracetamol|acetaminophen|pills?|meds?|medicine|medication)\b",
)

ADVICE_OR_RISK_QUESTION_PATTERNS = (
    r"^\s*(should|could|would)\s+i\b.*\b(worry|go|see|visit|call|need)\b",
    r"^\s*do\s+i\s+need\b.*\b(doctor|gp|hospital|er|emergency|urgent|appointment|medical\s+care)\b",
    r"^\s*when\s+is\b.*\b(emergency|dangerous|serious|urgent)\b",
    r"^\s*is\b.*\b(dangerous|serious|emergency|urgent|bad|normal)\b",
    r"^\s*(could|does|do)\b.*\bmean\b",
    r"^\s*how\s+bad\s+is\b",
)

WRITING_TASK_PATTERNS = (
    r"\b(write|create|make|generate|give)\b.*\b(sentence|quiz|question|flashcards?|article|summary|poem|example|examples?)\b",
    r"\bexplain\b.*\b(phrase|term|word|simple\s+terms)\b",
    r"\bdefine\b.*\b(headache|pain|fever|cough|nausea|vomiting|dizziness|rash|symptoms?)\b",
    r"\blist\b.*\b(words?|terms?|symptoms?)\b",
    r"\buse\b.*\bin\s+(a\s+)?(sentence|paragraph|example)\b",
    r"\bconvert\b.*\binto\b",
    r"\brephrase\b",
    r"\btranslate\b.*\binto\b",
    r"\bsummari[sz]e\b.*\b(article|text|paragraph|summary)\b",
    r"\bflashcards?\b",
)

HYPOTHETICAL_CASE_PATTERNS = (
    r"^\s*if\s+(someone|a\s+person|a\s+patient)\b",
    r"\bsuppose\b.*\b(someone|person|patient)\b",
    r"\bimagine\b.*\b(someone|person|patient)\b",
    r"\bconsider\b.*\b(someone|person|patient)\b",
    r"\bexample\s+patient\b",
    r"\bas\s+an\s+example\b",
    r"\bin\s+this\s+scenario\b",
    r"\bthis\s+scenario\b.*\b(person|patient)\b",
    r"\bcase\s+study\b",
    r"\bcase\s+report\b",
    r"\bmedical\s+scenario\b",
    r"\bsample\s+patient\b",
    r"\broleplay\b",
    r"\bpretend\b",
    r"\bfor\s+(a\s+)?(novel|screenplay|story|game)\b",
    r"\b(game|fictional)\s+character\b",
)

NO_SYMPTOMS_PATTERNS = (
    r"\bno\s+symptoms?\b",
    r"\bno\s+medical\s+problem\b",
    r"\bnothing\s+wrong\s+with\s+me\b",
    r"\b(completely|totally|perfectly)\s+fine\b",
    r"\bfeel(?:ing)?\s+(completely\s+)?fine\b",
    r"\bi(?:\s+am|'m)\s+healthy\b",
    r"\bdon't\s+feel\s+(feverish|sick|dizzy|nauseous|pain|painful)\b",
    r"\bdo\s+not\s+have\s+(pain|fever|cough|nausea|vomiting|dizziness|symptoms?)\b",
    r"\bthere\s+is\s+no\s+(pain|fever|cough|nausea|vomiting|dizziness)\b",
    r"\bdeny\s+having\b",
    r"\bzero\s+symptoms?\b",
    r"\bnot\s+sick\b",
    r"\bonly\s+typing\b",
    r"\bnot\s+feeling\s+them\b",
    r"\bnone\s+of\s+these\s+apply\s+to\s+me\b",
    r"\bfeel\s+normal\b.*\b(mention|type|words?)\b",
    r"\bsymptom[-\s]?free\b",
    r"\bwithout\s+any\s+symptoms?\b",
    r"\b(don't|dont|do\s+not)\s+have\s+symptoms?\s+yet\b",
)

NEGATED_SYMPTOM_PATTERNS = (
    r"\b(don't|dont|do\s+not)\s+(have|feel|experience)\b.*\b(pain|fever|cough|nausea|vomiting|dizziness|rash|shortness\s+of\s+breath|symptoms?)\b",
    r"\b(i\s+am|i'm|im)\s+not\s+(experiencing|feeling|having)\b.*\b(pain|fever|cough|nausea|vomiting|dizziness|rash|shortness\s+of\s+breath|symptoms?)\b",
    r"\bnot\s+experiencing\b.*\b(pain|fever|cough|nausea|vomiting|dizziness|rash|shortness\s+of\s+breath|symptoms?)\b",
)

FUTURE_OR_PREVENTIVE_PATTERNS = (
    r"\b(might|may|could)\s+get\b.*\b(tomorrow|later|tonight|soon)\b",
    r"\bi\s+am\s+afraid\s+i\s+will\s+have\b",
    r"\bi\s+(want|need)\s+to\s+prevent\b",
    r"\bhow\s+can\s+i\s+avoid\b",
    r"\b(prevent|avoid)\b.*\b(pain|fever|cough|nausea|vomiting|dizziness|rash|shortness\s+of\s+breath)\b",
    r"\b(don't|dont|do\s+not)\s+have\s+symptoms?\s+yet\b",
    r"\bsymptoms?\s+yet\b.*\b(fear|afraid|worried)\b",
)

NON_PATIENT_CONTEXT_PATTERNS = (
    r"\b(my|the|a|an)\s+(dog|cat|car|vehicle|engine|computer|server|code|wallet|project|software|program|database|website|laptop|phone|robot)\b",
    r"\b(this|the|my)\s+(code|project|server|computer|website|app|software|database|laptop|phone|robot)\b.*\b(headache|fever|pain|vomit|vomiting|cough|sick)\b",
    r"\b(fictional\s+character|character\s+in\s+(my|a|the)\s+story)\b",
    r"\b(patient|person)\s+in\s+(my|a|the)\s+story\b",
    r"\bmy\s+story\b",
)

RESOLVED_SYMPTOMS_PATTERNS = (
    r"\b(had|used\s+to\s+have|was|were)\b.*\b(last\s+year|last\s+month|months?\s+ago|weeks?\s+ago|earlier|yesterday|before)\b.*\b(fine\s+now|currently\s+fine|better\s+now|gone|not\s+anymore|went\s+away|stopped|resolved|cleared\s+up|okay|ok)\b",
    r"\b(had|used\s+to\s+have|was|were)\b.*\b(fever|pain|headache|cough|vomiting|dizzy|dizziness|nausea)\b.*\b(fine\s+now|currently\s+fine|better\s+now|gone|not\s+anymore|went\s+away|stopped|resolved|cleared\s+up|okay|ok)\b",
    r"\b(fever|cough|headache|pain|vomiting|nausea)\b.*\b(ended|disappeared|cleared\s+up|went\s+away|stopped)\b",
    r"\brecovered\s+from\b.*\b(fever|cough|headache|pain|vomiting|nausea)\b",
    r"\bcurrently\s+no\s+issue\b",
)

REMOTE_HISTORY_PATTERNS = (
    r"\b(last\s+year|last\s+month|months?\s+ago|years?\s+ago|as\s+a\s+child)\b.*\b(had|experienced|suffered|got)\b",
    r"\b(had|experienced|suffered|got)\b.*\b(last\s+year|last\s+month|months?\s+ago|years?\s+ago|as\s+a\s+child)\b",
    r"\b(two|three|four|five|six|seven|eight|nine|ten)\s+months?\s+ago\b.*\b(had|experienced|suffered|got)\b",
    r"\b(had|experienced|suffered|got)\b.*\b(two|three|four|five|six|seven|eight|nine|ten)\s+months?\s+ago\b",
)

INDIRECT_DIAGNOSIS_PATTERNS = (
    r"\bwhat\s+(condition|disease|illness)\s+(causes|matches|fits|is)\b",
    r"\bwhich\s+(condition|disease|illness)\s+(causes|matches|fits|is)\b",
    r"\bwhat\s+is\s+causing\b",
)

CODE_LIKE_PATTERNS = (
    r"^\s*(select|insert|update|delete)\b.*\b(from|where|set)\b",
    r"^\s*(get|post|put|patch|delete)\s+/",
    r"^\s*[\{\[]",
    r"\"(symptoms?|label|urgent|input)\"\s*:",
    r"\btriage\s*\(",
    r"\bsymptoms?\s*=",
    r"\bprint\s*\(",
    r"</?[a-z][a-z0-9]*[^>]*>",
    r"\bcurl\s+-",
    r"\bpost\b.*\b(urgent|triage|symptom)\b",
    r"^\s*#.*\b(urgent|fever|pain|cough|symptom)\b",
)

CODE_SWITCH_PATTERNS = (
    r"\bme\s+duele\b",
    r"\bj'?ai\b",
    r"\bich\s+habe\b",
    r"\bboli\s+mnie\b",
    r"\bma\s+doare\b",
    r"\btengo\b",
)

SPACED_MEDICAL_TERM_PATTERNS = (
    r"\bh\s+e\s+a\s+d\b",
    r"\bc\s+h\s+e\s+s\s+t\b",
    r"\bp\s+a\s+i\s+n\b",
    r"\bf\s+e\s+v\s+e\s+r\b",
    r"\bc\s+o\s+u\s+g\s+h\b",
)
