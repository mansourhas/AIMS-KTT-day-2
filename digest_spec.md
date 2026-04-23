# Product & Business Adaptation Specification (digest_spec.md)

## 1. Morning Digest: Salon Owner (Feature Phone)
[cite_start]**Constraint Checklist & Confidence Score:** 3 SMS max, 160 characters per SMS[cite: 65]. 

This digest is sent to the salon owner at 07:00 AM to help them plan client appointments around expected grid stability.

**SMS 1: The Forecast (136 / 160 chars)**
> AIMS Power Alert: High risk of outage today from 18:00-20:00 (peak 95% at 19:00). Expected duration: ~2 hrs. Morning & afternoon safe.

**SMS 2: The Action Plan (142 / 160 chars)**
> Salon Plan: Unplug Blow Dryer & Water Heater at 18:00. Keep Clippers & LED Lights ON to finish haircuts. Hair Dryer off-limits until 20:00.

**SMS 3: The Business Value (128 / 160 chars)**
> Following this plan saves ~4,500 RWF today vs. grid trip/shutdown. Reply '1' to acknowledge. Next update at 13:00 if needed.


---

## 2. Offline Protocol & Staleness Risk Budget
[cite_start]**Scenario:** The salon's internet connection drops at 13:00, preventing the afternoon forecast refresh[cite: 66, 94].

* **What the Device Shows:** * The `lite_ui.html` dashboard features a "Last Synced" timestamp.
    * After 2 hours without internet, the timestamp text turns **orange**.
    * After 6 hours without internet, a banner appears stating: *"⚠️ Offline Mode: Showing defensive schedule."*
* **The Risk Budget (Maximum Staleness):**
    * I accept a maximum forecast staleness of **6 hours** before I stop trusting the precise hourly plan. 
    * **Why:** Weather (specifically `rain_mm`) heavily influences outages in our model. Rain fronts can move and develop rapidly over a 6-hour window.
    * **Fallback Behavior:** After 6 hours offline, the prioritizer reverts to a "Defensive Heuristic." It abandons the dynamic ML forecast and automatically enforces load-shedding of all "Luxury" and "Comfort" appliances during historical peak grid stress hours (18:00 - 21:00) to protect the salon's critical equipment from unexpected surges.

---

## 3. Accessibility & Illiteracy Adaptation
[cite_start]To ensure the solution is actionable for users who cannot read text or interpret probability charts, the system relies on physical and visual cues[cite: 67].

* **Visual Icons (lite_ui.html):** The web dashboard strips away complex text and replaces appliance names with highly recognizable emojis (💇‍♀️ for Hair Dryer, ✂️ for Clippers, 🧊 for Fridge). Status is indicated by universally understood color codes (🟢 for ON, 🔴 for OFF).
* **Hardware Integration (Colored LEDs):** The ultimate deployment target pairs the prioritizer with a cheap ESP32 relay board. Next to each heavy appliance's wall socket, a simple LED indicator dictates action:
    * **Green LED:** Safe to use.
    * **Red LED:** High outage risk, turn off immediately.
* **Audio Alternative (IVR/Voice):** For feature-phone users who cannot read the morning SMS, the daily digest triggers an automated IVR (Interactive Voice Response) phone call. A local-language text-to-speech voice explicitly states: *"Good morning. Please turn off your Hair Dryer at 6 PM today."*