# Project Summary: Qbox

Qbox is a Flask-based web application designed for a Q&A platform where users can interact through questions and answers. The application will allow users to create accounts, receive questions on their personal page, and publish answers publicly.

Potential Domains: qbox.lol or qbox.social

## Key Features

### 1. User Accounts
- Sign-up, login, and logout functionality.
- Password hashing for secure authentication.
- Unique user pages (e.g., `/users/username`).

### 2. Question Submission
- Allow visitors (anonymous or registered users) to submit questions to a specific user's page.
- Store questions in a database with sender information (if applicable) and timestamps.

### 3. Answer Management
- Provide users with a dashboard to review submitted questions.
- Allow users to write and publish answers to their public page.

### 4. Database Design
- Tables for:
  - **Users**: ID, username, email, hashed password, created_at.
  - **Questions**: ID, sender ID (nullable for anonymous), receiver ID, question text, created_at.
  - **Answers**: ID, question ID, answer text, created_at.

### 5. Basic UI
- Simple, responsive HTML templates using Jinja2.
- Separate pages for:
  - Homepage
  - User profile (Q&A display)
  - Login/Sign-up
  - Dashboard for managing questions and answers.

### 6. Stretch Goals
- Notifications for new questions.
- Anonymous question submission toggle.
- Page themes/customization for user profiles.

## Technical Stack
- **Backend**: Python with Flask.
- **Database**: SQLite for development, scalable to PostgreSQL or MySQL in production.
- **Frontend**: Jinja2 templates (extendable with React or Vue.js).
- **Hosting**: Vultr server (with Nginx for production deployment).

## Development Notes
- Start with basic authentication and database setup.
- Build out routes for question submission and answer publishing.
- Gradually add features and refine the UI.
