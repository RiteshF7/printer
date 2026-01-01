"""
PDF Processor for Duplex Printing Workflow

This script handles:
1. Splitting odd and even pages from an input PDF
2. Reversing odd pages (so page 1 ends up on top when printed)
3. Rotating even pages by 180 degrees
4. Generating output PDFs ready for duplex printing
"""

from pypdf import PdfReader, PdfWriter
import sys
import os


def process_pdf(input_path, output_dir="."):
    """
    Process PDF for duplex printing workflow.
    
    Args:
        input_path: Path to input PDF file
        output_dir: Directory to save output PDFs (default: current directory)
    
    Returns:
        tuple: (odd_pages_path, even_pages_path, page_info)
    """
    print(f"\n{'='*60}")
    print(f"Processing PDF: {input_path}")
    print(f"{'='*60}\n")
    
    # Read the input PDF
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    print(f"Total pages in input PDF: {total_pages}\n")
    
    # Initialize writers for odd and even pages
    odd_writer = PdfWriter()
    even_writer = PdfWriter()
    
    # Track page order information
    odd_pages_order = []
    even_pages_order = []
    
    # Split pages into odd and even
    print("Step 1: Splitting pages into odd and even...")
    for i in range(total_pages):
        page_num = i + 1  # 1-indexed page number
        page = reader.pages[i]
        
        if page_num % 2 == 1:  # Odd page
            odd_pages_order.append(page_num)
        else:  # Even page
            even_pages_order.append(page_num)
    
    print(f"  - Odd pages found: {odd_pages_order}")
    print(f"  - Even pages found: {even_pages_order}\n")
    
    # Step 2: Add odd pages in REVERSE order (so page 1 ends up on top)
    print("Step 2: Adding odd pages in REVERSE order...")
    for i in range(len(odd_pages_order) - 1, -1, -1):
        page_index = odd_pages_order[i] - 1  # Convert to 0-indexed
        odd_writer.add_page(reader.pages[page_index])
        print(f"  - Added page {odd_pages_order[i]} (position {len(odd_pages_order) - i} in output)")
    
    print(f"\n  Final odd pages order: {list(reversed(odd_pages_order))}\n")
    
    # Step 3: Add even pages in NORMAL order, rotated 180 degrees
    print("Step 3: Adding even pages in NORMAL order, rotated 180°...")
    for page_num in even_pages_order:
        page_index = page_num - 1  # Convert to 0-indexed
        page = reader.pages[page_index]
        # Rotate page by 180 degrees
        page.rotate(180)
        even_writer.add_page(page)
        print(f"  - Added page {page_num} (rotated 180°)")
    
    print(f"\n  Final even pages order: {even_pages_order}\n")
    
    # Save output PDFs
    odd_output_path = os.path.join(output_dir, "odd_pages.pdf")
    even_output_path = os.path.join(output_dir, "even_pages_rotated.pdf")
    
    print("Step 4: Saving output PDFs...")
    with open(odd_output_path, 'wb') as f:
        odd_writer.write(f)
    print(f"  - Saved: {odd_output_path}")
    
    with open(even_output_path, 'wb') as f:
        even_writer.write(f)
    print(f"  - Saved: {even_output_path}\n")
    
    # Create page info dictionary
    page_info = {
        'total_pages': total_pages,
        'original_sequence': list(range(1, total_pages + 1)),
        'odd_pages_original': odd_pages_order,
        'odd_pages_final': list(reversed(odd_pages_order)),
        'even_pages_original': even_pages_order,
        'even_pages_final': even_pages_order,
        'odd_output': odd_output_path,
        'even_output': even_output_path
    }
    
    print(f"{'='*60}")
    print("Processing complete!")
    print(f"{'='*60}\n")
    
    return odd_output_path, even_output_path, page_info


def print_pdf(pdf_path, printer_name=None):
    """
    Print a PDF file using system print command.
    
    Args:
        pdf_path: Path to PDF file to print
        printer_name: Optional printer name (if None, uses default printer)
    """
    import subprocess
    import platform
    
    print(f"\nPrinting: {pdf_path}")
    
    system = platform.system()
    
    if system == "Linux":
        if printer_name:
            cmd = ["lp", "-d", printer_name, pdf_path]
        else:
            cmd = ["lp", pdf_path]
    elif system == "Darwin":  # macOS
        if printer_name:
            cmd = ["lpr", "-P", printer_name, pdf_path]
        else:
            cmd = ["lpr", pdf_path]
    elif system == "Windows":
        # Windows printing using PowerShell or default print verb
        try:
            import subprocess
            if printer_name:
                # Use PowerShell to print with specific printer
                ps_cmd = f'Start-Process -FilePath "{pdf_path}" -Verb Print -ArgumentList "/d:{printer_name}"'
                cmd = ["powershell", "-Command", ps_cmd]
            else:
                # Use default print action
                import os
                os.startfile(pdf_path, "print")
                print(f"Print job sent to default printer!")
                return
        except Exception as e:
            print(f"Error with Windows printing: {e}")
            print("Trying alternative method...")
            # Fallback: try using the print command
            if printer_name:
                cmd = ["print", "/D:", printer_name, pdf_path]
            else:
                cmd = ["print", pdf_path]
    else:
        print(f"Unsupported operating system: {system}")
        return
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Print job sent successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error printing: {e}")
    except FileNotFoundError:
        print("Print command not found. Please install printing utilities.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_processor.py <input_pdf> [output_dir]")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    if not os.path.exists(input_pdf):
        print(f"Error: File not found: {input_pdf}")
        sys.exit(1)
    
    process_pdf(input_pdf, output_dir)

