This Privacy Policy explains how the Medical Pre-Triage Assistant collects, uses, stores, and protects users' personal data.

This application is an academic prototype developed by Cristian UNTARU, student at the Faculty of Computer Science, West University of Timișoara, as part of a bachelor's thesis project. The application is not a medical device, does not provide a medical diagnosis, and does not replace professional medical advice, a doctor's consultation, or emergency medical services.

### 01. Who is responsible for the data

The person responsible for this application is:

Cristian UNTARU,
Faculty of Computer Science,
West University of Timișoara.
Email: untarucristi89@gmail.com

For any question related to personal data, accounts, saved history, or data deletion, you can contact me at the email address above.

### 02. What data we collect

When you create an account, the application may collect:

- first name;
- last name;
- email address;
- password stored in a secure hashed form;
- account creation date.

When you use the symptom analysis feature, the application may save:

- the symptom description entered by you;
- the AI model used for the analysis;
- the estimated medical pre-triage category;
- model-generated scores;
- confidence level;
- explanatory messages shown to the user;
- retrieved medical context, if available;
- date and time of the analysis.

When you use the password recovery feature, the application may process:

- your email address;
- a temporary reset code;
- reset code expiration time;
- number of reset verification attempts.

### 03. Health-related data

The symptom description entered by you may contain information about your health. This information may be considered sensitive personal data under Article 9 of the General Data Protection Regulation, GDPR.

Please do not enter unnecessary personal information, such as national identification numbers, full address, phone number, financial information, or information about other people.

### 04. Why we use the data

The data is used to:

- create and manage user accounts;
- authenticate users;
- generate an AI-assisted medical pre-triage suggestion;
- save analysis history for authenticated users;
- support password recovery;
- test, demonstrate, and evaluate the application in an academic context;
- improve the security and functionality of the application.

### 05. Legal basis

Where GDPR applies, the processing of personal data may be based on:

- user consent, Article 6(1)(a) GDPR;
- providing the functionality requested by the user, Article 6(1)(b) GDPR;
- legitimate interest in application security, Article 6(1)(f) GDPR;
- explicit consent for data that may relate to health, Article 9(2)(a) GDPR.

Using the application and entering symptoms are voluntary.

### 06. How the AI analysis works

The application uses artificial intelligence and natural language processing models to interpret symptom descriptions and suggest an informative level of medical pre-triage.

The displayed result is only an informational recommendation. It must not be interpreted as a diagnosis, treatment, medical prescription, or final medical decision.

If your symptoms are severe, worsening, or may represent an emergency, you should immediately contact a doctor or emergency medical services.

### 07. Use of AI models

In the current implementation, the analysis is performed in the environment where the application runs, using AI models loaded by the application.

The application may download model files from external sources, such as Hugging Face, when they are not already available locally. However, the purpose of the application is not to send symptom descriptions to external AI chat services.

User input is not used by default to train new AI models.

### 08. Where data is stored

Account data, verification records, password reset records, and saved analysis history are stored in the PostgreSQL database configured for the application.

The configured hosted environment may use Streamlit Community Cloud for hosting and Supabase PostgreSQL for account and analysis persistence.

If the application is run locally for development, it can be configured to connect to the same external PostgreSQL database. Local development files are not the production database and are not used as the main persistence layer for the hosted application.

### 09. Passwords and password recovery

Passwords are not stored in plain text. They are transformed and stored as hashes using bcrypt.

For password recovery, the application may generate a temporary 6-digit code. The code is also stored in a secure form, has a limited validity period, and can only be used to reset the password.

If email sending is enabled, your email address may be used by the SMTP service configured in the application only for sending the password reset code.

### 10. Guest usage

The application may also be used as a guest.

In this case, the symptom analysis may be kept temporarily in the current application session in order to display the result, but it is not saved to an account history.

### 11. Local preferences

The application may store certain interface preferences locally in the browser, such as the light or dark theme.

These preferences are used only to improve the user experience and do not represent medical data.

### 12. Who we share data with

Data is not sold and is not used for advertising.

Access to the database should be limited to the project developer and, if necessary, authorized people involved in the academic evaluation or supervision of the project.

If the application is configured to send password recovery emails, your email address may be processed by the technical provider used to send that message.

### 13. How long we keep data

Account data and saved analysis history may be kept for as long as the application is maintained, tested, or evaluated in an academic context.

Password reset codes expire after a short period, but technical records may remain in the database until database cleanup or maintenance is performed.

You can delete your account directly from the application account menu. When account deletion is confirmed, the application deletes the account profile, the saved analysis history linked to that account, and password reset or verification code records linked to the account email address from the application database.

You may also request deletion of your account and associated data by sending an email to: untarucristi89@gmail.com

### 14. Security

The application uses technical measures such as:

- password hashing with bcrypt;
- temporary password reset codes;
- limited reset verification attempts;
- separation between account data and analysis logic;
- storage of account and analysis data in Supabase PostgreSQL for the configured hosted environment.

However, no application can guarantee absolute security. Since this is an academic prototype, you should avoid entering unnecessary personal information or highly detailed medical information.

### 15. Your rights

Depending on applicable law, including GDPR, you may have the following rights:

- the right to access your data;
- the right to correct inaccurate data;
- the right to request deletion of your data;
- the right to restrict processing;
- the right to object to processing;
- the right to data portability;
- the right to withdraw consent;
- the right to lodge a complaint with a data protection authority.

In Romania, the competent authority is the National Supervisory Authority for Personal Data Processing, ANSPDCP.

The application provides an in-app account deletion option. You may also contact the developer if you need help exercising any of these rights.

### 16. Use by minors

The application is not intended to be used independently by minors for making medical decisions.

If used in an educational or demonstrative context, it should be used under appropriate supervision.

### 17. Medical limitation

Medical Pre-Triage Assistant has an informational and educational purpose.

The application must not be used for medical emergencies, diagnosis, treatment, or as a replacement for professional medical consultation.

For any real medical concern, you should consult a doctor or an authorized medical service.

### 18. Changes to this policy

This Privacy Policy may be updated as the application develops.

The updated version will be displayed in the application.

### 19. Contact

For questions about this Privacy Policy or your personal data, you can contact:

Cristian UNTARU,
Faculty of Computer Science,
West University of Timișoara.
Email: untarucristi89@gmail.com
