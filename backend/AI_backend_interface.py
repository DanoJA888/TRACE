from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
from typing import Optional
import shutil
import os
import mdp3
from mdp3 import CredentialGeneratorMDP, WebScraper, CredentialMDP
from typing import Dict, Optional
import json
import csv
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#creates endpoints
app = FastAPI(title="Routes")

def extract_services_sites(json_path: str = 'outputs_crawler/crawl_results.json',
                           csv_path: str = 'services_sites/services_sites.csv') -> bool:
    # Ensure the folder for the CSV exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'website'])
            for entry in data:
                writer.writerow([entry.get('id'), entry.get('url')])

        return True  # Success

    except FileNotFoundError:
        return False  # JSON file was not found

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False  # Handle any other issues


class AIParams(BaseModel):
    params: Dict[str, str | bool | int] = Field(default_factory=dict)


@app.post("/generate-credentials")
async def generate_credentials_endpoint(file: UploadFile = File(None), data: str = Form(...)):
    #logging.info(f"Received credential generation request: {req}")
    file_word = ""
    try:
        if file:
            # Save the uploaded file
            file_location = f"./wordlist_uploads/{file.filename}"
            with open(file_location, "wb") as buffer:
                buffer.write(await file.read())
            file_word= file_location  # Store file path in dictionary
 
 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    craw_state = extract_services_sites() 
    if (craw_state == False):
        return {"crawler": craw_state}
       
    urls = mdp3.load_urls_from_csv("services_sites/services_sites.csv")
    csv_path = "./csv_uploads/web_text.csv"
    scrapper = WebScraper(urls)
    scrapper.generate_csv(csv_path)
    mdp3.nlp_subroutine(csv_path)

    data = json.loads(data)
    generator = CredentialGeneratorMDP(
        csv_path= csv_path,
        wordlist_path= file_word,
        user_include_char = data["userChar"],
        user_include_num = data["userNum"],
        user_include_sym = data["userSymb"],
        user_length = data["userLen"],

        pass_include_char = data["passChar"],
        pass_include_num = data["passNum"],
        pass_include_sym = data["passSymb"], 
        pass_length = data["passLen"] 
    )
    credentials = generator.generate_credentials(10)
    print("\nGenerated Credentials:")
    for username, password in credentials:
        print(f"Username: {username}, Password: {password}")
    return {"credentials": credentials}


# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)