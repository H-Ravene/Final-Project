#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# In this jupyter notebook we will be using statstical data over the period 2011-2016 to determine whether we can show that one league is "better" than the other.
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')
from bokeh.charts import BoxPlot, show
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import Range1d
from bokeh.palettes import brewer
#We are importing Overall Player Rating, Player Potential Rating, and Player Free Kick Accuracy from our SQLite database
database = '/Users/Herve/Downloads/database.sqlite'
con = sqlite3.connect(database)
#Our data is spread out over the database so many joins were necessary to link players to leagues, teams, and match data.
data = '''SELECT p.player_name, t.team_long_name, l.name,
            pa.overall_rating, pa.potential, pa.free_kick_accuracy, m.season
            FROM Player_Attributes pa
            JOIN Player p
            ON pa.player_api_id = p.player_api_id
            JOIN Match m
            ON (p.player_api_id = m.away_player_1 OR p.player_api_id = m.away_player_2
            OR p.player_api_id = m.away_player_3 OR p.player_api_id = m.away_player_4 
            OR p.player_api_id = m.away_player_5 OR p.player_api_id = m.away_player_6 
            OR p.player_api_id = m.away_player_7 OR p.player_api_id = m.away_player_8 
            OR p.player_api_id = m.away_player_9 OR p.player_api_id = m.away_player_10 
            OR p.player_api_id =  m.away_player_11)
            JOIN League l
            ON m.league_id = l.id
            JOIN Team t
            ON m.away_team_api_id = t.team_api_id
            WHERE (m.season = '2015/2016' OR m.season = '2014/2015' OR m.season = '2013/2014' 
            OR m.season = '2012/2013' OR m.season = '2011/2012')
            AND (l.name = 'Germany 1. Bundesliga' OR l.name = 'England Premier League')
            '''

df = pd.read_sql_query(data, con=con).drop_duplicates()
df.head()
#We are going to clean up the dataframe.
cols = ['Player', 'Team', 'League', 'Overall_Rating', 'Potential', 'Free_Kick_Accuracy', 'Season']
df_teams = df.copy()
df_teams.columns = cols
df_teams = df_teams.groupby(['League', 'Season','Team']).mean().reset_index(drop=False)
df_teams['Year'] = df_teams.Season.str[:4].apply(int)
df_teams.head(10)

#A column is calculated to see how well each team is "living up to their potential". 
per_dif = (((df_teams['Potential'] - df_teams['Overall_Rating'])/df_teams['Potential'])*100).round(2)
df_teams['Rating_vs_Potential'] = per_dif
df_teams.head()
#Since there are always "bad" teams in a league, we wanted to see if there's a difference in player quality for the top teams of each league each year
epl_only = (df_teams.League == 'England Premier League')
bl_only = (df_teams.League == 'Germany 1. Bundesliga')

epl = df_teams[epl_only].groupby(['Year','League','Team','Potential','Free_Kick_Accuracy','Rating_vs_Potential']).mean().Overall_Rating.groupby(level=0, group_keys=False).nlargest(3).reset_index(drop=False)
bl = df_teams[bl_only].groupby(['Year','League','Team','Potential','Free_Kick_Accuracy', 'Rating_vs_Potential']).mean().Overall_Rating.groupby(level=0, group_keys=False).nlargest(3).reset_index(drop=False)

top_teams = [epl, bl]
top3 = pd.concat(top_teams)

top3.head(30)
#We are going to create a chart to determine which league has the better players
sns.set_style("darkgrid")
sns.pointplot(x="Year", y="Overall_Rating", hue='League', palette='Blues_d',data=df_teams[epl_only])
sns.pointplot(x="Year", y="Overall_Rating", hue='League', palette='Reds_d',data=df_teams[bl_only])
#We are getting another look at the same data from above, but shown with boxplots to illustrate the range of scores better. 
palette = brewer['Dark2'][4]
output_notebook()
bottom, top = 65, 85
b = BoxPlot(df_teams, 
            values='Overall_Rating', 
            label=['Year','League'],
            color='League', 
            legend=None, 
            title='Annual Player Overall Ratings',
            width=1000,
           palette=palette)
b.y_range = Range1d(bottom, top)
show(b,notebook_handle=True)
#We are now comparing the best teams in each league
sns.set_style("darkgrid")
sns.pointplot(x="Year", y="Overall_Rating", hue='Team', palette='Blues_d',data=epl)
sns.pointplot(x="Year", y="Overall_Rating", hue='Team', palette='Reds_d',data=bl)
plt.legend(loc='center left', bbox_to_anchor=(1,0.5))
#We are now trying to determine how wide the gab is between Player Overall Rating and Player Potential between the two leagues
sns.pointplot(x="Year", y="Rating_vs_Potential",hue='League', palette='Blues_d',agg='max', data=df_teams[epl_only])
sns.pointplot(x="Year", y="Rating_vs_Potential",hue='League', palette='Reds_d', agg='max,', data=df_teams[bl_only])

