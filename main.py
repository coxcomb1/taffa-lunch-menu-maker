import requests
from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


LANGUAGE = "en"
URI = 'today' # Returns a text only version of today's lunch. Shows monday's food on weekends.
#URI = {day}/{month}/{year} # Returns the menu for the specified date if menu is known.

class TaffaMenu:
    
    def get_lunch_data(self, uri: str) -> list:
        
        print('Fetching data from Täffä API ...')
        
        url = f'http://api.tf.fi/taffa/{LANGUAGE}/{uri}/'
        response = requests.get(url)
        self.date = response.headers['Date'][:11]
        menu = response.text
        print('Data fetched successfully')
        return TaffaMenu._create_menu_text(menu, self.date)
        
    def _create_menu_text(menu: str, date: str) -> list:
        lines: list = f"Menu for {date}:\n\n{menu}".splitlines()
        return lines

    def draw_text_on_image(self, text: list):
        
        print('Creating image...')
        
        # Create a new image
        image = Image.new('RGB', (500, 150), color = (255, 255, 255))

        # Create a Draw object
        draw = ImageDraw.Draw(image)

        # Define the font and size
        font = ImageFont.truetype('arial.ttf', 15)
        bold_font = ImageFont.truetype('arialbd.ttf', 21)

        # Draw each line onto the image
        y_text = 10
        for i, line in enumerate(text):
            if i == 0:  # The first line
                draw.text((10, y_text), line, font=bold_font, fill=(0, 0, 0))
            else:
                draw.text((10, y_text), line, font=font, fill=(0, 0, 0))
            y_text += 18

        # Save the image
        image.save('taffa-menu-today.png')
        
        print('Image created successfully')
        
    def send_image_to_email(self):
        
        print('Sending email...')
        
        try: 
            # Email details
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = "my_email@tf.fi"
            sender_password = 'usr_pwd'
            receiver_email = "henkki@tf.fi"
            
            # Create a MIMEMultipart object
            msg = MIMEMultipart()

            # Add the subject, sender, and receiver
            msg['Subject'] = f'Taffa Menu for {self.date}'
            msg['From'] = sender_email
            msg['To'] = receiver_email

            # Create a MIMEText object for the email body
            body = MIMEText('See attached', 'plain')
            msg.attach(body)

            # Open the image file in binary mode, create a MIMEImage object, and attach it to the email
            with open('taffa-menu-today.png', 'rb') as img:
                msg_img = MIMEImage(img.read())
                msg_img.add_header('Content-Disposition', 'attachment', filename='taffa-menu-today.png')
                msg.attach(msg_img)

            # Connect to the SMTP server, log in, send the email, and close the connection
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                
        except Exception as e:
            print(f'Failed to send email. Error message: {e}')
            
        print('Email sent successfully')
        
    # def send_image_to_google_chat(self):
    #     from google.oauth2 import service_account
    #     from googleapiclient.discovery import build
    #     import json

    #     # Load the credentials from the service account file
    #     credentials = service_account.Credentials.from_service_account_file(
    #         'tf-hemsida-71b3e056593f.json',
    #         scopes=['https://www.googleapis.com/auth/chat.bot'])

    #     # Build the service
    #     chat_service = build('chat', 'v1', credentials=credentials)

    #     # Define the message
    #     message = {
    #         'text': 'Hello, world!'
    #     }

    #     # Send the message
    #     response = chat_service.spaces().messages().create(
    #         parent='spaces/AAAAE5OLi3o', # replace with the space ID where you want to send the message
    #         body=message).execute()

    #     print(response)
    
         
def main():
    taffa = TaffaMenu()
    data = taffa.get_lunch_data(uri=URI)
    taffa.draw_text_on_image(data)
    taffa.send_image_to_email()
    
if __name__ == "__main__":
    main()