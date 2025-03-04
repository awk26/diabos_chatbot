from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

def send_email(emailAddress,message,name,phone):
    """Sends an email with the provided name and content."""

    sender_email = "awdeshnonia@gmail.com"  # Replace with your email
    sender_password = "uftp xfin fixl xnvx"  # Replace with your password or app password
    receiver_email = "avdeshk@jmbaxi.com" # Replace with recipient email

    message = MIMEText(f"Hello {name},\n\n{phone},\n\n{emailAddress},\n\n{message}")
    message["Subject"] = "Email from Flask API"
    message["From"] = sender_email
    message["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

@app.route('/send_email', methods=['POST'])
def api_send_email():
    """API endpoint to send an email."""
    try:
        data = request.get_json()
        # if not data or 'name' not in data or 'content' not in data:
        #     return jsonify({"error": "Missing name or content in request body"}), 400

        emailAddress=data['emailAddress'],
        message= data['message'],
        name= data['name'],
        phone=data['phone']

        print(emailAddress,message,name,phone)
       
        success, message = send_email(emailAddress,message,name,phone)

        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # app.run(debug=True) #remove debug=True in production
    app.run(host="0.0.0.0",port=5000)