# UMLS Integration Setup

- Obtain a UMLS API key from NLM.
- Set environment variable: export UMLS_API_KEY="your-key"
- The app uses UMLS vocabulary integration (fallback patterns if key missing).
- For production, cache concept lookups and rate-limit API calls.
