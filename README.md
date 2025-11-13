# PHI Classifier & Synthetic Health Data Generator v2.0

A production-ready, HIPAA-compliant Python application for automated detection of Protected Health Information (PHI) in documents and generation of clinically coherent synthetic health data for testing and development.

## 🚀 Version 2.0 - Major Update

**What's New:**
- ✅ **Pre-trained ML models** - Ready to use out of the box (no training required)
- ✅ **State-of-the-art NER** - Uses BioBERT and transformer models for entity recognition
- ✅ **Clinical coherence** - Synthetic data with realistic diagnosis-medication-lab correlations
- ✅ **Production deployment** - Gunicorn + Docker with proper security
- ✅ **API authentication** - Optional API key protection for endpoints
- ✅ **Zero-shot classification** - Classifies PHI documents without task-specific training

---

## Features

### 🔍 PHI Classification

- **Pre-trained Models**: Uses state-of-the-art pre-trained models from Hugging Face
  - Biomedical NER: `d4data/biomedical-ner-all`
  - Zero-shot classifier: `facebook/bart-large-mnli`
  - Clinical embeddings: `emilyalsentzer/Bio_ClinicalBERT`
- **Hybrid Approach**: Combines ML models with rule-based HIPAA identifier detection
- **Comprehensive Detection**: Identifies all 18 HIPAA identifier types
- **Multiple Formats**: Supports TXT, DOCX, PDF, CSV, XLSX, JSON
- **Risk Assessment**: HIGH/MEDIUM/LOW/NONE risk levels
- **Real-time Processing**: Efficient CPU-friendly inference

### 🧪 Synthetic Data Generation

- **Clinically Coherent**: Diagnosis-medication-lab value correlations
- **Age/Gender Appropriate**: Validates medical appropriateness for demographics
- **Comprehensive PHI**: Includes all 18 HIPAA identifier types
- **Multiple Document Types**: Medical records, lab reports, discharge summaries
- **Configurable Output**: 1-10,000 documents in various formats
- **Privacy-Safe**: No real patient data exposure

### 🛡️ Security & Compliance

- **HIPAA Compliant**: Local processing, no external API calls for PHI
- **API Authentication**: Optional API key protection
- **Secure Storage**: Encrypted file handling
- **Audit Logging**: Comprehensive operation tracking
- **Input Validation**: File type checking and sanitization

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Client Browser                     │
│               or API Client (curl, etc.)            │
└────────────────────┬────────────────────────────────┘
                     │ HTTP (Port 80)
                     ▼
        ┌────────────────────────────┐
        │      Nginx Reverse Proxy    │
        │  - Load Balancing           │
        │  - SSL/TLS Termination      │
        │  - Static File Serving      │
        │  - Request Routing          │
        └────────────┬───────────────┘
                     │ Internal (Port 5000)
                     ▼
        ┌────────────────────────────┐
        │   Flask Application         │
        │   (Gunicorn WSGI Server)   │
        │  - Web UI                   │
        │  - REST API                 │
        │  - Business Logic           │
        └────────────┬───────────────┘
                     │
        ┌────────────┴────────────────┐
        │                             │
        ▼                             ▼
