"""
Flask web application for PDF duplex printing workflow
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from pdf_processor import process_pdf, process_multiple_pdfs, print_pdf
from printer_reverse import reverse_page, manual_reverse_instructions
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload and process it"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        # Save uploaded file
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Get options from form data
        remove_first_last = request.form.get('remove_first_last', 'true').lower() == 'true'
        add_watermarks = request.form.get('add_watermarks', 'true').lower() == 'true'
        
        # Process the PDF
        odd_path, even_path, page_info = process_pdf(filepath, OUTPUT_FOLDER, add_watermarks=add_watermarks, remove_first_last=remove_first_last)
        
        # Convert paths to relative for web access
        page_info['odd_output'] = os.path.relpath(odd_path)
        page_info['even_output'] = os.path.relpath(even_path)
        
        return jsonify({
            'success': True,
            'message': 'PDF processed successfully',
            'page_info': page_info
        })
    
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/print', methods=['POST'])
def print_pdf_endpoint():
    """Handle print requests"""
    try:
        data = request.json
        phase = data.get('phase')  # 'phase1' or 'phase2'
        pdf_path = data.get('pdf_path')
        printer_name = data.get('printer_name')
        
        if not phase or not pdf_path:
            return jsonify({'error': 'Missing phase or pdf_path'}), 400
        
        # Construct full path
        full_path = os.path.join(OUTPUT_FOLDER, os.path.basename(pdf_path))
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'PDF file not found'}), 404
        
        # Print the PDF
        print_pdf(full_path, printer_name)
        
        return jsonify({
            'success': True,
            'message': f'Print job sent for {phase}'
        })
    
    except Exception as e:
        logger.error(f"Error printing PDF: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/reverse', methods=['POST'])
def reverse_page_endpoint():
    """Handle page reverse/retract requests"""
    try:
        data = request.json
        printer_name = data.get('printer_name')
        copies = data.get('copies', 1)
        
        # Attempt to reverse the page
        success = reverse_page(printer_name, copies)
        
        return jsonify({
            'success': success,
            'message': 'Reverse command sent' if success else 'Manual reverse required - see instructions'
        })
    
    except Exception as e:
        logger.error(f"Error reversing page: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/upload-multiple', methods=['POST'])
def upload_multiple_files():
    """Handle multiple PDF file uploads, process them, and merge results"""
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        # Validate and save all PDFs
        saved_paths = []
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({'error': f'File {file.filename} is not a PDF'}), 400
            
            # Save uploaded file
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            saved_paths.append(filepath)
        
        # Get options from form data
        remove_first_last = request.form.get('remove_first_last', 'true').lower() == 'true'
        add_watermarks = request.form.get('add_watermarks', 'true').lower() == 'true'
        
        # Process all PDFs and merge them
        odd_path, even_path, page_info = process_multiple_pdfs(saved_paths, OUTPUT_FOLDER, add_watermarks=add_watermarks, remove_first_last=remove_first_last)
        
        # Convert paths to relative for web access
        page_info['odd_output'] = os.path.relpath(odd_path)
        page_info['even_output'] = os.path.relpath(even_path)
        
        return jsonify({
            'success': True,
            'message': f'{len(saved_paths)} PDF(s) processed and merged successfully',
            'page_info': page_info
        })
    
    except Exception as e:
        logger.error(f"Error processing multiple PDFs: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Download generated PDF files"""
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

