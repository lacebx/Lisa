import os
import mimetypes
import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

def read_file(file_path):
    try:
        mimetype = mimetypes.guess_type(file_path)[0]
        if mimetype is None:
            with open(file_path, 'r') as file:
                file_content = file.read()
        elif mimetype.startswith('text'):
            with open(file_path, 'r') as file:
                file_content = file.read()
        elif mimetype == 'application/pdf':
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
            page_interpreter = PDFPageInterpreter(resource_manager, converter)

            with open(file_path, 'rb') as file:  # Allow lisa to read binary file
                for page in PDFPage.get_pages(file, set()):
                    page_interpreter.process_page(page)

            file_content = fake_file_handle.getvalue()

            # close open handles
            converter.close()
            fake_file_handle.close()
        else:
            file_content = f"Cannot read file of type {mimetype}"
        # Check if the content exceeds the token limit
        if len(file_content) > 4000:  # This is just a heuristic number, adjust as needed
            file_content = file_content[:4000] + "... [Content truncated due to token limit]"
        return file_content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_to_file(file_path, file_content):
    try:
        with open(file_path, 'a') as file:  # 'a' mode for appending to the file instead of overwriting
            file.write('\n' + file_content)  # Start from a new line
        return "File written successfully."
    except IOError:
        return "Failed to write to file."

def create_file(file_path):
    try:
        open(file_path, 'a').close()  # 'a' mode will create the file if it doesn't exist
        return "File created successfully."
    except IOError:
        return "Failed to create file."
