# RailAssist AI — Dataset Label Mapping & Inspection Report

**Generated on:** 2026-10-25 | **Dataset:** `faizmubeen/indian_railways_complaint_tweets` (Revision `f2a3e5f`)
**License:** MIT | **Raw Records:** 4,535 (Complaint: 2,615, Non-Complaint: 1,920)

## 1. Executive Summary
This document establishes the verified, deterministic mapping between the original user labels (`Type`) in the Hugging Face dataset and the **ten target railway complaint categories** defined for the RailAssist AI system.
To maintain scientific integrity:
- Non-complaint tweets (1,920 records) are excluded from the supervised complaint classifier.
- Vague catch-all labels (`service`, `facility`, `miscellaneous`, `others`, `political`) are excluded to prevent label noise and avoid turning `Passenger Grievance` into an indiscriminate dumping ground.
- **Engineering** contains **0 valid complaint records** in this public dataset; it is formally documented as **Unsupported** rather than fabricating synthetic data.
- **Medical Assistance** contains only **11 genuine complaint records** (0.6% of training data); it is acknowledged as an **Insufficient Data** category.
- After deduplication of 2 duplicate records, **1,949 verified complaint records** form the cleaned supervised training dataset across 9 active categories.

## 2. Category Mapping & Distribution Table
| Target Category | Mapped Railway Department | Raw Types Mapped | Raw Complaint Count | Deduplicated Count | Share (%) | Status |
|---|---|---|---|---|---|---|
| **Operations & Traffic** | Operating Department (Traffic & Scheduling) | `punctuality`<br>`train delay`<br>`cancelled train`<br>`delay` | 787 | 785 | 40.3% | **Supported** |
| **Passenger Grievance** | Commercial Department (Public Grievance Cell) | `corruption / bribery`<br>`staff behaviour`<br>`crowding`<br>`ticket booking`<br>`refund`<br>`ticket booking charge`<br>`ticket/ seat availability`<br>`difficulty in booking tickets`<br>`fare charges` | 406 | 401 | 20.6% | **Supported** |
| **Housekeeping** | Environment & Housekeeping Management (EnHM) / OBHS | `cleanliness`<br>`bed roll` | 329 | 328 | 16.8% | **Supported** |
| **Security** | Security Department (Railway Protection Force - RPF) | `security`<br>`safety` | 142 | 141 | 7.2% | **Supported** |
| **Electrical** | Electrical Engineering Department (Train Lighting & AC) | `electrical equipment` | 95 | 95 | 4.9% | **Supported** |
| **Catering** | Catering & Vending Services Department (IRCTC / Commercial) | `catering & vending service`<br>`food`<br>`food quality` | 88 | 88 | 4.5% | **Supported** |
| **Coach Maintenance** | Mechanical Engineering Department (Carriage & Wagon - C&W) | `maintenance`<br>`poor condition`<br>`bed` | 66 | 66 | 3.4% | **Supported** |
| **Water & Sanitation** | Water Supply & Sanitation Department | `water availability` | 45 | 45 | 2.3% | **Supported** |
| **Total** | | | **1,958** | **1,949** | **100.0%** | |

## 3. Detailed Mapping Rationale & Actual Representative Examples

### Operations & Traffic
- **Assigned Department:** Operating Department (Traffic & Scheduling)
- **Scope Definition:** Train delays, schedule disruptions, punctuality problems, unscheduled crossings, and train cancellations.
- **Original Raw Labels Mapped:** `punctuality`, `train delay`, `cancelled train`, `delay`
- **Representative Verified Dataset Examples:**
  1. *(Raw Type: `punctuality`)* "Balurghat is suffering from unnecessary late of the following train (13161) continuously. #IndianRailways is incessantly ignoring the sufferings. How does a train take 7 hours for 350 kms & almost 5 h..."
  2. *(Raw Type: `punctuality`)* "#IndianRailways 02563 BJU NDLS Running late by 4:30 hrs , bad service . I am in this train and I need to recieve my wife and Kid from Nizamuddin station at 9:55 am ...."
  3. *(Raw Type: `punctuality`)* "Thinking of whether it is passenger train or expressÃ°Å ̧â„¢â€ž....#Lalbagh 12607 (Nov25,2022) 15:30pm departure from Chn---Bang.... its take 1:30 hours to reach Arakonam junctionÃ°Å ̧Â¤Â·Ã°Å ̧ÂÂ»Ã¢â..."

### Passenger Grievance
- **Assigned Department:** Commercial Department (Public Grievance Cell)
- **Scope Definition:** Staff misbehaviour, corruption or bribery demands by ticket examiners, unauthorized overcrowding in reserved coaches, ticketing booking failures, and refund disputes.
- **Original Raw Labels Mapped:** `corruption / bribery`, `staff behaviour`, `crowding`, `ticket booking`, `refund`, `ticket booking charge`, `ticket/ seat availability`, `difficulty in booking tickets`, `fare charges`
- **Representative Verified Dataset Examples:**
  1. *(Raw Type: `ticket booking`)* "#UTS app wants me to be away at certain distance from railway station to book ticket If I want to switch trains like from a sf express to MMTS it's hard to go out of station for booking @amofficialCRI..."
  2. *(Raw Type: `ticket booking`)* "Sir, this is the condition of ticket booking counter, Guwahati Railway Station.The working hour of evening start from 2:15 pm to 8:00 pm but there is no person on the counter. #IndianRailways #indianr..."
  3. *(Raw Type: `corruption / bribery`)* "There are no general tickets for common public in #IndianRailways from Tatanagar to Howrah Junction. Where TTE's are booking tickets inside the platform illegally and asking for extra fare...What is t..."

