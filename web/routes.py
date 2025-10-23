"""
Flask Routes Module

Web interface and REST API endpoints for PHI classification system.
"""

import json
import logging
import zipfile
import io
from datetime import datetime
from pathlib import Path

from flask import render_template, request, jsonify, current_app, send_file, send_from_directory
from . import web_bp
from .auth import require_api_key

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
@require_api_key
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
@require_api_key
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
        # Generate documents
        docs = generator.generate_synthetic_documents(count=count, formats=formats)

        # Save documents to disk if requested
        save_to_disk = data.get("save_to_disk", True)  # Default to True for user convenience
        output_dir = current_app.config.get("UPLOAD_FOLDER")
        saved_files = []

        if save_to_disk:
            from pathlib import Path
            output_path = Path(output_dir) / "generated"
            output_path.mkdir(parents=True, exist_ok=True)

            for doc in docs:
                filename = doc.get("filename", f"synthetic_{doc.get('document_id')}.txt")
                file_path = output_path / filename

                # Write content to file (handle both text and binary formats)
                content = doc.get("content", "")

                # Check if content is binary (bytes) or text (str)
                if isinstance(content, bytes):
                    # Binary format (PDF, DOCX)
                    with open(file_path, 'wb') as f:
                        f.write(content)
                else:
                    # Text format (TXT, JSON, CSV, XML)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                saved_files.append({
                    "filename": filename,
                    "path": str(file_path),
                    "size_bytes": doc.get("file_size_bytes", 0),
                    "download_url": f"/downloads/{filename}"
                })
                logger.info(f"Saved generated document to {file_path}")

        return jsonify({
            "status": "success",
            "count": len(docs),
            "saved_to_disk": save_to_disk,
            "output_directory": str(output_path) if save_to_disk else None,
            "saved_files": saved_files if save_to_disk else [],
            "download_all_url": "/api/downloads/zip" if save_to_disk and saved_files else None,
            "list_files_url": "/api/downloads/list",
            "documents": [
                {
                    "id": doc.get("document_id"),
                    "type": doc.get("document_type"),
                    "format": doc.get("format"),
                    "filename": doc.get("filename"),
                    "contains_phi": doc.get("contains_phi", True),
                    "phi_density": doc.get("phi_density", 0),
                    "file_size_bytes": doc.get("file_size_bytes", 0),
                    "medical_complexity": doc.get("medical_complexity", "unknown"),
                    "created_date": doc.get("created_date"),
                    "download_url": f"/downloads/{doc.get('filename')}" if save_to_disk else None
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

@web_bp.route("/api/downloads/list")
def list_downloads():
    """List all generated files available for download."""
    output_dir = current_app.config.get("UPLOAD_FOLDER")
    generated_path = Path(output_dir) / "generated"

    if not generated_path.exists():
        return jsonify({
            "status": "success",
            "files": [],
            "count": 0,
            "message": "No files generated yet"
        })

    files = []
    for file_path in generated_path.iterdir():
        if file_path.is_file():
            files.append({
                "filename": file_path.name,
                "size_bytes": file_path.stat().st_size,
                "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                "download_url": f"/downloads/{file_path.name}"
            })

    # Sort by creation time, newest first
    files.sort(key=lambda x: x['created'], reverse=True)

    return jsonify({
        "status": "success",
        "files": files,
        "count": len(files),
        "timestamp": datetime.now().isoformat()
    })

@web_bp.route("/api/downloads/<filename>")
def download_file(filename):
    """Download a specific generated file."""
    output_dir = current_app.config.get("UPLOAD_FOLDER")
    generated_path = Path(output_dir) / "generated"

    # Security: prevent directory traversal
    safe_filename = Path(filename).name
    file_path = generated_path / safe_filename

    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(generated_path, safe_filename, as_attachment=True)

@web_bp.route("/api/downloads/zip")
def download_all_zip():
    """Download all generated files as a ZIP archive."""
    output_dir = current_app.config.get("UPLOAD_FOLDER")
    generated_path = Path(output_dir) / "generated"

    if not generated_path.exists() or not any(generated_path.iterdir()):
        return jsonify({"error": "No files available for download"}), 404

    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in generated_path.iterdir():
            if file_path.is_file():
                zip_file.write(file_path, arcname=file_path.name)

    zip_buffer.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"synthetic_health_data_{timestamp}.zip"

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=zip_filename
    )