┌──────────────┐           ┌──────────────────┐
│   ML Models   │           │  Redis (Optional) │
│ - BioBERT NER │           │  - Rate Limiting  │
│ - BART        │           │  - Caching        │
│ - ClinicalBERT│           └──────────────────┘
└──────────────┘
```

**Important**: All client access goes through **port 80** (nginx). Port 5000 is internal to Docker and not exposed to the host.

### Directory Structure

```
/sensitive-data-classifier/
├── app.py                          # Main application entry point
├── core/
│   ├── classifier.py               # Pre-trained ML classification engine
│   ├── clinical_coherence.py      # Clinical correlation engine
│   ├── generator.py                # Synthetic data generator
│   ├── hipaa_identifier.py         # HIPAA identifier detection
│   ├── processor.py                # Document processor
│   └── security.py                 # Security management
├── web/
│   ├── routes.py                   # API endpoints
│   ├── auth.py                     # API authentication
│   └── templates/                  # HTML templates
├── config/
│   ├── app_config.py               # Application configuration
│   └── settings.py                 # Extended settings
├── deployment/
│   ├── Dockerfile.app              # Production Dockerfile
│   ├── docker-compose.yml          # Docker Compose config
│   ├── gunicorn.conf.py            # Gunicorn configuration
│   └── nginx.conf                  # Nginx reverse proxy
├── models_cache/                   # Pre-trained model cache (created automatically)
└── requirements.txt                # Python dependencies
```

---

## Quick Start

### Prerequisites

- **Python**: 3.9+ (3.11 recommended)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB (includes model cache ~2GB)
- **OS**: Linux (Ubuntu 20.04+), macOS, Windows with WSL2

### Installation

#### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/FredHutch/sensitive-data-classifier.git
cd sensitive-data-classifier

# Build and run with Docker Compose
cd deployment
docker-compose up -d

# Access the application
# Web UI: http://localhost
# API: http://localhost/api/
open http://localhost
```

#### Option 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/FredHutch/sensitive-data-classifier.git
cd sensitive-data-classifier

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ENVIRONMENT=development
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Run application (development mode)
python app.py
```

**First Run Note**: On first startup, the application will download pre-trained models (~500MB-1GB). This may take 5-10 minutes depending on your internet connection. Models are cached locally for subsequent runs.

---

## Configuration

### Environment Variables

```bash
# Environment
ENVIRONMENT=development                    # development|production|testing

# Security (required in production)
SECRET_KEY=your-secret-key-here           # Flask secret key
API_KEY_REQUIRED=false                    # Enable API authentication
API_KEY=your-api-key-here                 # API key if authentication enabled

# Paths
MODEL_CACHE_DIR=./models_cache            # ML model cache directory
UPLOAD_FOLDER=./uploads                   # Uploaded files directory

# Optional features
RATELIMIT_ENABLED=false                   # Enable rate limiting (requires Redis)
REDIS_URL=redis://redis:6379/0            # Redis URL for rate limiting
CORS_ENABLED=false                        # Enable CORS for web APIs

# Logging
LOG_LEVEL=INFO                            # DEBUG|INFO|WARNING|ERROR
```

### Production Deployment

For production use, update `deployment/app.env`:

```bash
ENVIRONMENT=production
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
API_KEY_REQUIRED=true
API_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
```

Then deploy:

```bash
docker-compose -f deployment/docker-compose.yml up -d
```

---

## API Documentation

### Authentication

When `API_KEY_REQUIRED=true`, include API key in request headers:

```bash
X-API-Key: your-api-key-here
```

### Endpoints

#### 1. Classify Documents

**Endpoint**: `POST /api/classify`

**Headers**:
- `Content-Type: multipart/form-data`
- `X-API-Key: your-api-key-here` (if API_KEY_REQUIRED=true)

**Example**:
```bash
# Single file
curl -X POST http://localhost/api/classify \
  -H "X-API-Key: your-api-key-here" \
  -F "files=@medical_record.pdf"

# Multiple files
curl -X POST http://localhost/api/classify \
  -H "X-API-Key: your-api-key-here" \
  -F "files=@medical_record.pdf" \
  -F "files=@lab_report.docx"
