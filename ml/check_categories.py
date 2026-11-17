import pandas as pd

df = pd.read_csv('data/raw/inidian_railway_complaint_tweets.csv')

print("=== 1. MEDICAL ASSISTANCE RECORDS ===")
med = df[df['Type'] == 'medical assistance']
for _, r in med.iterrows():
    lbl = r['Label']
    txt = ' '.join(r['Tweet'].split())[:130]
    print(f"[{lbl}] {txt}...")

print("\n=== 2. ENGINEERING MATCHES ===")
eng = df[df['Type'].str.contains('eng', case=False, na=False)]
for _, r in eng.iterrows():
    print(f"[{r['Label']}] Type={r['Type']} | {r['Tweet'][:130]}...")

print("\n=== 3. SAMPLES OF MAINTENANCE ===")
maint = df[(df['Type'] == 'maintenance') & (df['Label'] == 'complaint')]
for _, r in maint.head(4).iterrows():
    print(' '.join(r['Tweet'].split())[:130] + '...')

print("\n=== 4. SAMPLES OF SECURITY AND SAFETY ===")
sec = df[(df['Type'].isin(['security', 'safety'])) & (df['Label'] == 'complaint')]
for _, r in sec.head(4).iterrows():
    print(f"Type={r['Type']} | " + ' '.join(r['Tweet'].split())[:130] + '...')

print("\n=== 5. SAMPLES OF STAFF BEHAVIOUR & CORRUPTION ===")
stf = df[(df['Type'].isin(['staff behaviour', 'corruption / bribery'])) & (df['Label'] == 'complaint')]
for _, r in stf.head(4).iterrows():
    print(f"Type={r['Type']} | " + ' '.join(r['Tweet'].split())[:130] + '...')

print("\n=== 6. SAMPLES OF BED ROLL ===")
bed = df[(df['Type'] == 'bed roll') & (df['Label'] == 'complaint')]
for _, r in bed.head(4).iterrows():
    print(' '.join(r['Tweet'].split())[:130] + '...')
