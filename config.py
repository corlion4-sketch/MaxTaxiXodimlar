import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', "8502586197:AAE68DBK67jTvkiRPTCXjNlZftS6BlVTewE")

REGIONS = [
    "Andijon", "Buxoro", "Farg'ona", "Jizzax", 
    "Qashqadaryo", "Navoiy", "Namangan", "Samarqand",
    "Sirdaryo", "Surxondaryo", "Toshkent", "Urganch"
]
