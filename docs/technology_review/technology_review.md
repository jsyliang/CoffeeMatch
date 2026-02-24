# Technology Review: Interactive Python Framework for CoffeeMatch

## 1. Background and Product Motivation

CoffeeMatch is an interactive coffee discovery application designed to help users find Washington-based coffee roasters and products that match their preferences. The system collects structured user inputs (roast level, flavor tags, budget, caffeine preference) and produces ranked recommendations with transparent explanations.

Beyond a simple MVP, the intended product includes:

- An interactive preference quiz  
- Explainable recommendation results  
- Adjustable ranking weights (value vs. popularity vs. flavor match)  
- An admin workflow for submitting new coffee products  
- A reproducible data pipeline (scrape → clean → validate → serve)  
- Potential expansion into roaster directories or local discovery  

This creates a clear technology requirement:

> A Python framework for building interactive, stateful, and maintainable web applications centered around data workflows and recommendation logic.

The chosen framework must:

1. Support structured user input and dynamic output updates  
2. Allow explainable recommendation rendering
4. Be computationally efficient for small-to-medium datasets  
5. Support future expansion (admin workflows, additional views)  
6. Be maintainable by a data science–focused development team  

---

## 2. Candidate Technologies Evaluated

We evaluated two Python dashboard frameworks:

- **Streamlit**
- **Dash (Plotly)**

Both frameworks were installed and used to prototype the same minimal CoffeeMatch workflow.

---

## 2.1 Streamlit

Streamlit is an open-source Python library designed to transform Python scripts into interactive web applications with minimal boilerplate. Its official documentation states that developers can:

