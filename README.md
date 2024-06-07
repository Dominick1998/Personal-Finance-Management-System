# Personal Finance Management System

A web application that helps users manage their personal finances, including budgeting, expense tracking, and financial goal setting. Built with Flask and React.

## Features

- User authentication and profile management
- Income and expense tracking
- Budget creation and management
- Financial goal setting and tracking
- Data visualization for financial insights

## Tech Stack

- Backend: Flask
- Frontend: React
- Database: SQLAlchemy (for SQL databases)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Dominick1998/Personal-Finance-Management-System.git
   cd Personal-Finance-Management-System
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

5. Run the application:
   ```bash
   flask run
   ```

# Contributing to Personal Finance Management System

Thank you for considering contributing to our project! Here are some guidelines to help you get started.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request, please create an issue in our GitHub repository. Include as much detail as possible to help us understand and address the issue.

### Submitting Pull Requests

1. Fork the repository and create your branch from `main`.
2. Ensure your code follows our coding standards.
3. Include tests for your changes.
4. Ensure all tests pass.
5. Submit a pull request and provide a detailed description of your changes.

### Coding Standards

- Follow PEP 8 for Python code.
- Use meaningful variable and function names.
- Write clear and concise comments.

## License

This project is licensed under the MIT License.
