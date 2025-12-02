# Project Summary: Qbox

Qbox is a Flask-based web application designed for a Q&A platform where users can interact through questions and answers. The application will allow users to create accounts, receive questions on their personal page, and publish answers publicly.

Potential Domains: qbox.lol or qbox.social

## Key Features

### 1. User Accounts
- [x] Sign-up, login, and logout functionality. 
- [x] Password hashing for secure authentication. 
- [x] Unique user pages (e.g., `/user/username`). 
- [x] Admin flag on users for moderation access.

### 2. Question Submission
- [x] Allow visitors (anonymous or registered users) to submit questions to a specific user's page. 
- [x] Store questions in a database with sender information (if applicable) and timestamps. 
- [x] Questions can be flagged/hidden and rate-limited by IP.

### 3. Answer Management
- [x] Provide users with a dashboard to review submitted questions. 
- [x] Allow users to write and publish answers to their public page. 

### 4. Database Design
- Tables for:
  - **Users**: ID, username, email, hashed password, created_at, **is_admin** flag.
  - **Questions**: ID, sender ID (nullable for guests), receiver ID, question text,
    **is_anonymous**, **is_hidden**, **is_flagged**, created_at, ip_address.
  - **Answers**: ID, question ID, answer text, created_at, public_id.
  - **AnswerReports**: ID, answer ID, reporter (nullable), reporter_ip, reason, resolved flag, created_at.
  - **Blocks**: ID, user_id (nullable), ip_address (nullable), reason, expires_at, active flag, created_at.

### 5. Basic UI
- Simple, responsive HTML templates using Jinja2.
- Separate pages for:
  - Homepage
  - Public feed (with new users column and answer permalinks)
  - User profile (`/user/<username>`)
  - Login/Sign-up
  - Dashboard for managing unanswered questions
  - Settings page for account updates
  - Admin moderation panel (flags/reports/blocks) for admins

### 6. Stretch Goals
- [ ] Notifications for new questions.
- [x] Anonymous question submission toggle.
- [ ] Page themes/customization for user profiles.

## Technical Stack
- **Backend**: Python with Flask.
- **Database**: SQLite for development, scalable to PostgreSQL or MySQL in production.
- **Frontend**: Jinja2 templates (extendable with React or Vue.js).
- **Hosting**: Vultr server (with Nginx for production deployment).

## Development Notes
- Start with basic authentication and database setup.
- Build out routes for question submission and answer publishing.
- Gradually add features and refine the UI.
