from fastapi import FastAPI
from pydantic import BaseModel
import boto3
import os
import whisper
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback

# Import AWS credentials
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, S3_BUCKET_NAME

# Initialize FastAPI
app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS S3 client
s3_client = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

# Define Pydantic model for request body
class TranscribeRequest(BaseModel):
    file_key: str

# Fetch available audio files from S3
@app.get("/audio-files")
async def list_audio_files():
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix="audio_")
        if "Contents" in response:
            return [content["Key"] for content in response["Contents"]]
        return []
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error fetching audio files: {e}"})

# Transcribe the selected audio file

@app.post("/transcribe")
async def transcribe_audio(request: TranscribeRequest):
    try:
        file_key = request.file_key  # Extract file key

        # Ensure the /tmp directory exists
        temp_dir = "/tmp" if os.name != "nt" else "tmp"
        os.makedirs(temp_dir, exist_ok=True)

        # Download the audio file from S3
        audio_file_path = os.path.join(temp_dir, file_key.split('/')[-1])
        s3_client.download_file(S3_BUCKET_NAME, file_key, audio_file_path)

        # Debugging: Print confirmation that the file has been downloaded
        print(f"File downloaded successfully: {audio_file_path}")

        # Transcribe using Whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_file_path)

        return {"transcription": result["text"]}

    except Exception as e:
        error_message = traceback.format_exc()  # Get detailed error message
        print("Error occurred during transcription:", error_message)  # Print error to console
        return JSONResponse(status_code=500, content={"message": f"Error transcribing audio: {str(e)}"})

