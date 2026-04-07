"""imports or reads your raw dataset; if you scraped, include scraper here"""

import json
from google_play_scraper import reviews, Sort

all_reviews = []
#Continuation token is used by the API to keep track of where the last fetch left off
token = None

#Loop until we have collected at least 1000 reviews
while len(all_reviews) < 1000:
    batch, token = reviews(
        "com.calm.android", #The calm app
        lang="en",
        country="us",
        sort=Sort.NEWEST, #Getting the relevant reviews (Most recent)
        count=min(200, 1000 - len(all_reviews)), #Fetch 200 reviews at a time, or exactly what is left to reach 1000
        continuation_token=token, #Pass the token to get the next page of results
    )

    #Add the new patch
    all_reviews.extend(batch)

    #If the API doesn't return a token, it means there are no more reviews left to fetch
    if not token:
        break

#Saves the reviews in the correct file
with open("data/reviews_raw.jsonl", "w", encoding="utf-8") as f:
    for r in all_reviews:
        f.write(json.dumps(r, default=str) + "\n")

print(f"Saved {len(all_reviews)} reviews to data/reviews_raw.jsonl")