#!/bin/bash

set -e

TEX="sudipta_banik_software_engineer_resume"
PDF_OUT="sudipta_banik_software_engineer_resume.pdf"

# Compile (twice for correct layout/links)
pdflatex -interaction=nonstopmode "$TEX.tex"
pdflatex -interaction=nonstopmode "$TEX.tex"

# Cleanup aux files
rm -f "$TEX.aux" "$TEX.log" "$TEX.out"

# Copy to destinations
mkdir -p ~/Downloads/Resumes
cp "$TEX.pdf" "../$PDF_OUT"
cp "$TEX.pdf" ~/Downloads/Resumes/"$PDF_OUT"

echo "Done. PDF copied to ../ and ~/Downloads/Resumes/"

# Run ATS Validator
if [ -f "validate_ats.py" ]; then
    echo "Running ATS Friendliness Validator..."
    python3 validate_ats.py "$TEX.pdf"
fi