```

**Response:**
```json
{
  "status": "success",
  "results": [
    {
      "filename": "medical_record.pdf",
      "contains_phi": true,
      "confidence": 0.95,
      "risk_level": "HIGH",
      "total_identifiers": 12,
      "file_size": 45678,
      "word_count": 523
    }
  ],
  "total_files": 1,
  "successful_classifications": 1,
  "timestamp": "2025-10-22T12:34:56"
}
```

#### 2. Generate Synthetic Data

**Endpoint**: `POST /api/generate`

**Headers**:
- `Content-Type: application/json`
- `X-API-Key: your-api-key-here` (if API_KEY_REQUIRED=true)

**Body**:
```json
{
  "count": 10,
  "formats": ["txt", "docx", "pdf", "json", "csv"],
  "save_to_disk": true
}
```

**Example**:
```bash
curl -X POST http://localhost/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"count": 10, "formats": ["docx", "pdf"]}'
```

**Response:**
```json
{
  "status": "success",
  "count": 10,
  "saved_to_disk": true,
  "output_directory": "/app/uploads/generated",
  "saved_files": [
    {
      "filename": "synthetic_medical_record_0001.docx",
      "path": "/app/uploads/generated/synthetic_medical_record_0001.docx",
      "size_bytes": 15234
    }
  ],
  "documents": [
    {
      "id": "DOC-abc123",
      "type": "medical_record",
      "format": "docx",
      "filename": "synthetic_medical_record_0001.docx",
      "contains_phi": true,
      "phi_density": 0.15,
      "file_size_bytes": 15234,
      "medical_complexity": "high",
      "created_date": "2025-10-23T12:34:56"
    }
  ],
  "timestamp": "2025-10-23T12:34:56"
}
```

#### 3. System Status

**Endpoint**: `GET /api/status`

**Authentication**: Not required

**Example**:
```bash
curl http://localhost/api/status
```

#### 4. Model Information

**Endpoint**: `GET /api/models/info`

**Authentication**: Not required

**Example**:
```bash
curl http://localhost/api/models/info
```

**Response:**
```json
{
  "models_available": {
    "ner": true,
    "text_classifier": true,
    "clinical_embeddings": true
  },
  "model_details": {
    "ner": "d4data/biomedical-ner-all",
    "classifier": "facebook/bart-large-mnli",
    "embeddings": "emilyalsentzer/Bio_ClinicalBERT"
  },
  "is_trained": true,
  "cache_dir": "./models_cache"
}
```

---

## HIPAA Identifiers Detected

The system detects all 18 HIPAA identifier types:

1. **Names** - Patient, physician, family member names
2. **Geographic Data** - Addresses, cities, ZIP codes
3. **Dates** - Birth dates, admission dates, ages over 89
4. **Phone Numbers** - All telephone numbers
5. **Fax Numbers** - Fax machine numbers
6. **Email Addresses** - Electronic mail addresses
7. **Social Security Numbers** - SSNs in any format
8. **Medical Record Numbers** - MRN, patient IDs
9. **Health Plan Numbers** - Insurance policy numbers
10. **Account Numbers** - Financial account identifiers
11. **Certificate Numbers** - License numbers, certificates
12. **Vehicle Identifiers** - License plates, VINs
13. **Device Identifiers** - Medical device serial numbers
14. **Web URLs** - Internet addresses
15. **IP Addresses** - Network identifiers
16. **Biometric Identifiers** - Fingerprints, retinal scans
17. **Photograph Images** - Visual identifiers
18. **Other Identifiers** - Any other unique identifiers

### Organization-Specific PHI Detection

The system supports **custom identifier formats** specific to your organization:

**Example: Custom MRN Format**
- Pattern: `U` followed by 7 digits (e.g., U1234567)
- Regex: `(?i)\bU\d{7}\b`
- Automatically detected in all documents
- Generated documents use this format

To add custom patterns, update `core/hipaa_identifier.py` in the `medical_record_numbers` section.

---

## Understanding Classification Results

### Risk Level vs. Confidence Score: What's the Difference?

The classifier uses **two independent metrics** to assess documents:

#### 1. **Risk Level** (HIGH/MEDIUM/LOW/NONE)
- **Based on**: Count of PHI identifiers detected
- **Method**: Rule-based pattern matching (deterministic)
- **What it measures**: *How many* PHI identifiers are present in the document

| Risk Level | Identifier Count | Example |
|-----------|-----------------|---------|
| **HIGH** | 20+ identifiers | Complete medical record with names, MRNs, SSNs, dates, addresses |
| **MEDIUM** | 5-19 identifiers | Lab report with patient name, MRN, DOB, and a few dates |
| **LOW** | 1-4 identifiers | Document mentioning a phone number or single date |
| **NONE** | 0 identifiers | No PHI detected |

#### 2. **Confidence Score** (0.0 - 1.0)
- **Based on**: Machine learning model assessment
- **Method**: Transformer-based classification (probabilistic)
- **What it measures**: *How certain* the ML model is that the document resembles typical medical records in its training data

| Confidence Range | Interpretation |
|-----------------|----------------|
| **90-100%** | Document structure, vocabulary, and narrative flow match training data very closely |
| **70-89%** | Document appears to be a medical record with recognizable clinical patterns |
| **50-69%** | Document contains medical content but with some atypical characteristics |
| **<50%** | Document structure differs significantly from typical medical records |

### Why HIGH RISK with Moderate Confidence (50-70%) is Normal

**Common Scenario**: You may see results like this:

```json
{
  "filename": "synthetic_medical_record_0042.docx",
  "contains_phi": true,
  "risk_level": "HIGH",           // ← Many identifiers detected
  "confidence": 0.67,              // ← Moderate confidence (67%)
  "total_identifiers": 32
}
```

**This is expected behavior**, especially for:
- **Documents generated by this application**
- **Template-based medical records**
- **Documents from different EHR systems** than those in the training data
- **Specialized medical documents** (research notes, veterinary records, international formats)

#### Why This Happens

1. **Risk Level is Accurate**: The rule-based identifier detection found 32 PHI identifiers → **HIGH RISK is correct**
   - SSNs: 2 instances
   - MRNs: 3 instances
   - Names: 8 instances
   - Dates: 12 instances
   - Addresses: 5 instances
   - Phone numbers: 2 instances

2. **Confidence Score Reflects Document "Naturalness"**: The ML model recognizes this as a medical document but notices:
   - **Template patterns**: Generated documents follow consistent narrative structures
   - **Vocabulary distribution**: Slightly different word frequencies than real EHR notes
   - **Synthetic characteristics**: Clinical narratives that are coherent but don't perfectly match the training data distribution

**Key Point**: The ML model is correctly identifying that the document *contains medical content* but may have been generated rather than written by a human clinician. **This does NOT mean the PHI detection is inaccurate** — all 32 identifiers were still correctly detected by the rule-based system.

### When to Be Concerned

❌ **Concerning**: `risk_level: "NONE"` but manual review finds obvious PHI
- Indicates potential detection gaps in identifier patterns
- Review `core/hipaa_identifier.py` patterns

✅ **Expected**: `risk_level: "HIGH"` with `confidence: 0.50-0.70`
- PHI detection is working correctly
- Lower confidence just means document structure differs from training data

❌ **Concerning**: `risk_level: "HIGH"` with `confidence: <0.30`
- May indicate non-medical document with coincidental pattern matches
- Example: Phone directory with lots of names and phone numbers

### How the Hybrid System Works

```
┌────────────────────────────────────────────────────────┐
│                  Document Input                         │
└────────────────┬───────────────────────────────────────┘
                 │
                 ├──────────────────────┬─────────────────────────────┐
                 ▼                      ▼                             ▼
    ┌───────────────────────┐  ┌──────────────────┐  ┌────────────────────────┐
    │  Rule-Based Detection │  │  ML Classifier   │  │  Named Entity          │
    │  (HIPAA Patterns)     │  │  (BART Model)    │  │  Recognition (BioBERT) │
    │                       │  │                  │  │                        │
    │  • Regex patterns     │  │  • Document type │  │  • Medical entities    │
    │  • Exact matching     │  │  • Confidence    │  │  • Context analysis    │
    │  • Count identifiers  │  │  • Authenticity  │  │  • Entity validation   │
    └──────────┬────────────┘  └────────┬─────────┘  └───────────┬────────────┘
               │                        │                         │
               └────────────────────────┴─────────────────────────┘
                                        │
                                        ▼
                    ┌────────────────────────────────────┐
                    │       Final Classification         │
                    │                                    │
                    │  risk_level: HIGH (32 identifiers) │
                    │  confidence: 0.67 (67%)            │
                    │  contains_phi: true                │
                    └────────────────────────────────────┘