### Housekeeping
- **Assigned Department:** Environment & Housekeeping Management (EnHM) / OBHS
- **Scope Definition:** Coach cleanliness, dirty toilets, foul smell, pest/cockroach infestations, garbage disposal, and soiled/torn bedrolls and linen.
- **Original Raw Labels Mapped:** `cleanliness`, `bed roll`
- **Representative Verified Dataset Examples:**
  1. *(Raw Type: `cleanliness`)* "My parents travelled by #garibrath train from Raipur to Lucknow after 3 years and were extremely disgusted by the state of #biotoilets We have travelled by garib rath so many times earlier but never s..."
  2. *(Raw Type: `cleanliness`)* "Stopped travelling in #IndianRailways way back... It stinks right from the Sec station all the way thru the boarding station with garbage allover the trains n shit all over the toilets ðŸ¤®ðŸ¤®ðŸ¤®ðŸ¤..."
  3. *(Raw Type: `bed roll`)* "@IRCTCofficial I am travelling from bangalore to Mumbai train no. 11302 Coach no. M1, PNR -4760399048 the bed sheet given was not clean and full of wrinkles as itÃ¢â‚¬â„¢s used #hygiene #issue #notcle..."

### Security
- **Assigned Department:** Security Department (Railway Protection Force - RPF)
- **Scope Definition:** Theft of luggage and valuables, harassment, safety threats, unauthorized persons entering compartments, and calls for RPF intervention.
- **Original Raw Labels Mapped:** `security`, `safety`
- **Representative Verified Dataset Examples:**
  1. *(Raw Type: `security`)* "My old parents are currently travelling in this train from LTT to GHY. There's been some issues with their Co-passengers and the TC is nowhere to be found nor any RPF personnel. Please Help! @IRCTCoff..."
  2. *(Raw Type: `security`)* "Why railway is not taking action regarding these types of disturbances in trains .from morning to night they start chanting and they won't care about there fellow passengers. #IndianRailways #RPF #min..."
  3. *(Raw Type: `security`)* "HELP! Laptop Backpack with Belongings worth Rs.1,72,799 was stolen from LUR-YPR EXP Tr.no16584 on 21/08/2022.PNR8656030784, Seat24,A2.Second AC Makes me question how safe #IndianRailways is for the co..."

### Electrical
- **Assigned Department:** Electrical Engineering Department (Train Lighting & AC)
- **Scope Definition:** Air conditioning non-cooling or failure, non-functional fans, lights off/fused, and defective mobile charging sockets.
- **Original Raw Labels Mapped:** `electrical equipment`
- **Representative Verified Dataset Examples:**
  1. *(Raw Type: `electrical equipment`)* "@RailMinIndia Today my father (@LalitBi57894984 ) travelled in train no.15044 from Haldwani to Lucknowin Chair Car but no AC was working at all. Everyone sweated even after paying for AC Chair Car & t..."
  2. *(Raw Type: `electrical equipment`)* "I'm travelling in SDAH-KANCHANJUNGHA Express(13174)from guwahati in S6 coach.There is no provision of mobile charging in this coach.The journey will end tomorrow night. How all the people manage this...."
  3. *(Raw Type: `electrical equipment`)* "#IndianRailways #Railway Ministry, Travelling from DDU to Ajmer from Sialdah super fast train (12987) ..Third ac coach no B-6 ac is not working Last more than one hour , no technician is avilable, wor..."

### Catering
- **Assigned Department:** Catering & Vending Services Department (IRCTC / Commercial)
- **Scope Definition:** Food quality, unhygienic pantry cars, overcharging for meals, missing meals, stale snacks, and poor beverage services.
- **Original Raw Labels Mapped:** `catering & vending service`, `food`, `food quality`
- **Representative Verified Dataset Examples:**
  1. *(Raw Type: `catering & vending service`)* "#IndianRailways today I am suffering from New Delhi to Pryagraj in Rajdhani with PNR no 2154364195 train no is 22812 BBS Rajdhani with sheat no B5 50 middle birth I want to say that breakfast has not ..."
  2. *(Raw Type: `catering & vending service`)* "@Central_Railway @AshwiniVaishnaw @PMOIndia I request indian railway stop giving food in rails, worst food ever eat, donâ€TMt make fool of public in name of food, at least they can take from home #wor..."
  3. *(Raw Type: `food`)* "It was very disappointing last night to receive dinner from IRCTC, was booked using IRCTC App. Order no. 85739712. Food was rotten and we had to throw in bin. Starved through night with kids. Please p..."

