# Copyright 2026 Nova Code (https://www.novacode.nl)
"""
SurveyJS Python Package

This module serves as the entry point for the surveyjs package, providing
access to the core components for working with SurveyJS forms and the
survey creator.

It imports and exposes the following classes:
    - SurveyForm: Handles the rendering and processing of SurveyJS forms.
    - SurveyCreator: Provides functionality for creating and managing surveys.

Copyright 2026 Nova Code (https://www.novacode.nl)
See LICENSE file for full licensing details.
"""
# See LICENSE file for full licensing details.

from surveyjs.creator import SurveyCreator
from surveyjs.form import SurveyForm

__all__ = ['SurveyCreator', 'SurveyForm']
