# Contributing to Tome of Heroes

Thanks for helping out! Here's how to get started.

## Workflow

1. Fork the repo and create a branch from `main`:
   ```
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and commit them with a clear message.
3. Open a Pull Request against `main`.
4. At least **1 approving review** is required before merging.
5. All CI checks (flake8, pytest) must pass.

## Local Setup

```bash
pip install -r requirements.txt
pip install flake8 pytest
python server.py
```

## Code Style

- We use **flake8** for linting (max line length: 120).
- Run `flake8 .` before pushing to catch issues early.

## Tests

- Add tests in a `tests/` directory using **pytest**.
- Run `pytest` to execute the test suite.

## Suggesting Features

Open a GitHub Issue using the Feature Request template before starting large changes — helps avoid duplicate work.
