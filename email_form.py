from os import getenv

from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# HTML templates for responses
SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Message Sent</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
        .success { color: green; }
        .back-link { margin-top: 20px; }
    </style>
</head>
<body>
    <h1 class="success">Message Sent Successfully!</h1>
    <p>Thank you for your message. I'll get back to you soon.</p>
    <p class="back-link"><a href="/">Back to Home</a></p>
</body>
</html>
"""

ERROR_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
        .error { color: red; }
        .back-link { margin-top: 20px; }
    </style>
</head>
<body>
    <h1 class="error">Error Sending Message</h1>
    <p>Sorry, there was a problem sending your message. Please try again later.</p>
    <p>Error: {{ error_message }}</p>
    <p class="back-link"><a href="/">Back to Home</a></p>
</body>
</html>
"""


@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Validate required fields
        if not all([name, email, subject, message]):
            raise ValueError("All fields are required")

        # Mailgun configuration
        MAILGUN_API_KEY = getenv('MAILGUN_API_KEY')
        MAILGUN_DOMAIN = getenv('MAILGUN_DOMAIN')
        RECIPIENT_EMAIL = getenv('RECIPIENT_EMAIL')

        if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN, RECIPIENT_EMAIL]):
            raise ValueError("Missing required environment variables")

        # Prepare email content
        email_content = f"""
        New Contact Form Submission

        From: {name} <{email}>
        Subject: {subject}

        Message:
        {message}
        """

        # Send email using Mailgun API
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"{name} <noreply@{MAILGUN_DOMAIN}>",
                "to": RECIPIENT_EMAIL,
                "subject": f"Contact Form: {subject}",
                "text": email_content
            }
        )

        response.raise_for_status()
        return render_template_string(SUCCESS_PAGE)

    except Exception as e:
        app.logger.error(f"Error sending email: {str(e)}")
        return render_template_string(ERROR_PAGE, error_message=str(e)), 500


if __name__ == '__main__':

    app.run(debug=True)
