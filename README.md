# PDF Duplex Printer

A web-based tool for preparing PDFs for manual duplex printing using a two-phase printing workflow.

## Workflow

1. **Phase 1**: Print all odd-numbered pages in reverse order (so page 1 ends up on top of the stack)
2. **Phase 2**: Print all even-numbered pages (rotated 180°) in normal order onto the same stack without flipping the paper

This ensures page 2 prints on the back of page 1, page 4 on the back of page 3, etc.

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload a PDF file using the web interface

4. Review the page order information displayed

5. Click "Start Phase 1" to print odd pages (reversed order)

6. After Phase 1 completes, click "Start Phase 2" to print even pages (rotated 180°)

## Features

- **Web-based UI**: Easy-to-use interface for selecting PDFs and viewing page order
- **Page Order Visualization**: See original sequence and how pages will be printed
- **Console Output**: Real-time logging of page number changes and processing steps
- **Two-Phase Printing**: Separate buttons for Phase 1 and Phase 2 printing
- **Printer Selection**: Optional printer name input for systems with multiple printers

## Output Files

The tool generates two PDF files:
- `output/odd_pages.pdf`: Odd pages in reverse order
- `output/even_pages_rotated.pdf`: Even pages rotated 180 degrees

## Command Line Usage

You can also use the PDF processor directly from the command line:

```bash
python pdf_processor.py input.pdf [output_dir]
```

