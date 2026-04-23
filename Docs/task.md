[cite_start]Here is a comprehensive summary, detailed requirements, and a step-by-step execution plan for the **T2.3 Grid Outage Forecaster + Appliance Prioritizer** challenge[cite: 1, 4, 5]. 

### **Executive Summary**
[cite_start]You are tasked with building an actionable AI solution for small businesses (SMEs) like salons, cold rooms, and tailors that suffer from unpredictable power grid outages[cite: 11]. [cite_start]The solution consists of two main parts: a 24-hour probabilistic outage forecaster and an intelligent appliance load-shedding prioritizer[cite: 11, 26]. [cite_start]The final product must be designed for real-world, low-resource settings (low bandwidth, intermittent power, non-smartphone users)[cite: 62]. [cite_start]You have a strict time budget of 180 minutes, with a hard cap of 4 hours[cite: 7].

---

### **Detailed Requirements**

#### **1. Data Creation (Step 1 Focus)**
[cite_start]You must build a reproducible script that generates three synthetic datasets in under 2 minutes on a laptop[cite: 19]. 
* [cite_start]**`grid_history.csv`**: 180 days of hourly data containing timestamps, load (MW), temperature (C), humidity, wind (m/s), rain (mm), an outage flag (0 or 1), and outage duration in minutes[cite: 14, 15]. 
    * [cite_start]*Signal*: Daily load must show morning and evening peaks, weekly seasonality, and rainy-season noise[cite: 20].
    * [cite_start]*Probability Math*: The probability of an outage is calculated as `(a0 + a1*load_lag1 + a2*rain + a3*hour_of_day) + Bernoulli sampler`, with a base rate of 4% per hour[cite: 21, 22].
    * [cite_start]*Duration Math*: Outage duration follows a LogNormal distribution with a mean of 90 minutes and a standard deviation ($\sigma$) of approximately 0.6[cite: 24].
* [cite_start]**`appliances.json`**: A list of 10 typical appliances detailing their name, category (critical, comfort, or luxury), average wattage, startup spike wattage, and the revenue generated per hour if running (in RWF)[cite: 16].
* [cite_start]**`businesses.json`**: Definitions for 3 SME archetypes (salon, cold room, tailor) detailing their specific mix of the defined appliances[cite: 17].




#### **2. Machine Learning & Algorithms**
* [cite_start]**Forecaster (`forecaster.py`)**: Fit a 24-hour-ahead probabilistic model[cite: 26, 36]. [cite_start]You must output both the probability of an outage `P(outage)` and the expected duration `E[duration | outage]` for each hour[cite: 27].
    * [cite_start]*Allowed Models*: Naive Prophet, ARIMA-X, XGBoost on lagged features, or LightGBM[cite: 26].
    * [cite_start]*Evaluation*: Test on a rolling 30-day window using Brier score for the outage probability, Mean Absolute Error (MAE) for duration, and lead time on true outages[cite: 30].
* [cite_start]**Prioritizer (`prioritizer.py`)**: Given the forecast and a business's appliance list, generate a 24-hour schedule determining which appliances should be "ON" or "OFF" each hour[cite: 31, 36]. 
    * [cite_start]*Logic Rule*: You must maximize expected revenue while strictly enforcing the rule to "drop luxury before critical" appliances[cite: 32].





#### **3. Product & Business Adaptation**
[cite_start]This is a critical, highly-weighted requirement (20% of your score) focusing on local context[cite: 97, 98].
* [cite_start]**Morning Digest**: Design an SMS notification for a salon owner[cite: 65]. [cite_start]*Constraint: Maximum of 3 SMS messages, 160 characters each*[cite: 65].
* [cite_start]**Offline Contingency**: Define what the user sees if the internet drops midday and the forecast cannot refresh, including establishing a "maximum staleness" risk budget[cite: 66, 94].
* [cite_start]**Accessibility**: Explain how the output adapts for an illiterate customer (e.g., using voice, icons, or colored LEDs)[cite: 67].

#### **4. Technical Constraints**
* [cite_start]Environment: CPU-only[cite: 59].
* [cite_start]Training time: Less than 10 minutes[cite: 59].
* [cite_start]API Response time: Less than 300 ms on a laptop[cite: 60].

#### **5. Required Deliverables**
* [cite_start]**Code**: `forecaster.py`, `prioritizer.py`, and the data generator script[cite: 36, 50]. 
* [cite_start]**Evaluation**: `eval.ipynb` containing the held-out metrics[cite: 37].
* [cite_start]**UI**: `lite_ui.html` – a static webpage (under 50 KB) that overlays the day's forecast uncertainty band with the appliance plan[cite: 33, 38].
* [cite_start]**Documentation**: `digest_spec.md` (for the SMS design and business adaptations), `process_log.md` (detailing your timeline, LLM usage, and prompts), and a `SIGNED.md` containing the honor code[cite: 39, 40, 55, 105].
* [cite_start]**Video**: A 4-minute presentation hosted online (e.g., YouTube), following a strict timestamped structure demonstrating your code, UI, and answering three specific technical/business questions[cite: 46, 71, 72].

---

### **Execution Plan (No Code)**

Here is a recommended timeline to complete the challenge within the 4-hour limit:

**Hour 1: Data Infrastructure & Baseline Model**
1.  **Script the Data Generator**: Set up your environment and immediately write the Python script to build the synthetic CSV and JSON files following the exact mathematical distributions requested. 
2.  **Sanity Check the Data**: Ensure the generated CSV has 180 days of hourly data and the 4% base rate with daily peaks is visible.
3.  **Build the Forecaster**: Select your model (e.g., LightGBM or XGBoost for speed). Set up the 30-day rolling evaluation and train the model to output the required `P(outage)` and `E[duration]`.

**Hour 2: Prioritization Logic & Evaluation**
1.  **Draft the Prioritizer Algorithm**: Build the logic that ingests the JSON business/appliance data and the forecast. 
2.  **Implement the Optimization**: Write the function that cycles through the 24-hour forecast, calculates expected available power vs. outage risk, and toggles appliances ON/OFF. Ensure "luxury" items are always shed before "critical" ones.
3.  **Calculate Revenue Saved**: Build the required logic to compare your plan's preserved revenue against a naive "always-on" approach.
4.  **Finalize `eval.ipynb`**: Run the rolling metrics (Brier, MAE) and document them.

**Hour 3: UI, Product Adaptation, & Documentation**
1.  **Develop the Lite UI**: Create the static 50 KB HTML file. Use simple libraries or native JS/Canvas to graph the forecast uncertainty band and overlay the ON/OFF blocks for the appliances.
2.  **Write `digest_spec.md`**: Draft the 3 constrained SMS messages. Detail your strategy for offline staleness and illiteracy accessibility.
3.  **Complete the Admin Files**: Fill out your `process_log.md` with your logged LLM prompts. Create the `SIGNED.md` honor code file.

**Hour 4: Rehearsal, Recording, & Submission**
1.  **Prepare for the Video**: Set up your terminal, code files, and browser with `lite_ui.html` side-by-side.
2.  **Record the 4-Minute Video**: Strictly follow the prompt's timeline:
    * *0:00-0:30*: Face-camera intro + Brier score.
    * *0:30-1:30*: Screen-share code walk of forecaster/prioritizer.
    * *1:30-2:30*: Demo the `lite_ui.html`.
    * *2:30-3:30*: Read the SMS digest.
    * *3:30-4:00*: Answer the three specific questions regarding the worst forecast hour, RWF saved, and the offline contingency. 
3.  **Final Commit**: Push everything to your public GitHub/GitLab, host the video, and verify all checklist items are complete.