from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
from typing import Optional
import shutil
import os
from mdp3 import CredentialGeneratorMDP
from typing import Dict, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#creates endpoints
app = FastAPI(title="Routes")

@app.post("/upload-wordlist")
async def upload_wordlist(file: UploadFile = File(...)):
    # Save to local path so you can use it in mdp3
    filename = f"./wordlist_uploads/{file.filename}"
    os.makedirs("./wordlist_uploads", exist_ok=True)
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"path": filename}

class CredentialRequest(BaseModel):
    # path or name of the wordlist if needed
    wordlist_path: Optional[str] = ""

    # toggles for user
    user_include_char: bool = True
    user_include_num: bool = True
    user_include_sym: bool = True
    user_length: int = 12

    # toggles for password
    pass_include_char: bool = True
    pass_include_num: bool = True
    pass_include_sym: bool = True
    pass_length: int = 12

    # how many credentials to generate
    count: int = 10

class AIParams(BaseModel):
    params: Dict[str, str | bool | int] = Field(default_factory=dict)


@app.post("/generate-credentials")
async def generate_credentials_endpoint(file: UploadFile = File(None), data: str = Form(...)):
    #logging.info(f"Received credential generation request: {req}")
    file_word = ""
    try:
        """   temp = json.loads(data)
        print(temp)
        # Parse JSON data from form
        ai_params = AIParams(params=json.loads(data))
        print(ai_params)"""
        if file:
            # Save the uploaded file
            file_location = f"./wordlist_uploads/{file.filename}"
            with open(file_location, "wb") as buffer:
                buffer.write(await file.read())
            file_word= file_location  # Store file path in dictionary
 
 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    print("second")
    print(data)
    print(file_word)
    data = json.loads(data)
    generator = CredentialGeneratorMDP(
        csv_path= "site_list.csv",
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
    return {"credentials": credentials}

    """
    generator = CredentialGeneratorMDP(
        csv_path ="site_list.csv",      # or wherever your CSV is
        wordlist_path =req.wordlist_path or "wordlist_uploads\wordlist.txt",

        user_include_char = req.user_include_char or True,
        user_include_num = req.user_include_num or True,
        user_include_sym = req.user_include_sym or True,
        user_length = req.user_length or 12,

        pass_include_char = req.pass_include_char or True,
        pass_include_num = req.pass_include_num or True,
        pass_include_sym = req.pass_include_sym or True,
        pass_length = req.pass_length or 12
    )"""



# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)