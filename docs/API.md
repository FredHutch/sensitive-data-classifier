PHI Classifier & Synthetic Data Generator API

Endpoints
- GET /           Render index page
- GET /classify   Render classification UI
- GET /generate   Render synthetic data UI
- POST /api/classify
  - multipart/form-data with files[]
  - Response: { status, results: [ { filename, contains_phi, confidence, risk_level, total_identifiers, phi_elements? } ] }
- POST /api/generate
  - JSON body: { count: int, formats: [ "txt" | "docx" | "pdf" | "csv" ] }
  - Response: { status, count, documents: [ { id, type, format, metadata } ] }

Notes
- Classification is performed by core classifier + HIPAA identifier detector.
- Text extraction is handled by core document processor.
- Synthetic generation is provided by core generator.
