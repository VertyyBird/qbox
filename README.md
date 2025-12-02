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

4. Initialize the database (after creating/activating a virtualenv and installing requirements):
   ```
   FLASK_APP=app.py flask db upgrade
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Open your web browser and go to `http://127.0.0.1:5000/` to see the application in action.

## Running Tests

After installing the dependencies you can run the automated test suite with:

```
pytest
```

The tests use Flask's test client and an in-memory SQLite database, so no additional setup is required.

## Anonymous questions

Logged-in users can toggle **Ask Anonymously** when submitting a question.
The site records who asked the question for moderation but hides the
sender's identity from other users.

## URLs and routes

- User pages live at `/user/<username>`.
- Answers have permalinks at `/user/<username>/a/<public_id>`.
- Account settings are at `/settings`.
- Admins (users with `is_admin=True`) can review reports/flags at `/admin/moderation`.

## Moderation and avatars

- Question submission is rate-limited per IP and can be flagged/hidden by receivers; admins can block users or IPs with optional expiry.
- Answers can be reported and reviewed in the admin panel; reports do not auto-hide answers.
- Avatar URLs must use allowed hosts, valid image extensions, be reachable, and be no larger than 300x300px.

## Template notes

All HTML templates in the `templates` folder extend `base.html`. Because of this, they do not include their own `<!DOCTYPE>` declarations. Running an HTML linter on these individual files may result in warnings about the missing doctype.

To lint the fully rendered pages instead of the raw templates, you can fetch a page from the running development server and pipe it to `tidy`:

```
curl http://127.0.0.1:5000/ | tidy -config .tidyrc
```

## License

This project is licensed under the GNU Affero General Public License v3.0.

You must:
- Provide the full source code if you distribute or host a modified version.
- Attribute the original author [VeryyBird](https://github.com/VertyyBird).
- Distribute derivatives under the same licence.

Full licence: [https://www.gnu.org/licenses/agpl-3.0.html](https://www.gnu.org/licenses/agpl-3.0.html)


When adding new source files, include the AGPLv3 notice at the top of each file.
