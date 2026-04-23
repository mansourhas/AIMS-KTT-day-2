# Time log:
- [10:00 - 10:25] setting up the project and reading the doc.
- [10:30 - 11:50] trying to find the best models. 
- [12:15 - 12:50] refactored forecast and prioritization for best software engineering practicies.
- [1:12 - ] pracrice for recodring.


# AI usage Log:
I'm using gemini fast and pro chat interface for Questions, Ideation and Coding. also i'm planning to use codex for coding tasks. 

## [sample 1] 
i used gemini to create a todo list for me to make sure i'm not missing any mildstone within the task. 

the prompt: `summarize and detail rquirments and plan to do this, the data creation should be first step, don't give any code for now, just details`

the results are here, https://gemini.google.com/share/666379cb628f
and also i'm adding it to tasks.md

## [Sample 2]
This shows the AI tendensy to give me full code with low quality and how i'm trying to improve the qulaiyt.

This conversation contain all the discrion with ai to build the code:
https://gemini.google.com/share/b5535c9ab0fa


## [Sample 3]
Ideation and verfication what have i missed about the project, and where can i improve my ratings.
prompt (with all my code files as context):`give me exact tips for best video recording experiance, i want the judges to see my techniqual ability and how my decision making thinking is`

respond:```Highlighting Your Decision-Making ProcessThe judges want to see why you built it this way. Embed your decision-making directly into the 3 mandatory questions:Question 1 (Technical - Worst Forecast): When asked about the hour with the worst forecast, be honest. Point to a specific feature (like rain_lag1 vs rain_rolling_6h) that missed a sudden spike, and explain what feature engineering you would add next week to fix it. You can also mention your deliberate choice to use LightGBM instead of ARIMA due to auto-tool context limitations, as you noted in your process_log.md.Question 2 (Business - RWF Math): When calculating the RWF saved on camera, have the math pre-computed but explain the logic. Show that you understand the financial impact of letting a 95% outage risk trip the system versus proactively shedding the blow dryer.Question 3 (Local Context - Staleness): When explaining what happens if the internet drops at 13:00, confidently cite your offline protocol. Explain the 6-hour maximum staleness rule and why it exists (e.g., weather fronts moving rapidly), and describe how the UI timestamp turns orange to warn the non-literate user before reverting to the defensive fallback schedule.3. Recording Best PracticesBoost Font Sizes: Before you hit record, bump up the font size in your IDE and your terminal. If the judges can't read your terminal output during the live demo, it doesn't count.Smooth Transitions: Have forecaster.py, prioritizer.py, your terminal, your browser (lite_ui.html), and digest_spec.md already open in different tabs or neatly arranged windows. You do not have time to be hunting for files.Own the AI Usage: If you stumble, don't panic. The judges know you used AI (you've signed the honor code and submitted your process_log.md ). What matters is your ability to debug, navigate, and justify the code that is on the screen right in front of you.```

# Hardest decision i made:

- i wish i could have explored explainable simple models like AREMA (in my experiance Auto-tools are bad at captiaring the cotext of the problem), but setting the paramters right will take time ( update: very late in the challange my intution is telling me AREMA for synthatic data is easy). and will require developing complete different pipeline, so i decided to stick with the gboost familiy and do grid search and focuse on accuracy.

