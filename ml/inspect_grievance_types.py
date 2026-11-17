import pandas as pd

df = pd.read_csv('data/raw/inidian_railway_complaint_tweets.csv')
complaints = df[df['Label'] == 'complaint']

for t in ['staff behaviour', 'corruption / bribery', 'ticket booking', 'refund', 'crowding', 'service', 'facility', 'miscellaneous', 'others', 'political']:
    subset = complaints[complaints['Type'] == t]
    print(f"\n==================== Type: {t} (Count: {len(subset)}) ====================")
    for i, s in enumerate(subset['Tweet'].head(4), 1):
        clean_s = ' '.join(s.split())[:140]
        print(f"  {i}. {clean_s}...")
