from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey123'  # required for sessions
CORS(app)


# Paths and database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

db = SQLAlchemy(app)

# ---------- MODELS ----------
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    subject = db.Column(db.String(150))
    message = db.Column(db.Text)
    date = db.Column(db.String(50))
    status = db.Column(db.String(10))

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    method = db.Column(db.String(50))
    ref = db.Column(db.String(100))
    notes = db.Column(db.Text)
    date = db.Column(db.String(50))

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    profession = db.Column(db.String(100))
    message = db.Column(db.Text)
    image_path = db.Column(db.String(255))

class SiteContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mission = db.Column(db.Text)
    about = db.Column(db.Text)
    address = db.Column(db.String(255))
    hours = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    facebook = db.Column(db.String(255))
    donate_link = db.Column(db.String(255))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    upload_date = db.Column(db.String(50))
    
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    date = db.Column(db.String(50))

# Create DB if not exists
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()


# ---------- FRONTEND ROUTES ----------
@app.route('/')
def index():
    content = SiteContent.query.first()
    testimonials = Testimonial.query.order_by(Testimonial.id.desc()).all()
    news_items = News.query.order_by(News.id.desc()).all()

    if not content:
        content = SiteContent(
            mission="Our mission is to serve the community with compassion.",
            about="The Braintree Community Food Pantry provides food assistance to local families in need.",
            address="14 Storrs Ave Braintree, MA",
            hours="Saturday 10:00–12:00; Wednesday 4:00–6:00",
            email="braintreefoodpantrydirector@gmail.com",
            phone="781-277-1609",
            facebook="https://www.facebook.com/BraintreeFoodPantry",
            donate_link="#donate_info"
        )
        db.session.add(content)
        db.session.commit()

    return render_template(
        'index.html',
        content=content,
        testimonials=testimonials,
        news_items=news_items
    )



@app.route('/gallery')
def gallery():
    images = GalleryImage.query.order_by(GalleryImage.id.desc()).all()
    return render_template('gallery.html', images=images)



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('admin.html')


@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')



from flask import redirect, url_for, session

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/api/donations', methods=['POST', 'DELETE'])
def modify_donations():
    if request.method == 'POST':
        payload = request.get_json(force=True)
        d = Donation(
            name=payload.get('name',''),
            amount=float(payload.get('amount',0)),
            method=payload.get('method',''),
            ref=payload.get('ref',''),
            notes=payload.get('notes',''),
            date=payload.get('date','')
        )
        db.session.add(d); db.session.commit()
        return jsonify({'message':'Donation added','id':d.id}), 201

    if request.method == 'DELETE':
        did = request.args.get('id')
        d = Donation.query.get(did)
        if not d: return jsonify({'error':'Not found'}), 404
        db.session.delete(d); db.session.commit()
        return jsonify({'message':'Donation deleted'})


@app.route('/api/gallery', methods=['GET', 'POST', 'DELETE'])
def api_gallery():
    # GET – return all images
    if request.method == 'GET':
        images = [
            {
                "id": g.id,
                "filename": g.filename,
                "url": url_for('static', filename='uploads/' + g.filename)
            }
            for g in GalleryImage.query.order_by(GalleryImage.id.desc()).all()
        ]
        return jsonify(images)

    # POST – upload image
    if request.method == 'POST':
        file = request.files.get('image')
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        filename = file.filename
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        new_img = GalleryImage(
            filename=filename,
            upload_date=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        db.session.add(new_img)
        db.session.commit()

        return jsonify({"message": "Image uploaded", "id": new_img.id}), 201

    # DELETE – remove an image
    if request.method == 'DELETE':
        img_id = request.args.get("id")
        img = GalleryImage.query.get(img_id)

        if not img:
            return jsonify({"error": "Image not found"}), 404

        # Remove file from filesystem
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], img.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(img)
        db.session.commit()

        return jsonify({"message": "Image deleted"})



# ---------- API ROUTES ----------
@app.route('/api/site-content', methods=['GET', 'POST'])
def site_content():
    if request.method == 'GET':
        content = SiteContent.query.first()
        if not content:
            content = SiteContent(
                mission="Our mission is to serve the community with compassion.",
                about="The Braintree Community Food Pantry provides food assistance to local families in need.",
                address="14 Storrs Ave Braintree, MA",
                hours="Saturday 10:00–12:00; Wednesday 4:00–6:00",
                email="braintreefoodpantrydirector@gmail.com",
                phone="781-277-1609",
                facebook="https://www.facebook.com/BraintreeFoodPantry",
                donate_link="#donate_info"
            )
            db.session.add(content)
            db.session.commit()
        return jsonify({
            'mission': content.mission,
            'about': content.about,
            'address': content.address,
            'hours': content.hours,
            'email': content.email,
            'phone': content.phone,
            'facebook': content.facebook,
            'donate_link': content.donate_link
        })

    if request.method == 'POST':
        data = request.get_json()
        content = SiteContent.query.first()
        if not content:
            content = SiteContent()
            db.session.add(content)
        content.mission = data.get('mission')
        content.about = data.get('about')
        content.address = data.get('address')
        content.hours = data.get('hours')
        content.email = data.get('email')
        content.phone = data.get('phone')
        content.facebook = data.get('facebook')
        content.donate_link = data.get('donateLink')
        db.session.commit()
        return jsonify({'message': 'Website content updated successfully'})

from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


