import os, re
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.utils import get_google_credentials

class GoogleDocsManager:
    def __init__(self):
        self.docs_service = build('docs', 'v1', credentials=get_google_credentials())
        self.drive_service = build('drive', 'v3', credentials=get_google_credentials())

    def add_document(self, content, doc_title, folder_name, make_shareable=False, folder_shareable=False, markdown=False):
        """
        Create a Google Document and save it in the specified folder.
        """
        try:
            # Ensure the folder exists
            folder_id, folder_url = self._get_or_create_folder(folder_name, make_shareable=folder_shareable)
            if not folder_id:
                raise ValueError("Failed to get or create the folder.")

            if markdown:
                # Convert Markdown to Google Doc
                doc_id = self._convert_markdown_to_google_doc(content, doc_title)
            else:
                # Create a new Google Document and add content
                doc = self.docs_service.documents().create(body={"title": doc_title}).execute()
                doc_id = doc.get('documentId')

                # Add content to the document
                requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
                self.docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

            # Move the document to the folder
            self.drive_service.files().update(
                fileId=doc_id,
                addParents=folder_id,
                removeParents="root",
                fields="id, parents"
            ).execute()

            shareable_url = None
            if make_shareable:
                shareable_url = self._make_document_shareable(doc_id)

            document_url = f"https://docs.google.com/document/d/{doc_id}"
            return {
                "document_url": document_url,  
                "shareable_url": shareable_url,
                "folder_url": folder_url
            }
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_document(self, doc_url):
        """
        Retrieve the content of a Google Document by its URL.
        """
        try:
            # Extract the document ID from the URL
            match = re.search(r"/d/([a-zA-Z0-9-_]+)", doc_url)
            if not match:
                raise ValueError("Invalid Google Docs URL format.")
            doc_id = match.group(1)

            # Fetch the document
            document = self.docs_service.documents().get(documentId=doc_id).execute()
            content = ""
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for text_run in element['paragraph'].get('elements', []):
                        content += text_run.get('textRun', {}).get('content', '')

            return content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    def _get_or_create_folder(self, folder_name, make_shareable=False):
        """
        Get the ID and link of an existing folder with the specified name, or create one if it doesn't exist.
        """
        try:
            # Search for the folder
            escaped_name = folder_name.replace("'", "\\'")
            query = f"mimeType='application/vnd.google-apps.folder' and name='{escaped_name}' and trashed=false"
            results = self.drive_service.files().list(q=query, spaces='drive', fields="files(id, name, webViewLink)").execute()
            files = results.get('files', [])
            
            if files:
                # Folder exists
                folder = files[0]
                folder_id = folder['id']
                folder_link = folder.get('webViewLink')
            else:
                # Folder doesn't exist, create it
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
                folder_id = folder['id']
                folder_link = folder.get('webViewLink')

            # Make the folder shareable if required
            if make_shareable:
                self.drive_service.permissions().create(
                    fileId=folder_id,
                    body={"type": "anyone", "role": "reader"},
                    fields="id"
                ).execute()

            return folder_id, folder_link
        except Exception as e:
            print(f"An error occurred while retrieving or creating the folder: {e}")
            return None, None

    def _make_document_shareable(self, doc_id):
        """Make a document shareable with anyone who has the link."""
        try:
            self.drive_service.permissions().create(
                fileId=doc_id,
                body={"type": "anyone", "role": "reader"},
                fields="id"
            ).execute()
            file_info = self.drive_service.files().get(fileId=doc_id, fields="webViewLink").execute()
            return file_info.get("webViewLink")
        except Exception as e:
            print(f"Failed to make document shareable: {e}")
            return None

    def _convert_markdown_to_google_doc(self, markdown_content, title):
        """Convert Markdown content to a Google Document."""
        temp_file_path = "temp_markdown.md"
        try:
            # Save the Markdown content as a temporary file
            with open(temp_file_path, "w") as file:
                file.write(markdown_content)

            # Upload the Markdown file to Google Drive
            file_metadata = {"name": title, "mimeType": "application/vnd.google-apps.document"}
            media = MediaFileUpload(temp_file_path, mimetype="text/markdown")
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            doc_id = file.get("id")

            # Apply professional styling
            self._apply_document_styling(doc_id)

            # Insert logo at the top (if LOGO_URL is configured)
            self._insert_logo(doc_id)

            return doc_id
        except Exception as e:
            print(f"Failed to convert Markdown to Google Doc: {e}")
            return None
        finally:
            # 예외 발생 여부와 관계없이 임시 파일 항상 삭제
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def _insert_logo(self, doc_id):
        """Insert a logo image at the top of the Google Document."""
        logo_url = os.getenv("LOGO_URL")
        if not logo_url:
            return
        try:
            batch_requests = [
                # Create a dedicated first paragraph for the logo
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": "\n"
                    }
                },
                # Insert the logo image into that paragraph
                {
                    "insertInlineImage": {
                        "uri": logo_url,
                        "location": {"index": 1},
                        "objectSize": {
                            "height": {"magnitude": 50, "unit": "PT"},
                            "width": {"magnitude": 150, "unit": "PT"}
                        }
                    }
                },
                # Center-align the logo paragraph
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": 1, "endIndex": 3},
                        "paragraphStyle": {"alignment": "CENTER"},
                        "fields": "alignment"
                    }
                }
            ]
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": batch_requests}
            ).execute()
        except Exception as e:
            print(f"Logo insertion failed (document still saved): {e}")

    def _apply_document_styling(self, doc_id):
        """Apply professional styling to a Google Document after creation."""
        try:
            document = self.docs_service.documents().get(documentId=doc_id).execute()
            content  = document.get('body', {}).get('content', [])
            requests = []

            # Document margins (1 inch all sides)
            requests.append({
                "updateDocumentStyle": {
                    "documentStyle": {
                        "marginTop":    {"magnitude": 72, "unit": "PT"},
                        "marginBottom": {"magnitude": 72, "unit": "PT"},
                        "marginLeft":   {"magnitude": 72, "unit": "PT"},
                        "marginRight":  {"magnitude": 72, "unit": "PT"},
                    },
                    "fields": "marginTop,marginBottom,marginLeft,marginRight"
                }
            })

            for block in content:
                if 'paragraph' not in block:
                    continue

                paragraph  = block['paragraph']
                style_type = paragraph.get('paragraphStyle', {}).get('namedStyleType', '')
                start_idx  = block.get('startIndex', 0)
                end_idx    = block.get('endIndex', 0)
                # end_idx - 1 이 start_idx 이하면 텍스트 없는 빈 단락 → updateTextStyle 적용 불가
                text_end   = end_idx - 1
                has_text   = text_end > start_idx

                if end_idx <= start_idx:
                    continue

                if style_type == 'HEADING_1':
                    if has_text:
                        requests.append({"updateTextStyle": {
                            "range": {"startIndex": start_idx, "endIndex": text_end},
                            "textStyle": {
                                # Brand color: #005BF3 (blue)
                                "foregroundColor": {"color": {"rgbColor": {"red": 0.0, "green": 0.357, "blue": 0.953}}},
                                "fontSize": {"magnitude": 22, "unit": "PT"},
                                "bold": True,
                                "weightedFontFamily": {"fontFamily": "Roboto"}
                            },
                            "fields": "foregroundColor,fontSize,bold,weightedFontFamily"
                        }})
                    requests.append({"updateParagraphStyle": {
                        "range": {"startIndex": start_idx, "endIndex": end_idx},
                        "paragraphStyle": {
                            "spaceAbove": {"magnitude": 18, "unit": "PT"},
                            "spaceBelow": {"magnitude": 8,  "unit": "PT"},
                        },
                        "fields": "spaceAbove,spaceBelow"
                    }})

                elif style_type == 'HEADING_2':
                    if has_text:
                        requests.append({"updateTextStyle": {
                            "range": {"startIndex": start_idx, "endIndex": text_end},
                            "textStyle": {
                                # Brand color: #FF774C (orange)
                                "foregroundColor": {"color": {"rgbColor": {"red": 1.0, "green": 0.467, "blue": 0.298}}},
                                "fontSize": {"magnitude": 16, "unit": "PT"},
                                "bold": True,
                                "weightedFontFamily": {"fontFamily": "Roboto"}
                            },
                            "fields": "foregroundColor,fontSize,bold,weightedFontFamily"
                        }})
                    requests.append({"updateParagraphStyle": {
                        "range": {"startIndex": start_idx, "endIndex": end_idx},
                        "paragraphStyle": {
                            "spaceAbove": {"magnitude": 14, "unit": "PT"},
                            "spaceBelow": {"magnitude": 6,  "unit": "PT"},
                        },
                        "fields": "spaceAbove,spaceBelow"
                    }})

                elif style_type == 'HEADING_3':
                    if has_text:
                        requests.append({"updateTextStyle": {
                            "range": {"startIndex": start_idx, "endIndex": text_end},
                            "textStyle": {
                                # Brand color: #005BF3 muted (lighter blue)
                                "foregroundColor": {"color": {"rgbColor": {"red": 0.0, "green": 0.357, "blue": 0.953}}},
                                "fontSize": {"magnitude": 13, "unit": "PT"},
                                "bold": True,
                                "weightedFontFamily": {"fontFamily": "Roboto"}
                            },
                            "fields": "foregroundColor,fontSize,bold,weightedFontFamily"
                        }})

                elif style_type == 'NORMAL_TEXT':
                    if has_text:
                        requests.append({"updateTextStyle": {
                            "range": {"startIndex": start_idx, "endIndex": text_end},
                            "textStyle": {
                                "foregroundColor": {"color": {"rgbColor": {"red": 0.2, "green": 0.2, "blue": 0.2}}},
                                "fontSize": {"magnitude": 11, "unit": "PT"},
                                "weightedFontFamily": {"fontFamily": "Roboto"}
                            },
                            "fields": "foregroundColor,fontSize,weightedFontFamily"
                        }})
                    requests.append({"updateParagraphStyle": {
                        "range": {"startIndex": start_idx, "endIndex": end_idx},
                        "paragraphStyle": {
                            "lineSpacing": 130,
                            "spaceBelow": {"magnitude": 6, "unit": "PT"},
                        },
                        "fields": "lineSpacing,spaceBelow"
                    }})

            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={"requests": requests}
                ).execute()

        except Exception as e:
            # 스타일 실패해도 문서 자체는 이미 생성됨 — 파이프라인 중단 없음
            print(f"Styling failed (document still saved): {e}")
