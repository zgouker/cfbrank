import requests,pandas
from IPython.display import Image,HTML
import numpy as np

def reindex_from_1(df):
    df2 = df.reset_index(drop=True)
    df2.index = df2.index+1
    return df2

def path_to_image_html(path):
    '''
     This function essentially convert the image url to 
     '<img src="'+ path + '"/>' format. And one can put any
     formatting adjustments to control the height, aspect ratio, size etc.
     within as in the below example. 
    '''

    return '<img src="'+ path + '" style=max-height:20px;"/>'
	
def pull_teams(year):
	year = str(year)
	team_request_get = requests.get(url="https://api.collegefootballdata.com/teams/fbs?year="+year)
	team_df =  pandas.io.json.json_normalize(team_request_get.json())
	fbs_team_df = team_df[team_df.conference.notnull()]
	fbs_team_df.to_csv("data/teams_"+year+".csv")
	fbs_team_df = reindex_from_1(fbs_team_df)
	fbs_team_df.to_csv("data/fbs_teams_long_"+year+".csv")
	fbs_team_df['logo'] = fbs_team_df.logos.apply(lambda x: x[0])
	fbs_team_df['logo']
	fbs_team_df = fbs_team_df[['logo','school','mascot','conference','id']]
	fbs_team_df.to_csv("data/fbs_teams_short_"+year+".csv")
	
def pull_games(year):
	year = str(year)
	game_request_get = requests.get(url="https://api.collegefootballdata.com/games?year="+year+"&seasonType=regular")
	game_df =  pandas.io.json.json_normalize(game_request_get.json())
	fbs_game_df = game_df[game_df.away_conference.notnull()&game_df.home_conference.notnull()&game_df.home_points.notnull()]
	fbs_game_df_short = fbs_game_df[['away_team','away_points','home_team','home_points']]
	fbs_game_df.to_csv("data/fbs_games_short_"+year+".csv")
	
def normalize_dict(d):
    d_max = max(d.values())
    d_min = min(d.values())
    d_range = d_max - d_min
    d_new = d
    for team in d:
        d_new[team] -= d_min
        d_new[team] /= d_range
    return d_new
	
def get_rank(df,team):
    return df.index[df['school'] == team].tolist()[0]

def team_df_html(team_df):
	return HTML(team_df.to_html(escape=False ,formatters=dict(logo=path_to_image_html)))

def build_win_loss_relationships(game_df,wins_dict,losses_dict):
	for index,game in game_df.iterrows():
		if game['home_points']>game['away_points']:
			winning_team = game['home_team']
			losing_team = game['away_team']   
		else:
			winning_team = game['away_team']
			losing_team = game['home_team']
		wins_dict[winning_team].append(losing_team)
		losses_dict[losing_team].append(winning_team)
		
def calculate_scores(score_dict,wins_dict,losses_dict):
	for team in score_dict:
		#print(team)
		for team_defeated in wins_dict[team]:
			score_dict[team] += (len(wins_dict[team_defeated])+1)
			#print("+",team_defeated,(len(wins_dict[team_defeated])+1))
		for team_lost_to in losses_dict[team]:
			score_dict[team] -= (len(losses_dict[team_lost_to])+1)
			#print("-",team_lost_to,(len(losses_dict[team_lost_to])+1))
		#print("*",score_dict[team])

def calculate_records(record_dict,wins_dict,losses_dict):
	for team in wins_dict:
		num_wins = len(wins_dict[team])
		num_losses = len(losses_dict[team])
		record_dict[team] = str(num_wins) + "-" +  str(num_losses)
		
def calculate_best_worst(team_df,score_dict,record_dict,wins_dict,losses_dict,best_win_dict,worst_loss_dict):
	for team in wins_dict:
		if len(wins_dict[team]) == 0:
			best_win_dict[team] = "None"
		else:
			best_score = -99999
			for team_beat in wins_dict[team]:
				if score_dict[team_beat] > best_score:
					best_win_dict[team] = "#" + str(get_rank(team_df, team_beat)) + " " + team_beat + " (" + record_dict[team_beat] + ")"
					best_score = score_dict[team_beat]

	for team in losses_dict:
		if len(losses_dict[team]) == 0:
			worst_loss_dict[team] = "None"
		else:
			worst_score = 99999
			for team_lost_to in losses_dict[team]:
				if score_dict[team_lost_to] < worst_score:
					worst_loss_dict[team] = "#" + str(get_rank(team_df, team_lost_to)) + " " +team_lost_to + " (" + record_dict[team_lost_to] + ")"
					worst_score = score_dict[team_lost_to]
					
def calculate_ranks(year):
	year = str(year)
	game_df = pandas.read_csv("data/fbs_games_short_"+year+".csv")
	team_df = pandas.read_csv("data/fbs_teams_short_"+year+".csv")
	
	wins_dict = {}
	losses_dict = {}
	logo_dict = {}
	score_dict = {}
	second_order_score_dict = {}
	best_win_dict = {}		
	worst_loss_dict = {}
	
	for index,team_row in team_df.iterrows():
		team = team_row['school']
		wins_dict[team]=[]
		losses_dict[team]=[]
		logo_dict[team]=team_row['logo']
		score_dict[team] = 0
		second_order_score_dict[team] = 0
		
	build_win_loss_relationships(game_df,wins_dict,losses_dict)
	calculate_scores(score_dict,wins_dict,losses_dict)
	
	team_df['score'] = team_df['school'].map(score_dict)
	team_df = team_df.sort_values(by='score', ascending=False)
	team_df = reindex_from_1(team_df)
	
	record_dict = {}
	calculate_records(record_dict,wins_dict,losses_dict)
	calculate_best_worst(team_df,score_dict,record_dict,wins_dict,losses_dict,best_win_dict,worst_loss_dict)
					
	team_df['record'] = team_df['school'].map(record_dict)
	team_df['Best Win'] = team_df['school'].map(best_win_dict)
	team_df['Worst Loss'] = team_df['school'].map(worst_loss_dict)
	team_df = team_df[['logo','school','mascot','conference','record','score','Best Win','Worst Loss']]
	
	team_df.to_csv("data/ranks_"+year+".csv")
	
def get_ranks_df(year):
	team_df = pandas.read_csv("data/ranks_"+str(year)+".csv")
	team_df = team_df.loc[:, ~team_df.columns.str.contains('^Unnamed')]
	team_df = reindex_from_1(team_df)
	return team_df
	
def ranks_html(year):
	team_df = get_ranks_df(year)
	return team_df_html(team_df)
	
def pull_and_calculate(year):
	pull_games(year)
	pull_teams(year)
	calculate_ranks(year)