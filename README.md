# Personal Finance Management System

Personal Project created by Dominick Ferro

A comprehensive web application designed to help users manage their personal finances. This includes features for budgeting, expense tracking, financial goal setting, and detailed reports. The application is built using Flask for the backend and React for the frontend, providing a robust and interactive user experience.

## Features

- **User Authentication and Profile Management**: Secure login, registration, and profile management.
- **Income and Expense Tracking**: Record and categorize income and expenses.
- **Budget Creation and Management**: Set up budgets and track spending.
- **Financial Goal Setting and Tracking**: Define financial goals and monitor progress.
- **Data Visualization**: Visualize financial data with charts and graphs.
- **Recurring Transactions**: Set up recurring income and expenses.
- **Budget Alerts**: Receive alerts when approaching or exceeding budgets.
- **Export/Import Data**: Export financial data to CSV/Excel and import from these files.
- **Dark Mode**: Switch between light and dark themes.
- **Multi-Language Support**: Use the application in multiple languages.
- **Mobile Responsiveness**: Fully responsive design for mobile devices.
- **Secure Authentication**: Two-factor authentication for enhanced security.
- **Notifications and Reminders**: Email/SMS notifications and reminders.
- **Admin Panel**: Manage users, transactions, and system settings.
- **Audit Logs**: Keep track of user activities for security and accountability.
- **User Roles and Permissions**: Different roles with specific permissions to manage access control.
- **Financial Analytics**: Detailed financial analytics and insights, such as spending trends and forecasting.
- **Multi-Currency Support**: Manage finances in different currencies with real-time currency conversion.
- **User Activity Log**: Track and display user activities within the application.
- **Two-Factor Authentication (2FA)**: Enhance security by requiring a second form of authentication.
- **Advanced Search and Filtering**: Implement advanced search and filtering options for transactions and reports.
- **Expense Receipt Upload**: Upload and store digital copies of expense receipts.
- **Investment Tracking**: Track investments and portfolios, including stocks, bonds, and mutual funds.
- **Backup and Restore**: Backup user data and restore it when needed.

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Frontend**: React
- **Database**: SQLAlchemy (SQLite for development, can be configured for PostgreSQL or MySQL for production)
- **Deployment**: Docker, Heroku

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js and npm
- Docker (optional, for containerized deployment)

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/personal-finance-management-system.git
   cd personal-finance-management-system
   ```

2. **Create a virtual environment and activate it**:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   ```bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

5. **Run the application**:
   ```bash
   flask run
   ```

6. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Running Tests

To run the tests, use the following command:
```bash
python -m unittest discover tests
```

### Docker Setup

To run the application using Docker, follow these steps:

1. **Build the Docker image**:
   ```bash
   docker-compose build
   ```

2. **Run the Docker containers**:
   ```bash
   docker-compose up
   ```

The application should be accessible at `http://localhost:5000`.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a new Pull Request.

### Coding Standards

- Follow PEP 8 for Python code.
- Use meaningful variable and function names.
- Write clear and concise comments.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [React](https://reactjs.org/)
- [Chart.js](https://www.chartjs.org/)
- [Bootstrap](https://getbootstrap.com/)
