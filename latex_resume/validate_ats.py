import subprocess
import re
import sys
import os

def check_ats_friendliness(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found.")
        return

    print(f"=== ATS Friendliness Analysis: {pdf_path} ===\n")
    
    # 1. Metadata Check
    print("--- Metadata Check ---")
    try:
        # Check if pdfinfo is available
        try:
            info = subprocess.check_output(['pdfinfo', pdf_path]).decode('utf-8', errors='ignore')
        except FileNotFoundError:
            print("[SKIP] pdfinfo not found. Install poppler-utils.")
            info = ""

        if info:
            has_title = False
            has_author = False
            for line in info.split('\n'):
                if 'Title:' in line and len(line.split(':', 1)[1].strip()) > 0:
                    has_title = True
                    print(f"[OK] {line.strip()}")
                elif 'Author:' in line and len(line.split(':', 1)[1].strip()) > 0:
                    has_author = True
                    print(f"[OK] {line.strip()}")
            
            if not has_title: print("[FAIL] Missing Document Title metadata.")
            if not has_author: print("[FAIL] Missing Author metadata.")
    except Exception as e:
        print(f"[ERROR] Could not run pdfinfo: {e}")

    # 2. Text Extraction & Ligature Check
    print("\n--- Text Integrity & Ligature Check ---")
    try:
        # Get raw text (no layout) to check for word integrity
        raw_text = subprocess.check_output(['pdftotext', '-nopgbrk', pdf_path, '-']).decode('utf-8', errors='ignore')
        
        # Ligatures (Unicode range U+FB00 - U+FB06)
        ligatures = {
            '\uFB00': 'ff',
            '\uFB01': 'fi',
            '\uFB02': 'fl',
            '\uFB03': 'ffi',
            '\uFB04': 'ffl',
            '\uFB05': 'ft',
            '\uFB06': 'st'
        }
        
        found_ligatures = []
        for lig, rep in ligatures.items():
            if lig in raw_text:
                found_ligatures.append(f"'{lig}' ({rep})")
        
        if found_ligatures:
            print(f"[FAIL] Found ligatures: {', '.join(found_ligatures)}")
            print("       ATS systems may fail to parse words like 'fintech' or 'flow'.")
        else:
            print("[OK] No ligatures found.")

        # Check for non-standard characters (potential encoding issues)
        strange_chars = re.findall(r'[^\x00-\x7F\u2022\u2013\u2014\u2019\u00A0]', raw_text)
        if strange_chars:
            unique_strange = set(strange_chars)
            print(f"[WARN] Found non-standard characters: {list(unique_strange)}")
        else:
            print("[OK] Character encoding seems clean.")

    except Exception as e:
        print(f"[ERROR] Could not run pdftotext: {e}")

    # 3. Layout & Reading Order Check
    print("\n--- Layout & Reading Order Check ---")
    try:
        layout_text = subprocess.check_output(['pdftotext', '-layout', pdf_path, '-']).decode('utf-8', errors='ignore')
        
        # Check for overlapping or merged words
        merged_keywords = re.findall(r'[a-z][A-Z]', layout_text)
        if merged_keywords:
             print(f"[WARN] Potential merged words detected (e.g., {merged_keywords[:3]}). Check spacing.")
        else:
             print("[OK] No obvious word merging detected.")

        # Check if standard sections are found
        sections = ["Experience", "Education", "Skills", "Projects"]
        missing_sections = [s for s in sections if s.upper() not in layout_text.upper()]
        if missing_sections:
            print(f"[WARN] Could not clearly identify sections: {missing_sections}")
        else:
            print("[OK] All major resume sections identified.")

    except Exception as e:
        print(f"[ERROR] Could not analyze layout: {e}")

    print("\n=== Analysis Complete ===")

if __name__ == "__main__":
    target_pdf = "sudipta_banik_software_engineer_resume.pdf"
    if len(sys.argv) > 1:
        target_pdf = sys.argv[1]
    
    # Try to find the PDF in the current or parent directory
    if not os.path.exists(target_pdf):
        possible_paths = [
            os.path.join(os.path.dirname(__file__), target_pdf),
            os.path.join(os.getcwd(), target_pdf)
        ]
        for p in possible_paths:
            if os.path.exists(p):
                target_pdf = p
                break

    check_ats_friendliness(target_pdf)
