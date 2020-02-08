import requests,pandas

def reindex_from_1(df):
    df2 = df.reset_index(drop=True)
    df2.index = df2.index+1
    return df2
	
def pull_teams(year):
	team_request_get = requests.get(url="https://api.collegefootballdata.com/teams?year="+year)
	team_df =  pandas.io.json.json_normalize(team_request_get.json())
	fbs_team_df = team_df[team_df.conference.notnull()]
	fbs_team_df.to_csv("data/teams_"+year+".csv")
	fbs_team_df = reindex_from_1(fbs_team_df)
	fbs_team_df.to_csv("data/fbs_teams_long_"+season+".csv")
	fbs_team_df['logo'] = fbs_team_df.logos.apply(lambda x: x[0])
	fbs_team_df['logo']
	fbs_team_df = fbs_team_df[['logo','school','mascot','conference','id']]
	fbs_team_df.to_csv("data/fbs_teams_short_"+season+".csv")
	
def pull_games(year):
	game_request_get = requests.get(url="https://api.collegefootballdata.com/games?year="+year+"&seasonType=regular")
	game_df =  pandas.io.json.json_normalize(game_request_get.json())
	fbs_game_df = game_df[game_df.away_conference.notnull()&game_df.home_conference.notnull()&game_df.home_points.notnull()]
	fbs_game_df_short = fbs_game_df[['away_team','away_points','home_team','home_points']]
	fbs_game_df.to_csv("data/fbs_games_short"+year+".csv")