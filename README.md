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

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License

This project is licensed under the MIT License.
