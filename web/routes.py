"""
Flask Routes Module

Web interface and REST API endpoints for PHI classification system.
"""

import json
import logging
from datetime import datetime

from flask import render_template, request, jsonify, current_app
from . import web_bp

logger = logging.getLogger(__name__)

@web_bp.route("/")
def index():
    """Main landing page with system overview."""
    return render_template("index.html")

@web_bp.route("/classify")
def classify_page():
    """Document classification interface."""
    return render_template("classify.html")

@web_bp.route("/generate")
def generate_page():
    """Synthetic data generation interface."""
    return render_template("generate.html")

@web_bp.route("/api/classify", methods=["POST"])
def api_classify():
    """REST API endpoint for document classification."""
    files = request.files.getlist("files")
    if not files:
        return jsonify({"status": "error", "message": "No files uploaded"}), 400
    
    # Get services from app config
    services = current_app.config.get("APP_SERVICES", {})
    processor = services.get("processor")
    classifier = services.get("classifier")
    
    if not processor:
        return jsonify({"status":"error","message":"Processor unavailable"}), 503
    
    results = []
    for file in files:
        try:
            # Process document to extract text
            doc_result = processor.process_document(file, file.filename)
            text = doc_result.get("text", "") if doc_result.get("success") else ""
            
            # Classify for PHI
            classification = {"contains_phi": False, "confidence": 0.0, "risk_level": "NONE", "total_phi_identifiers": 0}
            if classifier and text:
                classification = classifier.classify_document(text)
            
            results.append({
                "filename": doc_result.get("filename", file.filename),
                "contains_phi": bool(classification.get("contains_phi", False)),
                "confidence": float(classification.get("confidence", 0.0)),
                "risk_level": classification.get("risk_level", "NONE"),
                "total_identifiers": int(classification.get("total_phi_identifiers", 0)),
                "file_size": doc_result.get("file_size", 0),
                "word_count": doc_result.get("word_count", 0)
            })
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "error": str(e),
                "contains_phi": False,
                "confidence": 0.0,
                "risk_level": "ERROR"
            })
    
    return jsonify({
        "status": "success",
        "results": results,
        "total_files": len(files),
        "successful_classifications": len([r for r in results if "error" not in r]),
        "timestamp": datetime.now().isoformat()
    })

@web_bp.route("/api/generate", methods=["POST"])
def api_generate():
    """REST API endpoint for synthetic data generation."""
    data = request.get_json(silent=True) or {}
    count = int(data.get("count", 10))
    formats = data.get("formats", ["txt"])
    
    # Get generator service
    services = current_app.config.get("APP_SERVICES", {})
    generator = services.get("generator")
    
    if not generator:
        return jsonify({"status":"error","message":"Generator unavailable"}), 503
    
    try:
        docs = generator.generate_synthetic_documents(count=count, formats=formats)
        return jsonify({
            "status": "success",
            "count": len(docs),
            "documents": [
                {
                    "id": doc.get("id"),
                    "type": doc.get("type"),
                    "format": doc.get("format"),
                    "metadata": doc.get("metadata", {})
                }
                for doc in docs
            ],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"status":"error","message":str(e)}), 500

@web_bp.route("/api/status")
def api_status():
    """REST API endpoint for system status."""
    services = current_app.config.get("APP_SERVICES", {})
    
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "status": "operational",
        "version": "1.0.0",
        "services": {
            "classifier": {"available": "classifier" in services},
            "processor": {"available": "processor" in services},
            "generator": {"available": "generator" in services}
        }
    })

@web_bp.route("/health")
def health_check():
    """Health check endpoint for load balancers."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })