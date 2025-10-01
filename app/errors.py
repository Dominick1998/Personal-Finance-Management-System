# app/errors.py
# includes error codes such as 404(Not Found) and 500(Internal server error).

from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    """
    Custom handler for 404 (Not Found) errors.
    Renders a custom 404 error page.
    """
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Custom handler for 500 (Internal Server Error) errors.
    Rolls back the database session to prevent invalid states
    and renders a custom 500 error page.
    """
    db.session.rollback()
    return render_template('500.html'), 500

#error 