import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', "8502586198:AAE68DBK67jTvkiRPTCXjNlZftS6BlVTewE")
DATABASE_URL = os.getenv('DATABASE_URL')

REGIONS = [
    "Andijon", "Buxoro", "Farg'ona", "Jizzax", 
    "Qashqadaryo", "Navoiy", "Namangan", "Samarqand",
    "Sirdaryo", "Surxondaryo", "Toshkent", "Urganch"
]