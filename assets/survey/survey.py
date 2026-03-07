"""This script summarizes information from surveys for our presentation.
It creates three seaborn charts after creating aggregating long-files via
pivot type tables. """

import os

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#remove prior files
NEW=0
try:
    os.remove("all_factors_selection.png")
# pylint: disable=W0702
except:
    NEW=NEW+1

try:
    os.remove("top3_factors_selection.png")
# pylint: disable=W0702
except:
    NEW=NEW+1

try:
    os.remove("optional_survey_questions_preference.png")
# pylint: disable=W0702
except:
    NEW=NEW+1

def chart_list(dataframe):
    """This function takes the groupby output of drink_frequency_binary
    on rows and survey questions as columns and shifts to a list format
    to create a bar plot, returning a list"""
    row = []
    rows = []
    count=0
    for j, name in enumerate(dataframe.columns):
        for i in range(0, len(dataframe)):
            count=count+1
            #remove drink_frequency_binary indicator rows (first two)
            if count > 2:
                if dataframe.iloc[i,0]==0:
                    drinker_type='drinking coffee less than daily'
                else:
                    drinker_type='drinking coffee daily'
                row = (drinker_type, dataframe.iloc[i,j], name)
                rows.append(row)
    df_out = pd.DataFrame(rows, columns=["drink_frequency_binary",
                                         "mean_response", "category"])
    return df_out

df = pd.read_csv("classmate_survey.csv", sep = ",")

#Firstchart of survey where particpants can select unlimited factors
#remove these fields since they won't be aggregated
df_1=df.drop(columns=['record_no','drink_frequency', 'roast_level', 'price',
                      'bean_origin', 'locality_of_roaster', 'decaf_ava',
                      'ground', 'user_comments', 'user_reviews_stars',
                      'organic_ava', 'certification_labels',
                      'top3_roast_level', 'top3_price', 'top3_bean_origin',
                      'top3_locality_of_roaster','top3_decaf_ava',
                      'top3_ground','top3_user_comments',
                      'top3_user_reviews_stars', 'top3_organic_ava',
                      'top3_certification_labels', 'no_binary_selections'])

#create new pivot for chart
chart_df1 = df_1.groupby(['drink_frequency_binary']).agg('mean')
chart_df1 = chart_df1.reset_index()
chart_df1=chart_df1.sort_values(1, axis=1, ascending=False)
chart_df1=chart_df1.sort_values('drink_frequency_binary', axis=0, ascending=0)

#chart
chart_df1b=chart_list(chart_df1)
fig_a = plt.figure()
ax_a = fig_a.add_subplot()
sns.barplot(chart_df1b, y="category", x="mean_response",
               hue="drink_frequency_binary", orient="h",
               palette=['#1657bd','#40e3d0'])
plt.title("All factors available for selection")
plt.tight_layout()
ax_a.set(ylabel=None)
ax_a.set_xlim(0,1)
fig_a.savefig("all_factors_selection.png")
#help from
#https://www.figma.com/color-wheel/
#https://stackoverflow.com/questions/63756623
#https://stackoverflow.com/questions/34162443
#https://seaborn.pydata.org/generated/seaborn.barplot.html

#Second chart of survey where only top3 coffee factors can be chosen
#remove theese fields since they won't be aggregated
df_2=df.drop(columns=['record_no','drink_frequency', 'roast_level', 'price',
                      'bean_origin', 'locality_of_roaster', 'decaf_ava',
                      'ground', 'user_comments', 'user_reviews_stars',
                      'organic_ava', 'certification_labels',
                      'binary_roast_level','binary_price','binary_bean_origin',
                      'binary_locality_of_roaster','binary_decaf_ava',
                      'binary_ground','binary_user_comments',
                      'binary_user_reviews_stars','binary_organic_ava',
                      'binary_certification_labels', 'no_binary_selections'])

#create new pivot for chart
chart_df2 = df_2.groupby(['drink_frequency_binary']).agg('mean')
chart_df2 = chart_df2.reset_index()
chart_df2=chart_df2.sort_values(1, axis=1, ascending=False)
chart_df2=chart_df2.sort_values('drink_frequency_binary', axis=0, ascending=0)

#chart
chart_df2b=chart_list(chart_df2)
fig_b = plt.figure()
ax_b = fig_b.add_subplot()
sns.barplot(chart_df2b, y="category", x="mean_response",
                hue="drink_frequency_binary", orient="h",
                palette=['#1657bd','#40e3d0'])
plt.title("Factors when prioritized in top3")
plt.tight_layout()
ax_b.set(ylabel=None)
ax_b.set_xlim(0,1)
fig_b.savefig('top3_factors_selection.png')

#Third chart where proportion of optional questions compared to drinking.
#new pivot
chart_df3 = df.groupby(['no_binary_selections']).agg({'drink_frequency_binary':
                                                      'mean'})
#chart
chart_df3 = chart_df3.reset_index()
fig_c = plt.figure()
ax_c = fig_c.add_subplot()
sns.barplot(chart_df3, y="drink_frequency_binary",
                x="no_binary_selections", hue=1, palette=['#1657bd'],
                legend=False)
plt.title("Elected responses (qty) vs proportion drinking coffee daily")
ax_c.set(xlabel=None, ylabel=None)
fig_c.savefig('optional_survey_questions_preference.png')
print(3," charts made ",3-NEW," charts replaced")
