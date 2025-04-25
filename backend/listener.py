import paho.mqtt.client as mqtt
import sounddevice as sd
import numpy as np
import wave
import boto3
import time
import config
import threading

# Global state
recording = False
audio_data = []
recording_thread = None  # New variable to track recording thread
s3_client = boto3.client("s3", aws_access_key_id=config.AWS_ACCESS_KEY, aws_secret_access_key=config.AWS_SECRET_KEY)

def on_message(client, userdata, message):
    global recording, audio_data, recording_thread
    payload = message.payload.decode()
    print(f"Received MQTT message (camera status): {payload}")

    if payload == "off":
        if not recording:
            print("🔴 Recording started...")
            recording = True
            audio_data = []
            recording_thread = threading.Thread(target=record_audio)
            recording_thread.start()

    elif payload == "on" and recording:
        print("🛑 Stopping recording...")
        recording = False  # This will stop the recording thread
        if recording_thread:
            recording_thread.join()  # Ensure thread completes before saving
        save_and_upload_audio()

def record_audio():
    global recording, audio_data

    def callback(indata, frames, time, status):
        if status:
            print(status)
        if recording:
            audio_data.append(indata.copy())

    with sd.InputStream(callback=callback, samplerate=44100, channels=1):
        while recording:
            sd.sleep(100)  # Allow time for message processing

def save_and_upload_audio():
    global audio_data

    if not audio_data:
        print("No audio recorded.")
        return

    filename = f"audio_{int(time.time())}.wav"
    print(f"Saving {filename}...")

    # Convert list to NumPy array
    audio_array = np.concatenate(audio_data, axis=0)

    # Save to a WAV file
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())

    # Upload to S3
    print(f"Uploading {filename} to S3...")
    s3_client.upload_file(filename, config.S3_BUCKET_NAME, filename)
    print("✅ Upload complete!")

# MQTT setup
client = mqtt.Client()
client.on_message = on_message
client.connect(config.MQTT_BROKER, config.MQTT_PORT)
client.subscribe(config.MQTT_TOPIC)
client.loop_forever()
