"""cleans raw data & make clean dataset"""

import json
import re
import string
from num2words import num2words
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk

#Download the required ntlk data packages
nltk.download("wordnet", quiet=True) #For lemmatization
nltk.download("stopwords", quiet=True) #For stopwords

#Initialize the NLP tools
STOP_WORDS = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


def clean(text):

    #Remove non-ASCII characters (special characters and emojis)
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    #Convert numbers to words
    text = re.sub(r'\b\d+\b', lambda m: num2words(int(m.group())), text)

    #Lowercase all text
    text = text.lower()

    #Remove the punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    #Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()

    #Remove stop words and lemmatize
    tokens = [lemmatizer.lemmatize(w) for w in text.split() if w not in STOP_WORDS]

    return ' '.join(tokens)


#Load raw reviews from the json file
raw = [json.loads(line) for line in open("../data/reviews_raw.jsonl") if line.strip()]

#Remove duplicates reviews by reviewId
seen, deduped = set(), []
for r in raw:
    if r["reviewId"] not in seen:
        seen.add(r["reviewId"])
        deduped.append(r)

#Remove empty or extremely short reviews (fewer than 5 words)
valid = [r for r in deduped if len((r.get("content") or "").split()) >= 5]

#Clean the content of each review
for r in valid:
    r["content"] = clean(r["content"])

#Save the cleaned reviews in the correct file
with open("../data/reviews_clean.jsonl", "w") as f:
    for r in valid:
        f.write(json.dumps(r) + "\n")

print(f"Done. {len(valid)} reviews saved to data/reviews_clean.jsonl")