### Coach Maintenance
- **Assigned Department:** Mechanical Engineering Department (Carriage & Wagon - C&W)
- **Scope Definition:** Physical coach damage, broken window panes, leaking coach roofs, damaged berths, loose latches, and structural rattles.
- **Original Raw Labels Mapped:** `maintenance`, `poor condition`, `bed`
- **Representative Verified Dataset Examples:**
  1. *(Raw Type: `maintenance`)* "Ndls to amritsar shatabadi 12029 air conditioning is not working from last one hour in C10 coach... People are feeling suffocated and kids are feeling very uneasy. Please get it rectified on an urgent..."
  2. *(Raw Type: `maintenance`)* "Travelled from Ahmedabad to Mumbai by #GujaratMail 12902 today in B2, seat 70. There's a constant hammering noise from the wall making sure that you don't sleep and don't miss your station.This needs ..."
  3. *(Raw Type: `maintenance`)* "Train no. 16585 SBC MAQ EXP, S7 coach, there is water leak and water dripping from the roof #indianrailways Ã¢Â¦@RailwaySevaÃ¢Â© Ã¢Â¦@RailMinIndiaÃ¢Â©, please resolve the issue. Thank you..."

### Water & Sanitation
- **Assigned Department:** Water Supply & Sanitation Department
- **Scope Definition:** Unavailability of water in coach washrooms, empty train water tanks, dry washbasins, and platform water tap failures.
- **Original Raw Labels Mapped:** `water availability`
- **Representative Verified Dataset Examples:**
  1. *(Raw Type: `water availability`)* "No water in Coach S6, S8 in 12174 Udyog Nagari Express from Partapgarh-Lokmanya Tilak Terminus. Passengers inconvenienced and unable to use washroom for toilet. Request @IRCTCofficial @RailwayNorthern..."
  2. *(Raw Type: `water availability`)* "@IRCTCofficial train no 22537 which departed on 16th of june from Gorakhpur to LTT (KUSHINAGAR EXP) doesn't have water in toilet.. its a basic need! Can you please resolve the issue ASAP. #IndianRailw..."
  3. *(Raw Type: `water availability`)* "Train number 22404 Ac3 running from 15th May B6 passengers are suffering due to unavailability of water in toilet. No one ready to listen problem.PNR 2140201165 #ashwinivaishnaw #IndianRailways..."

## 4. Excluded Labels and Justification
To ensure that the ML classifier learns reliable boundaries, ambiguous labels and non-complaints are systematically excluded rather than forcibly mislabeled:

| Original Label (`Type`) | Total Count | Complaint Count | Primary Reason for Exclusion |
|---|---|---|---|
| `medical assistance` | 27 | 11 | Excluded due to severe sample scarcity (only 11 genuine complaints in dataset; 0.6% representation) to maintain statistical evaluation rigor across fully-supported categories. |
| `engineering` | 0 | 0 | Excluded because 0 civil engineering complaint records exist in the source dataset. |
| `service` | 198 | 180 | Vague, highly diffuse complaints spanning policy, platform signs, or general customer support without specific domain clarity. |
| `miscellaneous` | 240 | 177 | Catch-all label containing noisy, multi-topic, or idiosyncratic grievances that lack coherent semantic boundaries. |
| `facility` | 196 | 142 | Generic observations about station waiting rooms or multi-service deficiencies without distinct operational target. |
| `others` | 414 | 68 | Unspecified feedback, meme references, and social commentary. |
| `political` | 55 | 52 | Political arguments, ministry criticism, senior citizen concession policy debates, and government privatization debates. |
| `loss/found` | 15 | 14 | Inquiries regarding misplaced personal items rather than service complaints. |
| `facilities` | 4 | 3 | Vague infrastructure remarks lacking department-specific resolution. |
| `service feedback` | 4 | 1 | Generic non-actionable commentary. |
| `service quality` | 4 | 1 | Single generic remark. |
| `service issue` | 2 | 1 | Single generic remark. |
| `logistics` | 1 | 1 | Freight/parcel handling query. |
| `child labor and begging on train` | 1 | 1 | Single isolated social issue record. |
| `opposition to the silverline project and ecological impact` | 1 | 1 | Political / ecological policy commentary. |
| `petrol theft during vehicle parceling` | 1 | 1 | Isolated parcel theft claim. |
| `criticism` | 1 | 1 | Generic political / institutional critique. |
| `request/suggestion` | 1 | 1 | User suggestions rather than actionable complaints. |
| `employee` | 1 | 1 | Internal HR dispute. |
| `non_complaint` (Label column) | 1,920 | 0 | Non-grievance messages (news, train photos, general appreciation) excluded from complaint classifier. |

## 5. Auditability and Pre-Training Sign-Off
- **Raw Source Preserved:** `data/raw/inidian_railway_complaint_tweets.csv` remains unmodified.
- **Cleaned Output Target:** `data/processed/cleaned_complaints.csv` with original provenance retained.
- **Deterministic Department Logic:** Defined in `data/category_mapping.json` and mirrored in `backend/app/category_mapping.json`.
- **Integrity Affirmation:** No synthetic data will be introduced for Engineering or Medical Assistance. Limitations are openly communicated in frontend and backend documentation.
