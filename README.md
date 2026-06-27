# SortMed

SortMed is a Streamlit application for AI-assisted medical pre-triage. A user writes a symptom description in English, the input is validated by a dedicated guard, and a fine-tuned transformer model returns an initial care recommendation.

The application is developed as part of a bachelor's thesis project on natural language processing for medical pre-triage. It is not a diagnostic system and must not be used as a replacement for professional medical advice.

The application can be run locally or in a configured academic evaluation environment. Account-related features require Supabase PostgreSQL and email settings.

## What the application does

SortMed supports the following workflow:

1. The user enters a symptom description in natural language.
2. The input guard rejects empty, non-medical, non-English, repetitive, adversarial or out-of-scope text.
3. A selected triage model classifies the description into one of three care levels.
4. The application displays the recommendation, confidence information and class score breakdown.
5. Related medical Q&A entries are retrieved from MedQuAD using semantic similarity.
6. Authenticated users can save and review their analysis history.

The three output classes are:

| Label | Meaning |
| --- | --- |
| `self_monitor` | Symptoms appear mild and can be monitored. |
| `consult_gp` | A non-urgent medical consultation is recommended. |
| `urgent` | The symptoms may require urgent medical attention. |

## Main features

- Streamlit web interface with custom CSS.
- Account registration, email verification, login, password reset and guest mode.
- Supabase PostgreSQL persistence for users, password reset codes and saved analyses.
- Hybrid input guard combining rule-based validation with a trained intent classifier.
- 16 selectable triage model variants: four base transformer architectures and four fine-tuning strategies.
- Context-aware MedQuAD retrieval using MiniLM sentence embeddings.
- Saved analysis history and account statistics.
- Automated tests with `pytest`, Streamlit `AppTest` and Playwright.

## Architecture

SortMed separates the interface, validation layer, model inference, semantic retrieval and persistence layer. The triage path and the MedQuAD retrieval path start from the same validated symptom description, but they serve different purposes.

| Layer | Responsibility |
| --- | --- |
| Streamlit interface | Renders the landing page, authenticated workspace, model selectors, results, account actions and saved history. |
| Authentication and persistence | Stores users, verification codes, reset codes and saved analyses in Supabase PostgreSQL. |
| Input guard | Normalizes the text, applies rule-based validation and accepts only symptom descriptions through the intent classifier. |
| Triage inference | Loads the selected Hugging Face model and predicts `self_monitor`, `consult_gp` or `urgent`. |
| MedQuAD retrieval | Encodes the symptom description with MiniLM and compares it with precomputed MedQuAD embeddings. |
| Result presentation | Shows the recommendation, confidence, score breakdown, model details and related medical context when available. |

```text
User symptom description
    |
    v
Streamlit interface
    |
    v
Input guard
    |-- validation rules
    |-- intent classifier
    |
    v
Validated symptom description
    |
    |-- Triage model inference
    |     |
    |     v
    |   Recommendation and score breakdown
    |
    |-- MiniLM semantic embedding
          |
          v
        MedQuAD embedding search
          |
          v
        Related medical information
```

## Models

The application can run the four base models with four training strategies:

