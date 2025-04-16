import whisper

model = whisper.load_model("tiny.en")

def transcribe_from_memory(audio_blob):
    try:
        result = model.transcribe(audio_blob, fp16=False)
        return result
    finally:
  
        pass










    
