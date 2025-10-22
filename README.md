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
docker-compose -f deployment/docker-compose.yml up -d

# Access the application
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

```bash
POST /api/classify
Content-Type: multipart/form-data
X-API-Key: your-api-key-here (if required)

# Example with curl
curl -X POST http://localhost:5000/api/classify \
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

```bash
POST /api/generate
Content-Type: application/json
X-API-Key: your-api-key-here (if required)

{
  "count": 10,
  "formats": ["txt", "json", "csv"]
}
```

**Response:**
```json
{
  "status": "success",
  "count": 30,
  "documents": [
    {
      "id": "synthetic_medical_record_0001.txt",
      "type": "medical_record",
      "format": "txt",
      "metadata": {...}
    }
  ],
  "timestamp": "2025-10-22T12:34:56"
}
```

#### 3. System Status

```bash
GET /api/status

# No authentication required
curl http://localhost:5000/api/status
```

#### 4. Model Information

```bash
GET /api/models/info

# No authentication required
curl http://localhost:5000/api/models/info
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

```bash
# Test classification
curl -X POST http://localhost:5000/api/classify \
  -F "files=@test_document.txt"

# Test generation
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 5, "formats": ["txt"]}'
```

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