> “transform Python scripts into interactive web apps in minutes, instead of weeks. Build dashboards, generate reports, or create chat apps.”  
(https://github.com/streamlit/streamlit/blob/develop/README.md)

Streamlit was co-founded in 2018 by Adrien Treuille, Amanda Kelly, and Thiago Teixeira. In 2022, it was acquired by Snowflake for approximately $800 million. The acquisition was positioned as a strategic move to enhance Snowflake’s data application ecosystem and capitalize on Streamlit’s strengths in data visualization and interactivity.

- Founding discussion: https://discuss.streamlit.io/t/our-35-million-series-b/11647  
- Acquisition coverage: https://techcrunch.com/2022/03/02/snowflake-acquires-streamlit-for-800m-to-help-customers-build-data-based-apps/  

Third-party comparisons (e.g., UI Bakery) suggest that Streamlit is well-suited for:

- Rapid prototyping  
- Fast development cycles  
- Data-focused applications  
- Situations where extensive UI customization is not the primary goal  

### Programming Model

Streamlit follows a script-based rerun model. The application executes from top to bottom and reruns when user input changes. State is managed using `st.session_state`, and performance is improved via built-in caching (`st.cache_data`).

### Observations from Prototyping

- CoffeeMatch was implemented quickly with minimal boilerplate.
- Integrating pandas-based recommendation logic was seamless.
- Adding explanation text and ranking breakdowns was straightforward.
- Admin submission workflows were easy to implement using forms and session state.
- Iterating on scoring logic required minimal structural changes.

---

## 2.2 Dash (Plotly)

Dash is an open-source Python framework developed by Plotly for building analytical web applications. Dash describes itself as:

> “the most downloaded, trusted Python framework for building ML & data science web apps”  
(https://github.com/plotly/dash/blob/dev/README.md)

Dash was originally launched in June 2017 as an open-source visualization framework. It was designed to tie interactive UI elements directly to analytical Python code.

- Introduction article: https://pbpython.com/plotly-dash-intro.html  
- Multi-language support announcement: https://medium.com/plotly/announcing-dash-for-julia-f017c90c6ef1  

Dash supports backends in Python, R, and Julia, and offers both open-source and enterprise versions.

According to third-party comparisons such as UI Bakery, Dash is often recommended for:

- High-traffic applications  
- Applications requiring fine-grained performance optimization  
- Advanced customization and UI control  

### Programming Model

Dash uses a reactive callback architecture. UI components are defined explicitly in a layout, and interactions are handled via Input → Output callback functions. Only components affected by a callback are re-rendered.

### Observations from Prototyping

- Required more boilerplate than Streamlit.
- Recommendation logic integrated cleanly into callback functions.
- Button-driven workflows were well-controlled through callback triggers.
- Multi-step admin flows were structured clearly using callbacks and `dcc.Store`.

---

## 3. Side-by-Side Comparison

We believe both Streamlit and Dash could address our project needs with their function and compatibility. A larger endeavor might demand Dash for computational efficiency though, and both seem to have examples available.


| Criterion | Streamlit | Dash |
|------------|-----------|------|
| Ease of MVP build | Excellent | Moderate |
| Learning curve | Low | Medium |
| Boilerplate overhead | Minimal | Higher |
| Explicit control over triggers | Moderate | Strong |
| Partial UI updates | No (script rerun) | Yes (callback-based) |
| State management | Simple session_state | Explicit via callbacks |
| Admin workflow support | Good | Very Good |
| Deployment simplicity | Very Good | Good |
| Fit for data-centric product | Excellent | Very Good |
| Customization flexibility | Moderate | High |
| High-traffic optimization | Moderate | Strong |

### Open Issues on Github

### Qualitativly (Open Issues)

** Streamlit **
Due to rerun of the script upon interaction procedures like st.cache_resource and st.cache_data seem to provide developers a loophole looking for snappy apps. Occasionally, such workarounds might have unforeseen consequences other places such as “First streamlit widget vanish when used above a @st.fragment that calls a @st.cache_resource function.”.
(https://github.com/streamlit/streamlit/issues/13634)

** Dash **
Some recent bugs listed for dash include quirks with interacting visual effects such as “Dropdown reopens when switching back from another window” & “Slider - Marker overlapped on the slider.” It would be important to keep a look out for these things, but there often seems to be work arounds or fixes.
(https://github.com/plotly/dash/issues/1934)
(https://github.com/plotly/dash/issues/3474)

### Quantiatively (Open Issues)

From the quantitative standpoint, open issues on GitHub suggest the two packages are relatively evenly matched in some of the ways we might use them, with the number of issues marked as “bugs” over the past year about the same for the keywords: buttons, slider, and filter. When we search on the word “pandas,” we can see that although it appears that Streamlit more frequently encounters pandas in issues 729 vs. Dash’s 198, the proportion outstanding for Streamlit is 15% vs. Dash’s 29%. This might suggest that Steamlit is more tested in this important arena. This actually seems consistent with UI Bakery’s comment’s as they highlight “[Streamlit] offers pre-built components and integrations with popular Python libraries like Pandas, NumPy, and Matplotlib” and no comparable plug for dash. But it also could be a result of more frequent entry level users.

** Streamlit **
- 1 ea “bugs” reported regarding “buttons” over the past year 
- 1 ea “bugs” reported over the past year including the word “slider” 
- 0 ea “bug”  reported regarding “filter” over the past year 
- 113 open issues including “pandas” on Dash and 616 closed, means that 15% are outstanding. 
(https://github.com/streamlit/streamlit/issues?q=is%3Aissue%20state%3Aopen%20sort%3Aupdated-desc)

** Dash **
- 2 ea “bugs” reported regarding “buttons” over the past year 
- 1 ea “bugs” reported over the past year including the word “slider” 
- 0 ea “bug”  reported regarding “filter” over the past year 
- 58 open issues including “pandas” on Dash and 140 closed, means that 29% are outstanding.
(https://github.com/plotly/dash/issues?q=is%3Aissue%20state%3Aopen%20sort%3Aupdated-desc)
---

## 4. Final Technology Choice

## 4.1 Final Choice: Streamlit 

**Final Choice: Streamlit**

While Dash offers stronger architectural control and customization, Streamlit better aligns with CoffeeMatch’s product priorities.

CoffeeMatch is fundamentally a **data-driven recommendation product**, where:

- The primary engineering value lies in improving recommendation logic and explainability.
- Iteration speed and maintainability are critical.
- The UI workflow is primarily form → compute → explain → display.
- The dataset scale is small-to-medium and does not require heavy optimization or partial-render control.

Streamlit enables:

- Rapid iteration on ranking weights and scoring logic  
- Seamless integration with pandas-based pipelines  
- Simple implementation of admin workflows  
- Easy addition of evaluation dashboards and analytics  

For the current product scope and foreseeable expansion, Streamlit provides the strongest balance between:

- Development velocity  
- Maintainability  
- Simplicity  
- Sufficient flexibility  

---

## 4.2 Why Not Dash as Final Choice?

Dash is particularly strong for:

- Highly complex multi-component dashboards  
- Large multi-page web applications  
- High levels of traffic and performance tuning  
- Extensive UI customization  

However, for CoffeeMatch:

- Interaction complexity is moderate.  
- Partial rerender optimization is not critical at current scale.  
- The team prioritizes rapid iteration on recommendation logic and data pipeline improvements.  

Dash remains a viable future alternative if CoffeeMatch evolves into a larger multi-user platform requiring greater UI control or traffic scalability.

---

## 5. Areas of Concern and Risk Mitigation

### Scalability

Streamlit reruns the script on interaction, which may become inefficient with very large datasets or heavy concurrent usage.

**Mitigation:**
- Use caching (`st.cache_data`)  
- Keep recommendation logic modular  
- Separate backend services if scaling becomes necessary  

### CSV Write Safety

Appending directly to CSV files may create corruption risks in concurrent environments.

**Mitigation:**
- Use downloadable submission rows for demonstration  
- Store user additions in a separate file (`user_added.csv`)  
- Migrate to SQLite if multi-user writes become necessary  

---

## 6. Conclusion

Both Streamlit and Dash are mature, capable frameworks for building data-centric web applications. After hands-on evaluation, Streamlit was selected as the final framework due to its simplicity, strong alignment with data science workflows, and superior development velocity for this product’s scope.

Dash remains a technically strong alternative, particularly for future expansion requiring higher levels of customization or traffic optimization.
