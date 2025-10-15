import os
import threading
from flask import Flask, render_template, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Collect form data
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        size = request.form.get("size")
        layers = request.form.get("layers")
        flavor = request.form.get("flavor")
        filling = request.form.get("filling")
        color = request.form.get("color")
        cupcakes = request.form.get("cupcakes")
        pickup_date = request.form.get("pickup_date")
        notes = request.form.get("notes")

        # Collect uploaded files (multiple)
        files = request.files.getlist("image")  # now supports multiple files

        # Build email content
        message = f"""
        New Order from {name}:
        Email = {email}
        Phone number = {phone}
        
        Cake size = {size}
        
        Number of layers = {layers}
        
        Cake flavor = {flavor}
        
        Filling = {filling}
        
        Cake color = {color}
        
        Number of Cupcakes = {cupcakes}

        Notes = {notes}
        Pickup Date: {pickup_date}
        """

        # Send email asynchronously
        threading.Thread(target=send_email, args=(message, files)).start()

        # Immediately show thank-you page
        return render_template("thankyou.html")

    # Default GET request
    return render_template("home.html")


def send_email(message, files=None):
    EMAIL_USER = os.environ.get("EMAIL_USER")
    EMAIL_PASS = os.environ.get("EMAIL_PASS")

    if not EMAIL_USER or not EMAIL_PASS:
        print("Error: EMAIL_USER or EMAIL_PASS not set.")
        return

    from_email = EMAIL_USER
    to_email = EMAIL_USER  # you’ll receive the orders

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = "New Cake Order"
    msg.attach(MIMEText(message, "plain"))

    # Handle multiple files
    if files:
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        for file in files:
            if file and file.filename:
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(filepath)
                with open(filepath, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={file.filename}")
                    msg.attach(part)

    try:
        # Send via Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully with attachments.")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    app.run(debug=True)