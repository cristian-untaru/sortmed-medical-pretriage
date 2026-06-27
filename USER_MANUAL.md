# SortMed User Manual

SortMed is a web application for AI-assisted medical pre-triage. It allows users to describe symptoms in English and receive an indicative recommendation about the level of care that may be appropriate.

SortMed does not provide a medical diagnosis, does not prescribe medication, and does not replace professional medical advice. If symptoms are severe, rapidly worsening, or feel urgent, contact emergency services or a qualified healthcare professional.

## 1. Accessing the Application

SortMed can be accessed through the application environment configured by the project maintainer.

The application requires an internet connection and a modern browser such as Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari.

## 2. Ways to Use SortMed

SortMed can be used in two ways:

- with a user account;
- as a guest user.

A user account allows saved analyses, account statistics, and access to previous symptom checks. Guest mode is useful for quick testing, but guest results are not saved to a personal history.

## 3. Creating an Account

To create a new account:

1. Click `Get Started`.
2. Select `Create account`.
3. Enter your first name, last name, email address, and password.
4. Accept the Terms of Service and Privacy Policy.
5. Enter the 6-digit verification code sent by email.

After the email address is verified, the account is ready to use.

## 4. Logging In and Resetting the Password

To log in, use the email address and password set during account creation.

If you forgot your password:

1. Click `Forgot your password?`.
2. Enter your email address.
3. Check your inbox for the verification code.
4. Enter the code and choose a new password.

If the verification email does not appear, check the Spam or Junk folder before requesting a new code.

## 5. Describing Symptoms

Symptom descriptions must be written in English. The text should be clear and specific enough for the system to understand what you feel, where the symptom appears, and when it started.

Good examples:

```text
I have chest pain and shortness of breath.
I have had a headache and dizziness since yesterday.
I feel nauseous and I have been vomiting since this morning.
```

Poor examples:

```text
Hello
What medicine should I take?
Do I have migraine?
ma doare capul
head tac toe pain
```

SortMed validates the text before running the triage model. Very short, repetitive, non-medical, non-English, diagnostic, or medication-seeking inputs are rejected and the user is asked to rewrite the description.

## 6. Choosing an AI Model

On the `Medical Assistance` page, two dropdowns are available:

- `Select fine-tuning method`;
- `Select base model`.

Available fine-tuning methods:

- `Full fine-tuning`;
- `LoRA`;
- `Bottleneck MLP Adapter`;
- `Frozen Encoder`.

Available base models:

- `DistilBERT`;
- `BioBERT`;
- `RoBERTa`;
- `BioMedBERT`.

All model variants return the same type of recommendation: `Self-monitor`, `Consult GP`, or `Urgent`. The selected model can influence the confidence score and the probability distribution. For normal use, the default model selection can be left unchanged.

## 7. Running an Analysis

To analyze a symptom description:

1. Select the fine-tuning method and base model, if needed.
2. Write the symptom description in the text area.
3. Click `Analyze Symptoms`.

If the input is accepted, SortMed runs the selected model and displays the recommendation. If the input is rejected by the safety checks, the application shows a message explaining how to rewrite it.

## 8. Understanding the Recommendation

SortMed can return one of three recommendations:

- `Self-monitor` - the symptoms appear mild and can be monitored;
- `Consult GP` - a non-emergency medical evaluation is recommended;
- `Urgent` - the symptoms may require prompt medical attention.

These results are indicative. They should not be treated as a confirmed medical decision, especially when symptoms are severe, persistent, or worsening.

## 9. Confidence and Score Breakdown

The `Confidence` section shows how strongly the model supports the displayed recommendation.

The `Score Breakdown` section shows the model scores for all three classes:

- `Self-monitor`;
- `Consult GP`;
- `Urgent`.

A higher score means that the model considers that class more likely for the submitted description. If the top scores are close to each other, the result is more uncertain and should be interpreted with extra caution.

## 10. About This AI Analysis

The `About this AI analysis` section explains the model configuration used for the result.

It can include:

- the base AI model;
- the fine-tuning method;
- the task performed by the model;
- the possible result classes;
- the Hugging Face model identifier used by the application.

This section is included for transparency. It does not change the fact that the output is only a pre-triage recommendation.

## 11. Related Medical Information

After an accepted analysis, SortMed may display related medical information from the MedQuAD dataset.

This feature uses semantic retrieval. The user's symptom description is converted into a numerical embedding with a sentence embedding model, then compared with precomputed MedQuAD embeddings. Only entries with sufficient semantic relevance are shown.

`Semantic relevance` indicates how close the retrieved MedQuAD entry is to the submitted symptom description. A higher value means a stronger semantic match.

If no related medical information is displayed, it does not mean the symptom is unimportant. It only means that no MedQuAD entry passed the relevance threshold for that specific input.

## 12. Results Page

The `Results` page shows the current analysis and the saved analysis history for logged-in users.

For each saved analysis, the user can review:

- the date and time;
- the recommendation;
- the confidence score;
- the selected model and fine-tuning method;
- the symptom description;
- the score breakdown;
- related medical information, when available.

Guest users do not have a personal saved history.

## 13. Account Page

The account page shows profile information and usage statistics.

Depending on the available history, it can show:

- the total number of analyses;
- the most frequently used base model;
- the most frequent recommendation;
- average confidence;
- the distribution of recommendations;
- recent account activity.

PEFT variants are grouped under their base model in the main account statistics, so the overview remains easy to read.

## 14. Data Saved by the Application

For logged-in users, SortMed may save:

- account data required for authentication;
- symptom descriptions submitted for analysis;
- the selected model;
- the returned recommendation;
- confidence and class scores;
- related medical information, when available.

The data is used to display the history and account statistics. Users should avoid entering personal details that are not needed to describe the symptoms.

More information is available in the `Terms of Service` and `Privacy Policy` sections inside the application.

## 15. Limitations

SortMed has several important limitations:

- it does not provide a diagnosis;
- it does not recommend medication or treatment;
- it does not replace a doctor or emergency service;
- it expects symptom descriptions in English;
- it may reject unclear, very short, repetitive, or question-like inputs;
- different model selections may produce different confidence scores;
- MedQuAD information is contextual reference material, not personalized medical advice.

For severe chest pain, breathing difficulty, fainting, sudden neurological symptoms, severe allergic reactions, major injuries, or any situation that feels urgent, contact emergency services immediately.

## 16. Common Issues

### I did not receive the verification email

Check the Spam or Junk folder and confirm that the email address was entered correctly. If needed, request a new verification code.

### My symptom description was rejected

Rewrite it as a clear English sentence. Include what you feel, where the symptom is located, and how long it has been present.

### I cannot see my analysis history

History is available only for logged-in users. If you use Guest mode, results are not saved to an account.

### The first analysis is slower than expected

The first request can take longer because the application may need to load machine learning models and retrieval resources. Later requests are usually faster because cached resources are reused.

## 17. Recommended Use

Use SortMed as an initial orientation tool. The result can help you understand which level of care may be appropriate, but it should always be confirmed by a qualified healthcare professional when symptoms persist, worsen, or cause concern.
