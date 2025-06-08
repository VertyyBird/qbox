# Contributing to Qbox

Thank you for considering contributing to Qbox!

This document describes how to set up the project for development, run the application, and submit changes.

## Project setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/VertyyBird/qbox.git
   cd qbox
   ```
2. **Create a virtual environment** (optional but recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` file** with a `SECRET_KEY` variable. You can generate a key with:
   ```bash
   python -c 'import secrets; print(secrets.token_hex(16))'
   ```

## Running the app for development

Run the Flask application directly:
```bash
python app.py
```

Or:
```bash
flask run
```

The server starts in development mode at `http://127.0.0.1:5000/`.

## Submitting issues and pull requests

1. [Open an issue](https://github.com/VertyyBird/qbox/issues) for bugs or feature requests. Describe the problem and steps to reproduce.
2. Fork the repository and create a new branch for your feature or fix.
3. Make your changes with clear commit messages.
4. Submit a pull request targeting the `main` branch and reference any related issues.

## Coding style guidelines

- Follow [Pep 8](https://peps.python.org/pep-0008/) for Python code with 4‑space indentation.
- Keep lines under 79 characters when possible.
- Use descriptive variable and function names.
- Format HTML with consistent indentation.

Appreciate your contributions!
