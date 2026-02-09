# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionFile(Question):
    """SurveyJS File Upload question.

    Value is typically a list of file metadata objects or base64 data.
    """

    @property
    def store_data_as_text(self):
        """Whether files are stored as base64 text."""
        return self.raw.get('storeDataAsText', True)

    @property
    def allow_multiple(self):
        return self.raw.get('allowMultiple', False)

    @property
    def max_size(self):
        """Maximum file size in bytes (0 = unlimited)."""
        return self.raw.get('maxSize', 0)

    @property
    def accepted_types(self):
        """Accepted file types (MIME types or extensions)."""
        return self.raw.get('acceptedTypes', '')

    @property
    def allow_camera_access(self):
        return self.raw.get('allowCameraAccess', False)

    @property
    def source_type(self):
        return self.raw.get('sourceType', 'file')

    @property
    def files(self):
        """Get the list of file objects from the value."""
        val = self.value
        if val is None:
            return []
        if isinstance(val, list):
            return val
        return [val]

    @property
    def file_count(self):
        """Number of uploaded files."""
        return len(self.files)
