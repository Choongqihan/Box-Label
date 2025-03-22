import os
import glob

# Path to your PDFs folder
pdf_folder = "pdfs/"  # Change this if needed

# Find all PDF files in the directory
pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))

# Delete each PDF file
for file in pdf_files:
    try:
        os.remove(file)
        print(f"Deleted: {file}")
    except Exception as e:
        print(f"Error deleting {file}: {e}")

print("PDF cleanup completed.")
