from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv
import re
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    try:
        chrome_options = Options()
        
        # Create a new profile directory for automation
        profile_dir = os.path.join(os.getcwd(), "chrome_profile")
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
            
        # Set up Chrome options
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")
        chrome_options.add_argument("--profile-directory=Default")
        
        # Additional options to prevent crashes
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # Create a new service
        service = Service()
        
        # Initialize the driver with the service
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        raise

def wait_for_element(driver, by, value, timeout=10):
    """Wait for an element to be present on the page."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except Exception as e:
        print(f"Timeout waiting for element {value}: {e}")
        return None

def send_email(posts, region, recipient_email):
    """Send scraped posts via email."""
    if not posts:
        print(f"No posts found for {region}, skipping email.")
        return

    # Email configuration
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    # Validate email credentials
    if not sender_email or not sender_password:
        print("Error: Email credentials not found in .env file")
        print("Please create a .env file with:")
        print("EMAIL_USER=your_email@outlook.com")
        print("EMAIL_PASSWORD=your_app_password")
        return
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"LinkedIn Posts Update - {region} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Create email body
    body = "Here are the latest LinkedIn posts:\n\n"
    for i, post in enumerate(posts, 1):
        body += f"Post {i}:\n"
        body += f"Content: {post['content']}\n"
        body += f"Hashtags: {', '.join(post['hashtags'])}\n"
        body += "-" * 80 + "\n\n"
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        print(f"Attempting to send email to {recipient_email}...")
        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login to the server
        print("Logging in to email server...")
        server.login(sender_email, sender_password)
        
        # Send email
        print("Sending email...")
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your .env file exists and contains:")
        print("   EMAIL_USER=your_email@outlook.com")
        print("   EMAIL_PASSWORD=your_app_password")
        print("2. For Outlook/Hotmail, you need to:")
        print("   - Enable 2-factor authentication")
        print("   - Generate an App Password")
        print("   - Use the App Password in your .env file")
        print("3. Check your internet connection")

def clean_text(text):
    """Clean and format the text content."""
    # Remove HTML tags
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    
    # Replace multiple newlines with single newline
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Clean up bullet points
    text = re.sub(r'•\s*', '• ', text)
    
    # Remove any remaining HTML entities
    text = re.sub(r'&[a-zA-Z]+;', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def scrape_posts(url):
    """Scrape the first 5 posts from the given URL."""
    driver = setup_driver()
    try:
        # Go directly to search results
        print("Navigating to search results...")
        driver.get(url)
        
        # Wait for the page to load with explicit wait
        wait = WebDriverWait(driver, 20)  # Increased timeout to 20 seconds
        
        # Wait for either the feed content or login form
        try:
            # Wait for feed content to appear
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.update-components-text")))
            print("Page loaded successfully!")
        except:
            print("Waiting for page to load...")
            time.sleep(10)  # Additional wait time
        
        # Find all posts using the correct selector
        print("Looking for posts...")
        posts = driver.find_elements(By.CSS_SELECTOR, "div.update-components-text")[:5]
        print(f"Found {len(posts)} posts")
        
        results = []
        for i, post in enumerate(posts, 1):
            try:
                print(f"Processing post {i}...")
                # Get the post content using the correct selector
                content_element = post.find_element(By.CSS_SELECTOR, "span.break-words")
                raw_content = content_element.get_attribute('innerHTML')
                
                # Clean and format the content
                content = clean_text(raw_content)
                
                # Get hashtags if they exist
                hashtags = []
                hashtag_elements = post.find_elements(By.CSS_SELECTOR, "a[data-test-app-aware-link]")
                for tag in hashtag_elements:
                    hashtag_text = tag.text.strip()
                    if hashtag_text.startswith('#'):
                        hashtags.append(hashtag_text)
                
                results.append({
                    "content": content,
                    "hashtags": hashtags
                })
                print(f"Successfully processed post {i}")
            except Exception as e:
                print(f"Error extracting post {i}: {e}")
                continue
                
        return results
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
    finally:
        print("Closing browser...")
        driver.quit()

def process_region(region):
    """Process a single region's posts."""
    print(f"\n{'='*50}")
    print(f"Processing region: {region['name']}")
    print(f"{'='*50}\n")
    
    # Construct URL
    url = os.getenv("SCRAPE_URL")
    recipient = os.getenv("RECIPIENT_EMAIL")
    
    # Scrape posts
    posts = scrape_posts(url)
    
    # Send email if posts found
    send_email(posts, region['name'], recipient)
    
    # Print results
    if posts:
        print(f"\nScraped Posts for {region['name']}:")
        for i, post in enumerate(posts, 1):
            print(f"\nPost {i}:")
            print(f"Content: {post['content']}")
            print(f"Hashtags: {', '.join(post['hashtags'])}")
            print("-" * 80)

if __name__ == "__main__":
    # Load environment variables
    load_dotenv() 
    process_region({'name': 'UAE'}) 