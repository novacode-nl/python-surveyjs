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
6. Add a draft entry under `## Unreleased` in [CHANGELOG.md](CHANGELOG.md) for
   any user-visible change (see [Changelog](#changelog)); maintainers may
   reword or move it. Leave `version` in `pyproject.toml` as it is:
   maintainers choose the version when releasing (see [Releasing](#releasing)).
7. Commit your work with clear, descriptive commit messages.
8. Open a pull request against the `main` branch, describing what your change
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

## Linting

The code is checked with [Ruff](https://docs.astral.sh/ruff/), on every push
too. Its version and rules are in [pyproject.toml](pyproject.toml), and
`poetry install` installs it:

```sh
poetry run ruff check          # report problems
poetry run ruff check --fix    # fix what Ruff can fix itself
```

## Coding Guidelines

- Keep changes focused; one logical change per pull request.
- Match the existing code style and naming conventions, and make sure
  `poetry run ruff check` passes (see [Linting](#linting)).
- Start every Python file with the project copyright header (keep the original
  year or add the current year, e.g. `2026-2027`); Ruff checks it:

  ```python
  # Copyright 2026 Nova Code (https://www.novaforms.io)
  # See LICENSE file for full licensing details.
  ```

- Update documentation when you change behavior.
- Translate every text a respondent reads (titles, labels, choice texts,
  messages, …) through `translate()` on the element or page, so both SurveyJS
  localizable strings and the `i18n` map apply.

## Changelog

[CHANGELOG.md](CHANGELOG.md) follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Contributors add a
draft entry with their pull request; maintainers edit the entries into their
final form, before merging or when releasing.

- Newest version first. Version headings are `## X.Y.Z`, without a date.
- Changes not released yet go under `## Unreleased`, which always stays at the
  top (empty when nothing is pending).
- Group changes under these headings, in this order, and leave out empty ones:
  - `### Breaking Changes` — each entry says what users must change in
    their code.
  - `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`,
    `### Security`.
- A short overview of the release may go above the groups.
- Write plainly and briefly: what changed, and what it was before when that
  helps. Show a short code example when a change is easier to show than to
  describe.

## Releasing

Releases are published to PyPI by the
[publish workflow](.github/workflows/publish.yml), using
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/).

Each file on PyPI comes with a provenance attestation that links it to the
commit that built it. There is no manual upload and no API token.

To release (maintainers only):

1. Bump `version` in [pyproject.toml](pyproject.toml):
   - a patch version (`0.9.1`) for fixes, or for changes that leave the code
     as it is;
   - a minor version (`0.10.0`) for new features. Before 1.0.0, breaking
     changes also go in a minor version; from 1.0.0 on, they need a major
     version (`2.0.0`).
2. In [CHANGELOG.md](CHANGELOG.md), rename `## Unreleased` to `## X.Y.Z` and
   add a new, empty `## Unreleased` above it.
3. Push to `main`, or merge the pull request with the version bump.
4. Approve the `Upload to PyPI` job in the workflow run.

The workflow only releases when the version is not on PyPI yet, and tags the
commit `vX.Y.Z` after the upload. If a job fails, use *Re-run failed jobs*;
PyPI does not accept a version that was uploaded before, so a broken release
gets a new version instead.

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE) that covers this project.

Copyright 2026 Nova Code ([https://www.novaforms.io](https://www.novaforms.io))