@app.route('/api/messages', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def api_messages():
    if request.method == 'GET':
        data = [{
            'id': m.id,
            'name': m.name,
            'email': m.email,
            'subject': m.subject,
            'message': m.message,
            'date': m.date,
            'status': m.status
        } for m in Message.query.order_by(Message.id.desc()).all()]
        return jsonify(data)

    if request.method == 'POST':
        data = request.get_json()
        new_msg = Message(
            name=data.get('name', ''),
            email=data.get('email', ''),
            subject=data.get('subject', ''),
            message=data.get('message', ''),
            date=datetime.now().strftime('%Y-%m-%d %H:%M'),
            status='Unread'
        )
        db.session.add(new_msg)
        db.session.commit()

        # ---------- EMAIL NOTIFICATION ----------
        sender_email = "braintreefoodpantrycontact@gmail.com"
        app_password = "kuqn rgkv cajd cfbr"

        recipients = [
            "braintreefoodpantrydirector@gmail.com",   # <-- REQUIRED
            "YOUR_SECOND_EMAIL@gmail.com"             # <-- optional
        ]

        email_subject = f"New Contact Form Submission: {new_msg.subject}"
        email_body = f"""
    A new message was submitted through the Braintree Food Pantry contact form.

    Name: {new_msg.name}
    Email: {new_msg.email}
    Subject: {new_msg.subject}

    Message:
    {new_msg.message}

    Submitted on: {new_msg.date}
    """

        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = email_subject
            msg.attach(MIMEText(email_body, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.sendmail(sender_email, recipients, msg.as_string())

        except Exception as e:
            print("EMAIL SENDING ERROR:", e)

        # ---------- RETURN SUCCESS ----------
        return jsonify({'message': 'Message sent successfully'}), 201


    if request.method == 'PATCH':
        data = request.get_json()
        msg_id = data.get('id')
        msg = Message.query.get(msg_id)
        if not msg:
            return jsonify({'error': 'Message not found'}), 404

        # Only update status if provided
        if 'status' in data:
            msg.status = data['status']
        db.session.commit()
        return jsonify({'message': f'Message {msg.id} updated successfully', 'status': msg.status}), 200

    if request.method == 'DELETE':
        msg_id = request.args.get('id')
        msg = Message.query.get(msg_id)
        if not msg:
            return jsonify({'error': 'Message not found'}), 404

        db.session.delete(msg)
        db.session.commit()
        return jsonify({'message': 'Message deleted successfully'}), 200



@app.route('/api/testimonials', methods=['GET', 'POST', 'DELETE'])
def testimonials():
    if request.method == 'GET':
        data = [
            {
                'id': t.id,
                'name': t.name,
                'profession': t.profession,
                'message': t.message,
                'image_path': t.image_path
            } for t in Testimonial.query.all()
        ]
        return jsonify(data)

    if request.method == 'POST':
        name = request.form['name']
        profession = request.form['profession']
        message = request.form['message']
        file = request.files.get('image')

        img_path = None
        if file:
            filename = file.filename
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            img_path = f'uploads/{filename}'

        new_t = Testimonial(name=name, profession=profession, message=message, image_path=img_path)
        db.session.add(new_t)
        db.session.commit()
        return jsonify({'message': 'Testimonial added successfully'}), 201

    if request.method == 'DELETE':
        id = request.args.get('id')
        t = Testimonial.query.get(id)
        if not t:
            return jsonify({'error': 'Not found'}), 404
        db.session.delete(t)
        db.session.commit()
        return jsonify({'message': 'Testimonial deleted successfully'})

@app.route('/api/news', methods=['GET', 'POST', 'DELETE'])
def api_news():
    if request.method == 'GET':
        data = [
            {
                "id": n.id,
                "title": n.title,
                "description": n.description,
                "image_path": n.image_path,
                "date": n.date
            }
            for n in News.query.order_by(News.id.desc()).all()
        ]
        return jsonify(data)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        file = request.files.get('image')

        img_path = None
        if file:
            filename = file.filename
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            img_path = f"uploads/{filename}"

        item = News(
            title=title,
            description=description,
            date=date,
            image_path=img_path
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({"message": "News item added"}), 201

    if request.method == 'DELETE':
        nid = request.args.get("id")
        n = News.query.get(nid)
        if not n:
            return jsonify({"error": "Not found"}), 404

        # delete file
        if n.image_path:
            path = os.path.join(app.config['UPLOAD_FOLDER'], n.image_path.replace("uploads/",""))
            if os.path.exists(path):
                os.remove(path)

        db.session.delete(n)
        db.session.commit()
        return jsonify({"message": "News deleted"})
    

@app.route("/paypal/webhook", methods=["POST"])
def paypal_webhook():
    data = request.json

    # Confirm PayPal actually sent the event
    event_type = data.get("event_type", "")

    # We only save completed donations
    if event_type == "PAYMENT.CAPTURE.COMPLETED":

        resource = data["resource"]
        payer = resource.get("payer", {})

        # Extract donor fields
        first = payer.get("name", {}).get("given_name", "")
        last = payer.get("name", {}).get("surname", "")
        donor_name = f"{first} {last}".strip() or "Anonymous"

        email = payer.get("email_address", "")
        amount = float(resource["amount"]["value"])
        txn_id = resource.get("id", "no-ref")

        donation = Donation(
            name=donor_name,
            amount=amount,
            method="PayPal",
            ref=txn_id,
            notes=email,  # optional
            date=datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        db.session.add(donation)
        db.session.commit()

    # PayPal requires a 200 OK response
    return jsonify({"status": "ok"}), 200


@app.route('/api/donations', methods=['GET'])
def get_donations():
    data = [
        {
            'id': d.id,
            'name': d.name,
            'amount': d.amount,
            'method': d.method,
            'ref': d.ref,
            'notes': d.notes,
            'date': d.date
        } for d in Donation.query.all()
    ]
    return jsonify(data)


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('admin'))
        else:
            # If credentials are wrong, reload page with error message
            return render_template('login.html', error='Invalid username or password.')

    # If GET request (first visit)
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
