"""
ml/get_dept_samples.py
Generates 10 verified, realistic test complaints for every railway department
and verifies their classification through the trained Random Forest model.
"""

import json
import joblib

rf = joblib.load('backend/models/railassist_rf_pipeline.joblib')
with open('backend/app/category_mapping.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)

depts = cfg['departments']

# Curated, authentic complaint descriptions representing each operational department
samples = {
    "Housekeeping": [
        "The bio-toilet in coach S4 is severely clogged, overflowing with dirty water and emitting foul smell.",
        "Coach B2 is full of cockroaches crawling under the seats and trash has not been cleaned.",
        "The bedsheet and blanket provided in 2AC were dirty, stained, and smelled like unwashed linen.",
        "Garbage bin near the coach door is overflowing with paper cups, food packets and bad odor.",
        "Washbasin in coach S1 is stained with pan spit and full of filth, no cleaning staff attended.",
        "Floor of the sleeper compartment is full of dust and mud, please send housekeeping staff.",
        "The pillow cover provided in 3AC was torn and soiled, request fresh bedroll linen urgently.",
        "Toilets are extremely unhygienic with urine on the floor and foul stink throughout the coach.",
        "Cleaning staff did not clean the compartment or toilets since train departed source station.",
        "Unpleasant foul odor coming from the toilet vent throughout coach S6, need air freshener."
    ],
    "Operations & Traffic": [
        "Train 12951 Rajdhani Express is delayed by 5 hours with zero updates from station master.",
        "The train is stranded at the outer signal for more than 2 hours without moving.",
        "Why has train 12301 been held up at the crossing while freight trains are given priority?",
        "Train running 6 hours late and missed connecting train at Mughalsarai junction.",
        "Unscheduled halt at small station for over 90 minutes without any announcement.",
        "Train delayed by 4 hours, no information displayed on platform digital screen.",
        "Train 14005 is incessantly running late every single day, causing huge schedule disruption.",
        "Stuck in the train outside Kanpur for 3 hours without signal clearance.",
        "Train reached 7 hours after scheduled arrival time, complete punctuality failure.",
        "Train cancelled at the last minute without prior SMS notification to passengers."
    ],
    "Electrical": [
        "Air conditioning in coach B3 is not working and passengers are suffocating in heat.",
        "The mobile charging socket near berth 45 is not working and has no electric power supply.",
        "Coach lights are flickering continuously and two reading lamps are fused.",
        "AC is not working in coach B4, temperature is very high and fans are also stopped.",
        "The electrical charging points in the entire bay are dead, mobile phone cannot be charged.",
        "AC cooling is completely ineffective in coach B5, blowing hot air instead of cool air.",
        "Night lamp and main tube lights are not working in coach A1, coach is totally dark.",
        "No power in laptop charging sockets throughout coach B4.",
        "Fan is not working above berth 18 in sleeper coach S2, very hot and suffocating.",
        "Air conditioner stopped working over two hours ago in 3AC compartment."
    ],
    "Catering": [
        "Food was tremendous poor quality and tea served was cold, stale and sour.",
        "The dinner packet served by pantry staff was spoiled and rotten with bad pungent smell.",
        "IRCTC vendor overcharged 150 rupees for standard veg thali with MRP of 80.",
        "Breakfast packet was stale, bread was hard and butter packet was melted.",
        "Pantry car vendor refused to provide bill for bottled water and meals.",
        "The dinner served by catering staff had cockroaches inside the food packet.",
        "Unhygienic catering staff serving food without gloves or hair nets in pantry car.",
        "No dinner served in train 22414, pantry staff refused meals saying stock is over.",
        "Overcharging on food and cold meals served in Rajdhani express.",
        "Pantry vendor charging 30 rupees for 15 rupees Rail Neer water bottle."
    ],
    "Security": [
        "My laptop backpack and luggage were stolen from upper berth while I was sleeping, need RPF.",
        "Unauthorized men entered the ladies coach and are harassing female passengers, send police.",
        "Drunk and unruly passengers drinking alcohol and threatening passengers in coach S3.",
        "Pickpockets snatched gold chain near coach door when train started moving.",
        "Suspicious unknown persons entered reserved coach and threatening passengers with weapons.",
        "Luggage stolen from under berth 21 between Bhopal and Itarsi, request RPF assistance.",
        "A group of men abusing passengers and creating nuisance, please send RPF urgently.",
        "Passenger bag snatched at station platform while boarding sleeper coach.",
        "Unauthorized hawkers and aggressive beggars harassing families inside compartment.",
        "Theft reported in coach A2, purse containing cash and jewelry stolen at night."
    ],
    "Water & Sanitation": [
        "The toilet washbasin and flush tanks in coach S7 have no water since morning.",
        "Water tank is completely empty in coach B2, cannot use washroom.",
        "No water in taps throughout all toilets in coach S3, acute water problem.",
        "Taps in the toilet are completely dry, passengers unable to use washroom due to no water.",
        "Flush tank not working due to lack of water in train toilet compartment.",
        "Water availability is zero in sleeper coach S5, please refill water tank at next station.",
        "Train departed source station with dry water tanks, no water in washroom.",
        "Both western and Indian toilets in coach B1 have no water supply.",
        "Washroom taps have run dry, water not available in coach S9.",
        "Please arrange water filling in coach S8 at next junction, tanks have no water."
    ],
    "Passenger Grievance": [
        "TTE demanded extra money and bribe for allocating vacant berth in 3AC.",
        "Ticket cancelled 5 days ago but refund amount has not been credited to bank account.",
        "Ticket booking counter clerk closed window 1 hour before scheduled time.",
        "Unreserved passengers illegally occupying reserved seats and TTE refusing to help.",
        "TTE behaving very rudely and misbehaved with senior citizen passengers.",
        "Paid for confirmed Tatkal ticket but seat already occupied by unauthorized passengers.",
        "Cancellation fee deducted illegally on train cancelled by railways.",
        "TTE taking cash without issuing official EFT receipt in coach S2.",
        "UTS mobile app money deducted twice from account but ticket not generated.",
        "Station staff at inquiry counter extremely unhelpful and arrogant with travelers."
    ],
    "Coach Maintenance": [
        "Window pane in coach S3 is cracked and cold wind is rushing inside continuously.",
        "Coach roof is leaking water heavily during rain and dripping right on berth 32.",
        "Continuous hammering noise from the wall and loose panels making it impossible to sleep.",
        "Berth chain is broken and upper berth is hanging unsafely in coach S5.",
        "Coach door latch is broken and sliding door is jamming, safety hazard.",
        "Emergency window lock is defective and rattling loudly throughout journey.",
        "Middle berth hinge is damaged and wobbling when passenger climbs up.",
        "Coach exterior window glass is broken and glass shards are falling on passengers.",
        "Toilet door hinges are detached and cannot be closed from inside.",
        "Mechanical noise and coach vibration is severe due to broken carriage suspension."
    ],
    "Medical Assistance": [
        "Passenger is vomiting continuously and suffering from acute dehydration, need doctor at next station.",
        "Fellow passenger having very high fever and breathing difficulty, please provide medical assistance.",
        "Elderly passenger suffered sudden severe chest pain in coach B2, need urgent doctor and stretcher.",
        "A small child in coach S4 is having high fever and convulsions, urgent pediatric medicines needed.",
        "Passenger fell down from berth and suffered bleeding head injury, arrange first aid immediately.",
        "Need anti-vomiting medicine and doctor support in train 12702 for sick family member.",
        "Pregnant lady feeling acute abdominal pain in coach A1, arrange ambulance and doctor at station.",
        "Passenger suffering from severe asthma attack and inhaler is empty, need urgent medical help.",
        "Wheelchair and medical assistance required for disabled passenger at arrival platform.",
        "Dog bite reported at railway station platform, passenger requires rabies injection and dressing."
    ],
    "Engineering": [
        "Track ballast is severely displaced near kilometer 142, track stability looks compromised.",
        "Noticed a visible crack on the rail joint near the bridge approach before station.",
        "Overhead catenary traction wire is hanging loose dangerously close to the rail track.",
        "Severe track vibration and uneven rail alignment noticed on the down line curve.",
        "Railway bridge pillar shows visible structural concrete spalling and cracks under the river bed.",
        "Fishplate bolts appear missing on the outer rail curve near the junction signal.",
        "Signal post foundation has sunk into loose soil, causing signal alignment distortion.",
        "Level crossing gate mechanical barrier gear is jammed and broken, endangering road traffic.",
        "Permanent-way track geometry feels rough and jerking severely on the mainline section.",
        "Embankment soil erosion noticed near railway culvert after heavy rainfall."
    ]
}

results = {}
for category, text_list in samples.items():
    cat_results = []
    dept_name = depts.get(category, "Specialized Department")
    for text in text_list:
        pred_cat = rf.predict([text])[0]
        prob = max(rf.predict_proba([text])[0])
        mapped_dept = depts.get(pred_cat, "General Department")
        cat_results.append({
            "text": text,
            "predicted_category": pred_cat,
            "mapped_department": mapped_dept,
            "confidence": f"{prob*100:.1f}%",
            "matches_target": bool(pred_cat == category)
        })
    results[category] = {
        "department": dept_name,
        "samples": cat_results
    }

with open('data/reports/sample_complaints_by_dept.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print("[+] Generated data/reports/sample_complaints_by_dept.json successfully.")
