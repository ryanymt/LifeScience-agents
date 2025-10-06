# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tool for extracting text from a PDF document at a given URL."""

import io
import PyPDF2
import requests


def extract_pdf_text_from_url(pdf_url: str) -> str:
    """
    Downloads a PDF from a URL and extracts its text content.

    Args:
        pdf_url: The direct URL to a PDF file.

    Returns:
        The extracted text of the PDF, or an error message if it fails.
    """
    if not pdf_url.endswith(".pdf"):
        return "Error: URL does not appear to point to a PDF file."

    try:
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        pdf_file = io.BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        full_text = "".join(page.extract_text() for page in reader.pages)

        if not full_text.strip():
            return (
                "Successfully downloaded the PDF, but could not extract text. "
                "The PDF may be image-based or corrupted."
            )
        # --- CHANGE ---
        # Return ONLY the raw text for clean input into the next tool.
        return full_text

    except Exception as e:
        return f"Failed to download or parse the PDF from {pdf_url}. Error: {e}"