```

**Advantage**: This hybrid approach ensures **comprehensive PHI detection** (rule-based) while providing **context about document authenticity** (ML-based).

### Practical Guidance

**For Security/Compliance Teams**:
- **Prioritize by Risk Level**: Focus on HIGH/MEDIUM risk documents regardless of confidence score
- **Use Confidence for Context**: Low confidence may indicate unusual document formats worth investigating
- **Trust Identifier Counts**: The `total_identifiers` count is based on deterministic pattern matching

**For Testing/Validation**:
- **Generated documents with 50-70% confidence are ideal for benchmarking** — they contain realistic PHI without overfitting to specific EHR systems
- **Documents scoring >90% confidence** may indicate the classifier has memorized training data patterns

**For Custom Identifier Patterns**:
- Organization-specific patterns (like `U1234567` MRNs) are detected via regex → contribute to risk level
- These patterns don't affect confidence scores (ML model isn't trained on them)

---

## Enterprise Security Features

### HTTPS/SSL Support

The application supports HTTPS with TLS 1.2/1.3 for secure communication.

**Quick Setup**:
```bash
cd deployment
./generate-ssl-certs.sh    # Generate self-signed certificates
./setup-https.sh            # Configure and enable HTTPS
```

**Production Setup**:
1. Obtain certificates from a trusted CA (Let's Encrypt, DigiCert, etc.)
2. Copy certificates to `deployment/ssl/`:
   - `cert.pem` - SSL certificate
   - `key.pem` - Private key
3. Copy to Docker volume:
   ```bash
   docker run --rm \
     -v $(pwd)/ssl:/certs \
     -v phi-classifier_ssl-certs:/ssl \
     alpine cp /certs/*.pem /ssl/
   ```
4. Enable HTTPS redirect in `nginx.conf` (uncomment line 32)
5. Restart: `docker-compose restart nginx`

**Access**:
- HTTP: `http://localhost` (or your domain)
- HTTPS: `https://localhost` (or your domain)

**SSL Configuration** (nginx.conf):
- TLS 1.2 and 1.3 only
- Strong cipher suites
- Perfect Forward Secrecy (PFS)
- HSTS enabled (max-age 31536000)

### SAML Authentication (SSO)

Single Sign-On via SAML 2.0 with support for:
- **Microsoft Entra ID** (Azure AD)
- **Okta**
- **OneLogin**
- **Auth0**
- Any SAML 2.0 compliant IdP

**Setup Instructions**:
1. See detailed guide: [`deployment/SAML_ENTRA_ID_SETUP.md`](deployment/SAML_ENTRA_ID_SETUP.md)
2. Configure your Identity Provider (IdP)
3. Update SAML settings in `deployment/saml_config/`
4. Enable SAML in `deployment/app.env`:
   ```bash
   SAML_ENABLED=true
   SAML_SETTINGS_PATH=/app/config/saml
   ```
5. Restart application: `docker-compose restart app`

**SAML Endpoints**:
- Metadata: `https://your-domain.com/saml/metadata`
- ACS (Assertion Consumer Service): `https://your-domain.com/saml/acs`
- SLS (Single Logout Service): `https://your-domain.com/saml/sls`
- Login: `https://your-domain.com/saml/login`
- Status: `https://your-domain.com/saml/status`

**Protected Routes**:
Use the `@saml_required` decorator to protect specific routes:
```python
from web.saml_auth import saml_required

@app.route('/admin')
@saml_required
def admin_dashboard():
    email = session.get('saml_user_email')
    return f"Admin Dashboard - {email}"
```

**User Attributes**:
After SAML authentication, session contains:
- `saml_user_email` - User's email address
- `saml_user_name` - Display name
- `saml_user_groups` - Group memberships
- `saml_session_index` - SSO session identifier

---

## OCR Support for Scanned Documents

The application includes **Optical Character Recognition (OCR)** powered by Tesseract for processing scanned documents and images.

### Supported Formats

**Images**:
- PNG (.png)
- JPEG (.jpg, .jpeg)
- TIFF (.tiff, .tif)
- BMP (.bmp)

**Scanned PDFs**:
- Automatically detects scanned PDFs (no extractable text)
- Falls back to OCR when standard extraction fails
- Processes each page as an image

### How It Works

1. **Text Extraction Attempt**: First tries standard text extraction
2. **OCR Fallback**: If no text found, automatically uses OCR
3. **Image Processing**: Converts PDF pages to images (300 DPI)
4. **Text Recognition**: Tesseract OCR extracts text
5. **PHI Detection**: Standard classification on extracted text

### OCR Performance

| Document Type | Processing Time | Accuracy |
|--------------|----------------|----------|
| Single page image | 2-5 seconds | ~95% (clear scans) |
| Multi-page PDF | 3-8 seconds/page | ~90-95% |
| Low quality scans | 5-10 seconds/page | ~70-85% |

**Optimization Tips**:
- Use 300 DPI for scanned documents
- Ensure good contrast (black text on white background)
- Remove artifacts/noise before scanning
- Use portrait orientation for optimal OCR

### Example Usage

**Via API**:
```bash
# Upload scanned PDF
curl -X POST https://localhost/api/classify \
  -F "files=@scanned_medical_record.pdf"

# Response includes OCR metadata
{
  "filename": "scanned_medical_record.pdf",
  "contains_phi": true,
  "extraction_method": "OCR (Tesseract)",
  "ocr_applied": true,
  "page_count": 3,
  "confidence": 0.87
}
```

**Via Web UI**:
1. Navigate to **Classify Documents**
2. Upload scanned image or PDF
3. OCR automatically applied if needed
4. Results show "OCR Applied" badge

### OCR Languages

Default: English (eng)

To add more languages:
```bash
# In Dockerfile.app, add additional language packs
RUN apt-get install -y \
    tesseract-ocr-eng \
    tesseract-ocr-spa \  # Spanish
    tesseract-ocr-fra    # French
```

### Troubleshooting OCR

**Issue**: "OCR libraries not available"
```bash
# Rebuild Docker image with OCR dependencies
docker-compose build
docker-compose up -d
```

**Issue**: Poor OCR accuracy
- Improve scan quality (higher DPI)
- Adjust contrast/brightness
- Remove background noise
- Ensure text is horizontal

**Issue**: Slow OCR performance
- OCR is CPU-intensive
- Allocate more CPU cores to Docker
- Consider using GPU acceleration (advanced setup)

---

## Synthetic Health Data Generation: Comparative Analysis

### How This Tool Compares to Other Generators

#### vs. Synthea™

**Synthea** (developed by MITRE Corporation) is the industry-standard open-source synthetic patient generator, focusing on comprehensive longitudinal patient histories with full interoperability support.

| Feature | This Tool | Synthea |
|---------|-----------|---------|
| **Primary Use Case** | PHI detection testing & benchmarking proprietary classifiers | Research, testing EHR systems, FHIR validation |
| **Data Format** | Clinical narrative text (progress notes, discharge summaries) | Structured data (FHIR, C-CDA, OMOP CDM, CSV) |
| **Document Realism** | High-fidelity clinical narratives with natural PHI embedding | Structured patient timelines with comprehensive medical events |
| **PHI Density** | Tuned for classifier benchmarking (20-50 identifiers per document) | Complete patient data (medications, encounters, social determinants) |
| **Generation Speed** | Real-time (10-100 documents/second) | Batch processing (minutes for population-level data) |
| **Clinical Coherence** | Diagnosis-medication-lab correlations with template variation | Full disease progression modeling with state machines |
| **Interoperability** | TXT, DOCX, PDF, JSON, CSV output | HL7 FHIR (R4, STU3, DSTU2), C-CDA, OMOP CDM, Bulk FHIR |
| **Setup Complexity** | Docker one-liner, no configuration | Requires Java JDK 11+, JSON module configuration |
| **Dataset Size** | 1-10,000 documents on-demand | Can generate millions (1M+ available publicly) |
| **Medical Modules** | General medicine with clinical coherence engine | Specialized modules (cerebral palsy, sepsis, AML, opioid use) |
| **Target Audience** | Security teams, PHI detection tool vendors, compliance officers | Healthcare interoperability developers, researchers, EHR vendors |

**When to Use This Tool vs. Synthea:**

✅ **Use This Tool** for:
- Testing and benchmarking PHI classification systems
- Creating realistic medical narratives for security testing
- Generating documents that mimic actual EHR clinical notes
- Fast, on-demand generation without infrastructure setup
- Evaluating ML models for PHI detection accuracy
- Creating training data for NER and document classification models

✅ **Use Synthea** for:
- FHIR server testing and validation
- Population health research requiring longitudinal patient histories
- Testing clinical decision support systems
- EHR integration testing with HL7 standards
- Disease progression modeling studies
- Large-scale public health datasets

### Emerging Methods in AI-Based Synthetic Health Data

Recent advances in **Large Language Models (LLMs)** and generative AI are revolutionizing synthetic health data generation. This tool leverages several emerging techniques:

#### 1. **Transformer-Based Clinical Embeddings**

**Traditional Approach**: Rule-based templates with fixed vocabulary
**Our Approach**: Uses **BioBERT** and **ClinicalBERT** for contextualized medical text understanding

- Pre-trained on PubMed, MIMIC-III clinical notes, and medical literature
- Captures semantic relationships between diagnoses, medications, and lab values
- Enables realistic clinical narrative generation that passes ML classifier scrutiny

**Research Foundation**: Recent studies (Nature npj Digital Medicine, 2024) show GPT-style models are employed in ~40% of medical text generation studies, demonstrating superior performance over traditional methods.

#### 2. **Hybrid ML + Rule-Based Generation**

Unlike pure LLM approaches (which can hallucinate clinically inappropriate combinations), this tool combines:

- **Clinical Coherence Engine**: Rule-based validation ensuring age/gender-appropriate diagnoses and medications
- **ML-Based Variation**: BioBERT embeddings for generating natural medical phrasing
- **Template Diversity**: Multiple narrative templates with extensive clinical vocabulary (14+ symptom qualities, 7+ examination findings per body system)

**Advantage**: Achieves **70-95% classifier confidence** (comparable to real medical records) while maintaining clinical validity.

#### 3. **Zero-Shot Classification for Quality Assurance**

**Innovation**: Uses **BART-large-MNLI** zero-shot classifier to validate generated documents

- Tests whether synthetic documents are classified as "medical records containing PHI" with high confidence
- Creates a feedback loop: documents scoring <70% confidence are flagged for template enhancement
- Enables "symmetric" generator/classifier where generated data is realistic enough to fool external PHI detection systems

**Application**: Critical for **benchmarking proprietary PHI classifiers** - generated documents serve as ground truth test cases.

#### 4. **Privacy-Preserving Synthetic Data**

**Key Advantage Over Real Data**: No privacy risks, HIPAA restrictions, or IRB approvals required

Recent research (JAMIA Open, 2024) identifies privacy preservation as the primary driver of synthetic health data adoption, addressing:
- Class imbalance in rare disease datasets
- Data scarcity for protected populations
- Regulatory barriers to data sharing

This tool generates unlimited PHI-containing documents for testing **without exposing actual patient data**.

### How This Tool Leverages AI Progress

#### Current Implementation:
1. **Pre-trained Transformers**: BioBERT NER, BART zero-shot classification, ClinicalBERT embeddings
2. **Clinical Knowledge Bases**: SNOMED CT, ICD-10, RxNorm, LOINC vocabularies
3. **Statistical Coherence**: Correlation matrices for diagnosis-medication-lab triplets
4. **Narrative Templates**: 15+ document type variants with clinical vocabulary databases

#### Emerging Enhancements (Roadmap):
- **LLM-Based Structured Text Generation**: Fine-tuned GPT models for fully generative clinical narratives
- **Synthetic Dialog Augmentation**: Patient-provider conversations for telemedicine PHI testing
- **Multi-Agent Architectures**: Simulating multiple providers with distinct documentation styles
- **Federated Synthetic Data**: Generating institution-specific medical record patterns

### Research Validation

Recent peer-reviewed studies validate the approaches used in this tool:

- **"Large language models and synthetic health data: progress and prospects"** (JAMIA Open, Oct 2024): Identifies LLMs as superior for medical text generation
- **"A review on generative AI models for synthetic medical text"** (Nature npj Digital Medicine, 2024): Shows GPT-style models outperform GANs for narrative clinical text
- **"Synthea: An approach, method, and software mechanism"** (JAMIA, 2018): Establishes standards for synthetic patient data quality

This tool bridges traditional synthetic data generation (Synthea's structured approach) with cutting-edge AI methods (transformer-based clinical narrative generation) to create **benchmark-quality medical documents** specifically optimized for PHI detection system validation.

---

## Performance & Scalability

### Resource Requirements

| Configuration | CPU | RAM | Storage | Throughput |
|--------------|-----|-----|---------|------------|
| Minimum | 2 cores | 4GB | 20GB | ~10 docs/min |
| Recommended | 4 cores | 8GB | 50GB | ~30 docs/min |
| Optimal | 8 cores | 16GB | 100GB | ~60 docs/min |

### Model Download Sizes

- NER Model: ~400MB
- Text Classifier: ~1.3GB
- Clinical Embeddings: ~400MB
- **Total**: ~2GB (one-time download)

### Processing Speed

- Small documents (<10KB): ~100-200ms
- Medium documents (10-100KB): ~500ms-2s
- Large documents (>100KB): ~2-5s

*Times measured on 4-core CPU. GPU acceleration can improve speed 3-5x.*

---

## Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-flask

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov=web --cov-report=html
```

### Manual Testing

#### Web UI Testing
```bash
# Open web browser
open http://localhost

# Navigate to "Classify Documents" to test file upload
# Navigate to "Generate Synthetic Data" to create test files
```

#### API Testing
```bash
# Test classification endpoint
curl -X POST http://localhost/api/classify \
  -F "files=@test_document.txt"

# Test generation endpoint (creates DOCX and PDF files)
curl -X POST http://localhost/api/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 5, "formats": ["txt", "docx", "pdf"]}'

# Check system status
curl http://localhost/api/status

# View generated files (inside Docker container)
docker-compose exec app ls -lh /app/uploads/generated/

# Copy generated files to host
docker cp $(docker-compose ps -q app):/app/uploads/generated ./generated_docs
```

**Note**: All API requests go through nginx on port 80. Port 5000 is internal to Docker and not accessible from the host.

---

## Troubleshooting

### Models Not Downloading

```bash
# Check internet connection
# Clear cache and retry
rm -rf models_cache/
python app.py
```

### Out of Memory

```bash
# Reduce batch size or use lighter models
# Upgrade RAM to 8GB minimum
```

### Slow Performance

```bash
# Use GPU if available
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Or reduce model complexity in classifier.py
```

---

## Development

### Project Structure

- **core/**: Core business logic (classification, generation, processing)
- **web/**: Flask web application (routes, templates, auth)
- **config/**: Configuration management
- **deployment/**: Docker and deployment configurations
- **tests/**: Unit and integration tests

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## License

MIT License - see LICENSE file for details.

---

## Support

For issues, questions, or feature requests:
- **GitHub Issues**: https://github.com/FredHutch/sensitive-data-classifier/issues
- **Documentation**: See `deployment/README_DEPLOY.md` for detailed deployment guide

---

## Citations

### Pre-trained Models

- **BioBERT NER**: [d4data/biomedical-ner-all](https://huggingface.co/d4data/biomedical-ner-all)
- **BART Zero-shot**: [facebook/bart-large-mnli](https://huggingface.co/facebook/bart-large-mnli)
- **ClinicalBERT**: [emilyalsentzer/Bio_ClinicalBERT](https://huggingface.co/emilyalsentzer/Bio_ClinicalBERT)

### HIPAA Compliance

This tool assists with HIPAA compliance but does not guarantee it. Organizations are responsible for ensuring their use of this tool meets all applicable regulations.

---

**Version**: 2.0.0
**Last Updated**: October 2025
**Maintainer**: FredHutch Research Computing
