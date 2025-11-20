import cv2
import mediapipe as mp
import winsound
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ---------------- SEND EMAIL WITH PHOTO ----------------
def send_email_with_photo(subject, body, image_path):
    sender = "habeebjaffer3883@gmail.com"
    password = "ztfvqnefxvmqovrs"    # Gmail App Password

    receiver = sender   # <-- Send email to yourself

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    msg.attach(MIMEText(body, "plain"))

    try:
        with open(image_path, "rb") as attachment:
            mime = MIMEBase("application", "octet-stream")
            mime.set_payload(attachment.read())
            encoders.encode_base64(mime)
            mime.add_header(
                "Content-Disposition",
                f"attachment; filename={image_path}"
            )
            msg.attach(mime)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print("Email with photo sent to yourself!")

    except Exception as e:
        print("Error sending email:", e)


# ---------------- POSE DETECTION ----------------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
email_sent = False  # To avoid repeated emails

print("Camera started... Waiting for human detection...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        winsound.Beep(1000, 150)

        if not email_sent:
            print("Human detected! Capturing image...")

            image_path = "detected_human.jpg"
            cv2.imwrite(image_path, frame)

            print("Sending email with attached image...")
            send_email_with_photo(
                subject="Alert: Human Detected",
                body="A human was detected. Attached is the captured image.",
                image_path=image_path
            )

            email_sent = True
        else:
            print("Human detected (email already sent)")

    else:
        if email_sent:
            print("Human left the frame — reset email alert")
        email_sent = False

    cv2.imshow("Pose Estimation", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        print(" Program closed by user.")
        break

cap.release()
cv2.destroyAllWindows()
