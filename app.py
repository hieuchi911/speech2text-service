import urllib
import os
from pydub.utils import make_chunks
from pydub import AudioSegment

from sanic import Sanic
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import soundfile as sf
import torch
from sanic.response import json

app = Sanic("STT-Server")

@app.before_server_start
async def load_model(app):
    global AI_MODEL, PROCESSOR
    PROCESSOR = Wav2Vec2Processor.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h",
                                                cache_dir="models/wav2vec2-base-vietnamese-250h")
    AI_MODEL = Wav2Vec2ForCTC.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h",
                                                cache_dir="models/wav2vec2-base-vietnamese-250h")

@app.route('/to-text', methods=['POST'])
async def speech_to_text(request):
    global AI_MODEL

    # Retreive audio file (from external db?)
    url = request.json['url']
    uid = request.json['uid']
    
    received_file = f'facebook-audio/output_{uid}.mp4'
    wav_file =  f'facebook-audio/output_{uid}.wav'

    urllib.request.urlretrieve(url, received_file)
    os.system('ffmpeg -y -i {} -acodec pcm_s16le -ar 16000 -ac 1 {}'.format(received_file, wav_file))
    num_files = make_chunk(f'facebook-audio/output_{uid}.wav', uid)
    
    transcription = []
    for i in range(num_files):
        ds = map_to_array({
            "file": f"audio/audio-chunks-user-{uid}/chunk{i+1}.wav"
        })

        # tokenize
        input_values = PROCESSOR(ds["speech"], return_tensors="pt", padding="longest").input_values  # Batch size 1

        # retrieve logits
        logits = AI_MODEL(input_values).logits
        # take argmax and decode
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription += (PROCESSOR.batch_decode(predicted_ids))

    return json({'text': " ".join(transcription)})

def make_chunk(file, uid):
    file = AudioSegment.from_wav(file)
    chunks = make_chunks(file, 10000)
    folder_name = f"audio/audio-chunks-user-{uid}"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)

    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
    
    return len(chunks)

def map_to_array(batch):
    speech, _ = sf.read(batch["file"])
    batch["speech"] = speech
    return batch

if __name__ == '__main__':
    app.run()
