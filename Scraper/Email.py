from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from Scraper.Scoring import fetch_car_data_with_scores


def fetch_recent_highscore(lowest_score, search, price_importance=1, year_importance=1, mileage_importance=1):
    item_list_from_search = None
    mode = 'scrape'
    cars_scored_dict = fetch_car_data_with_scores(mode, item_list_from_search, price_importance, mileage_importance,
                                                  year_importance, search)

    # Filter items based on the lowest_score
    filtered_cars = [car for car in cars_scored_dict if car['score'] >= float(lowest_score)]

    if filtered_cars:
        # Only send email if there are cars to notify about
        send_email_notification(filtered_cars)
        print(f"Sent email for {len(filtered_cars)} cars.")
    else:
        print("No cars found with the specified score. No email sent.")

    return filtered_cars


def send_email_notification(filtered_cars):
    # Email account credentials
    sender_email = "starojos000@gmail.com"
    receiver_email = "starojos000@gmail.com"  # Set to your email or phone’s SMS gateway
    password = "pxmh wthu vayt jdhy"

    # Email content
    subject = "Deal Alert!"
    body = "Found good deals:\n\n"

    for car in filtered_cars:
        car_details = (
            f"Name: {car['name']}\n"
            f"Price: ${car['price']}\n"
            f"Miles: {car['miles']} miles\n"
            f"Year: {car['year']}\n"
            f"Score: {car['score']}\n"
            f"Link: {car['link']}\n"
        )
        body += car_details + "\n---\n"

    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Notification sent!")
    except Exception as e:
        print("Failed to send email:", e)


if __name__ == "__main__":
    lowest_score = 70
    search_car = 'Honda Accord'
    cars = fetch_recent_highscore(lowest_score, search_car)
    print('hi')
    for i in cars:
        print(i)