| Fine-tuning method | DistilBERT | BioBERT | RoBERTa | BioMedBERT |
| --- | --- | --- | --- | --- |
| Full fine-tuning | [model](https://huggingface.co/cristian-untaru/distilbert-medical-triage) | [model](https://huggingface.co/cristian-untaru/biobert-medical-triage) | [model](https://huggingface.co/cristian-untaru/roberta-medical-triage) | [model](https://huggingface.co/cristian-untaru/biomedbert-medical-triage) |
| LoRA | [model](https://huggingface.co/cristian-untaru/lora-distilbert-medical-triage) | [model](https://huggingface.co/cristian-untaru/lora-biobert-medical-triage) | [model](https://huggingface.co/cristian-untaru/lora-roberta-medical-triage) | [model](https://huggingface.co/cristian-untaru/lora-biomedbert-medical-triage) |
| Bottleneck MLP Adapter | [model](https://huggingface.co/cristian-untaru/bottleneck-mlp-distilbert-medical-triage) | [model](https://huggingface.co/cristian-untaru/bottleneck-mlp-biobert-medical-triage) | [model](https://huggingface.co/cristian-untaru/bottleneck-mlp-roberta-medical-triage) | [model](https://huggingface.co/cristian-untaru/bottleneck-mlp-biomedbert-medical-triage) |
| Frozen Encoder | [model](https://huggingface.co/cristian-untaru/frozen-encoder-distilbert-medical-triage) | [model](https://huggingface.co/cristian-untaru/frozen-encoder-biobert-medical-triage) | [model](https://huggingface.co/cristian-untaru/frozen-encoder-roberta-medical-triage) | [model](https://huggingface.co/cristian-untaru/frozen-encoder-biomedbert-medical-triage) |

The input guard uses a separate intent classifier:

- [cristian-untaru/sortmed-intent-classifier](https://huggingface.co/cristian-untaru/sortmed-intent-classifier)

Model selection can be configured in [`backend/model_config.py`](backend/model_config.py).

## Input guard

The input guard is implemented in [`backend/input_guard/`](backend/input_guard/). It is intentionally placed before the triage models, because a classifier trained for triage will otherwise produce a class for almost any text.

The guard uses two layers:

- rule-based validation for malformed, too short, repetitive, non-English or adversarial input;
- an intent classifier that accepts only `symptom_description`.

Invalid intents are rejected with specific messages. The classifier distinguishes between:

- `symptom_description`;
- `medication_request`;
- `diagnosis_request`;
- `general_medical_question`;
- `non_medical`.

Only valid symptom descriptions are passed to the triage model.

## MedQuAD semantic retrieval

The related medical information section is based on context-aware semantic retrieval, not keyword matching.

The application uses:

- `sentence-transformers/all-MiniLM-L6-v2` to embed the user query;
- precomputed MedQuAD embeddings stored on Hugging Face;
- cosine similarity as the semantic relevance score;
- threshold filtering before displaying retrieved entries;
- optional cross-encoder reranking, controlled by environment configuration.

MedQuAD retrieval artifacts are loaded from:

- [cristian-untaru/medquad-retrieval-pretriage](https://huggingface.co/datasets/cristian-untaru/medquad-retrieval-pretriage)

The triage dataset used for model training is available at:

- [cristian-untaru/symcat-medical-triage-dataset](https://huggingface.co/datasets/cristian-untaru/symcat-medical-triage-dataset)

## Project structure

```text
.
|-- app.py                         # Main Streamlit page
|-- backend/                       # Authentication, database, inference and retrieval logic
|   `-- input_guard/               # Rule-based and intent-based input validation
|-- pages/                         # Streamlit multipage views
|-- ui/                            # Reusable UI components and rendering helpers
|-- assets/                        # CSS and static media
|-- content/legal/                 # Terms of Service and Privacy Policy
|-- scripts/                       # Utility scripts
|-- tests/                         # Unit, integration, AppTest and e2e tests
|-- USER_MANUAL.md                 # End-user manual
|-- requirements.txt               # Runtime dependencies
`-- requirements-dev.txt           # Test dependencies
```

## Local setup

The commands below assume Windows PowerShell and should be run from the application source directory, the folder that contains `app.py`.

Prerequisites:

- Python 3.10 or newer;
- access to a Supabase PostgreSQL database;
- SMTP credentials for email verification and password reset;
- internet access for downloading Hugging Face models and datasets.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For development and tests:

```powershell
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
```

## Streamlit secrets

The application requires a PostgreSQL connection string and email settings. Locally, these are read from `.streamlit/secrets.toml`. This file is ignored by Git and must not be committed.

Example structure:

```toml
[database]
url = "postgresql://..."

[email]
smtp_host = "smtp.gmail.com"
smtp_port = 465
smtp_user = "your-email@example.com"
smtp_password = "your-app-password"
from_address = "your-email@example.com"
```

Any hosted Streamlit environment must use the same values through Streamlit secrets.

Without valid Supabase and email credentials, account-related features such as registration, login, password reset and saved analysis history will not work.

## Running the application

SortMed is a Streamlit application. There is no separate backend service to start; the Python modules in `backend/` are imported by the Streamlit app during runtime.

```powershell
streamlit run app.py
```

The application initializes the PostgreSQL schema automatically if the required tables do not already exist.

## Testing

Regular tests:

```powershell
python -m pytest
```

End-to-end tests require the Streamlit app to be running in a separate terminal:

```powershell
streamlit run app.py --server.port 8501
```

Then run:

```powershell
$env:SORTMED_E2E_BASE_URL="http://localhost:8501"
python -m pytest -m e2e
```

Detailed testing instructions are available in [`tests/README.md`](tests/README.md).

## Deployment notes

The project can be deployed in a managed Streamlit environment or run locally for development and academic evaluation.

If deployed in a managed Streamlit environment, the required configuration is:

- Python dependencies from `requirements.txt`;
- Streamlit secrets containing the Supabase PostgreSQL URL and email credentials;
- access to the Hugging Face model and dataset repositories.

No local SQLite database is required in deployment. User accounts and saved analyses are persisted in Supabase PostgreSQL.

## Safety and limitations

SortMed is an academic pre-triage prototype. It has important limitations:

- it does not provide a medical diagnosis;
- it does not prescribe medication or treatment;
- it is not an emergency decision system;
- it expects symptom descriptions in English;
- model outputs may be uncertain or incorrect;
- MedQuAD entries provide related context, not personalized medical conclusions.

For severe, worsening or emergency symptoms, users should contact emergency services or a qualified healthcare professional.

## User documentation

The end-user manual is available in [`USER_MANUAL.md`](USER_MANUAL.md).

## External resources

Additional project resources are available here:

- Supplementary project materials: [Google Drive folder](https://drive.google.com/drive/u/0/folders/1J5O4G9R4Xy641l3nt5Qd9Fy2H1nMQV1d)  
  Contains training and evaluation resources, including repositories, notebooks, metrics and processed data used during development.
- Hugging Face profile: [cristian-untaru](https://huggingface.co/cristian-untaru)  
  Contains the published models, datasets and retrieval artifacts used by the application.
- GitHub repository: [cristian-untaru/sortmed-medical-pretriage](https://github.com/cristian-untaru/sortmed-medical-pretriage)  
  Contains the development version of the source code.

## Author

Cristian Untaru  
Bachelor's thesis project  
Faculty of Computer Science, West University of Timisoara
