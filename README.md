# Qbox Project

Qbox is my attempt at making a Q&A site like CuriousCat. I'm tired of the new Q&A sites that require you to install an app. This will just be a website, no app installation required.

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/VertyyBird/qbox.git
   cd qbox
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Generate a secret key for your `.env` file:
   ```
   python -c 'import secrets; print(secrets.token_hex(16))'
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your web browser and go to `http://127.0.0.1:5000/` to see the application in action.
