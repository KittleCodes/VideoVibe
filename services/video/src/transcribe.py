import os
import wave
import re
import contextlib
import speech_recognition as sr
from moviepy.editor import AudioFileClip
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
import nltk

nltk.download('punkt')
nltk.download('stopwords')

def format_time_vtt(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{milliseconds:03}"

def extract_keywords(text):
    words = word_tokenize(text.lower())
    stopwords = set(nltk.corpus.stopwords.words('english'))
    filtered_words = [word for word in words if word.isalnum() and word not in stopwords]
    return Counter(filtered_words).most_common(10)

def find_sentence_times(sentences, words):
    sentence_times = []
    word_index = 0

    pattern = re.compile(r"\b\w+'\w*|\w+\b")

    for sentence in sentences:
        tokens = pattern.findall(sentence)
        print(tokens)
        sentence_word_count = len(tokens)
        
        if word_index + sentence_word_count > len(words):
            break

        start_time = words[word_index]["start"]
        end_time = words[word_index + sentence_word_count - 1]["end"]

        sentence_times.append({
            "sentence": sentence,
            "start": start_time,
            "end": end_time
        })

        word_index += sentence_word_count

    return sentence_times

def transcribe_and_save(video_file_path):
    base_name = os.path.splitext(os.path.basename(video_file_path))[0]
    dash_output_path = os.path.join('dash/', base_name)
    os.makedirs(dash_output_path, exist_ok=True)
    
    transcribed_audio_file_name = f"{base_name}.wav"
    vtt_file_name = os.path.join(dash_output_path, f"{base_name}.vtt")

    audioclip = AudioFileClip(video_file_path)
    audioclip.write_audiofile(transcribed_audio_file_name)

    with contextlib.closing(wave.open(transcribed_audio_file_name, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()

    r = sr.Recognizer()

    keywords_dict = {}

    with open(vtt_file_name, "w") as vtt_file:
        vtt_file.write("WEBVTT\n\n")

        with sr.AudioFile(transcribed_audio_file_name) as source:
            audio = r.record(source)

        try:
            text = r.recognize_whisper(audio, word_timestamps=True, show_dict=True)
            words = []
            for idx, segment in enumerate(text['segments']):
                for word in segment['words']:
                    words.append(word)
                    
            compiled = ''.join([word["word"] for word in words])
            sentences = sent_tokenize(compiled)
            
            sentence_times = find_sentence_times(sentences, words)
            
            for idx, st in enumerate(sentence_times):
                start_time_vtt = format_time_vtt(st['start'])
                end_time_vtt = format_time_vtt(st['end'])

                vtt_file.write(f"{idx + 1}\n")
                vtt_file.write(f"{start_time_vtt} --> {end_time_vtt}\n")
                vtt_file.write(f"{st['sentence']}\n\n")

            keywords = extract_keywords(text['text'])
            for keyword, count in keywords:
                if keyword in keywords_dict:
                    keywords_dict[keyword] += count
                else:
                    keywords_dict[keyword] = count

        except sr.UnknownValueError:
            print("Could not understand audio.")

    os.remove(transcribed_audio_file_name)

    return keywords_dict
