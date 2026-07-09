# Contributing to the python-surveyjs project

First off, thank you for taking the time to contribute!\
Contributions are welcome and appreciated — bug reports, feature requests,
documentation improvements, tests and code.

This project is open source and released under the [MIT License](LICENSE).

## Code of Conduct

Please be respectful and constructive in all interactions. We expect everyone
participating in this project to help keep the community welcoming and friendly.

## How to Contribute

### Reporting Bugs

Before opening a new issue, please search the
[existing issues](https://github.com/novacode-nl/python-surveyjs/issues) to
avoid duplicates.

When filing a bug report, include:

- A clear, descriptive title.
- Steps to reproduce the problem.
- What you expected to happen and what actually happened.
- Your Python version and the version of **SurveyJS** you are using; also see
  their [releases page](https://surveyjs.io/stay-updated/release-notes).
- A minimal code sample or SurveyJS JSON that triggers the issue, if possible.

### Suggesting Enhancements

Open an issue describing the enhancement, the use case it addresses, and any
alternatives you have considered.

### Submitting Changes

1. Fork the repository and create your branch from `main`.
2. Set up a development environment (see below).
3. Make your changes, following the project's coding style and conventions.
4. Add or update tests that cover your change.
5. Ensure the full test suite passes.
6. Commit your work with clear, descriptive commit messages.
7. Open a pull request against the `main` branch, describing what your change
   does and why.

Note that we cannot merge your pull request until you have signed a Contributor
License Agreement (see below). It's worth starting that process early, since it
involves an email exchange.

## Contributor License Agreement (CLA)

Before we can accept your contribution, we ask that you sign a Contributor
License Agreement (CLA). This protects both you and the project, and ensures we
have the rights necessary to distribute your contribution under the project's
license.

To request the Agreement, please send an email to
[cla@novaforms.io](mailto:cla@novaforms.io). We will reply with the appropriate
document to sign.

There are two forms of the Agreement:

- **Individual Contributor License Agreement (ICLA).** The ICLA
  (“CLA”) concerns a modified version of the
  [Apache Software Foundation Individual Contributor License Agreement v2.2](https://apache.org/licenses/icla.pdf).
  Sign this if you are contributing as an individual.

- **Corporate Contributor License Agreement (CCLA).** The CCLA
  (“CLA”) concerns a modified version of the
  [Apache Software Foundation Software Grant and Corporate Contributor License Agreement v r190612](https://apache.org/licenses/cla-corporate.pdf).
  Sign this if you are contributing on behalf of an employer or other
  organization.

We are unable to merge contributions until the relevant CLA has been signed.

## Development Setup

Clone the repository and install the project in editable mode. We recommend
using [Poetry](https://python-poetry.org/):

```sh
git clone git@github.com:novacode-nl/python-surveyjs.git
cd python-surveyjs
poetry install
```

Alternatively, with `pip`:

```sh
pip install -e .
```

## Running Tests

From the top-level directory:

```sh
poetry run python -m unittest
```

Please make sure all tests pass, and add new tests for any code you change or
add.

## Coding Guidelines

- Keep changes focused; one logical change per pull request.
- Match the existing code style and naming conventions (linting is not currently
  enforced, but will be added later — we're aiming for consistency across the
  codebase).
- Include the project copyright header on new source files (keep the original
  year or add the current year, e.g. `2026-2027`):

  ```python
  # Copyright 2026 Nova Code (https://www.novaforms.io)
  # See LICENSE file for full licensing details.
  ```

- Update documentation when you change behavior.

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE) that covers this project.

Copyright 2026 Nova Code ([https://www.novaforms.io](https://www.novaforms.io))
