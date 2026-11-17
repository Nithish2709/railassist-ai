import json
import pandas as pd

df = pd.read_csv('data/raw/inidian_railway_complaint_tweets.csv')

# Explicit mapping from Type to Target Category
MAPPING = {
    # Operations & Traffic
    'punctuality': 'Operations & Traffic',
    'train delay': 'Operations & Traffic',
    'cancelled train': 'Operations & Traffic',
    'delay': 'Operations & Traffic',

    # Housekeeping
    'cleanliness': 'Housekeeping',
    'bed roll': 'Housekeeping',

    # Passenger Grievance
    'corruption / bribery': 'Passenger Grievance',
    'staff behaviour': 'Passenger Grievance',
    'crowding': 'Passenger Grievance',
    'ticket booking': 'Passenger Grievance',
    'refund': 'Passenger Grievance',
    'ticket booking charge': 'Passenger Grievance',
    'ticket/ seat availability': 'Passenger Grievance',
    'difficulty in booking tickets': 'Passenger Grievance',
    'fare charges': 'Passenger Grievance',

    # Security
    'security': 'Security',
    'safety': 'Security',

    # Electrical
    'electrical equipment': 'Electrical',

    # Catering
    'catering & vending service': 'Catering',
    'food': 'Catering',
    'food quality': 'Catering',

    # Coach Maintenance
    'maintenance': 'Coach Maintenance',
    'poor condition': 'Coach Maintenance',
    'bed': 'Coach Maintenance',

    # Water & Sanitation
    'water availability': 'Water & Sanitation',

    # Medical Assistance
    'medical assistance': 'Medical Assistance'

    # Engineering has NO labels in the dataset
}

# Only consider complaints
complaints = df[df['Label'] == 'complaint'].copy()
complaints['Mapped_Category'] = complaints['Type'].map(MAPPING)

mapped_df = complaints.dropna(subset=['Mapped_Category']).copy()

print(f"Total raw complaints: {len(complaints)}")
print(f"Total mapped complaint rows: {len(mapped_df)}")
print(f"Total unmapped/excluded complaint rows: {len(complaints) - len(mapped_df)}")

print("\n--- Distribution BEFORE deduplication ---")
print(mapped_df['Mapped_Category'].value_counts())

# Check duplicates in mapped_df
dup_count = mapped_df.duplicated(subset=['Tweet']).sum()
print(f"\nDuplicates in mapped complaints: {dup_count}")

dedup_df = mapped_df.drop_duplicates(subset=['Tweet'], keep='first').copy()
print(f"Total after dropping duplicate tweets: {len(dedup_df)}")

print("\n--- Distribution AFTER deduplication ---")
counts = dedup_df['Mapped_Category'].value_counts()
for cat, count in counts.items():
    pct = (count / len(dedup_df)) * 100
    print(f"  {cat:22s}: {count:4d} ({pct:5.1f}%)")
