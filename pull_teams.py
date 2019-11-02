import requests,pandas
def reindex_from_1(df):
    df2 = df.reset_index(drop=True)
    df2.index = df2.index+1
    return df2
	
team_request_get = requests.get(url="https://api.collegefootballdata.com/teams?year=2019")
team_df =  pandas.io.json.json_normalize(team_request_get.json())
fbs_team_df = team_df[team_df.conference.notnull()]
fbs_team_df.to_csv("teams.csv")
fbs_team_df = reindex_from_1(fbs_team_df)
fbs_team_df.to_csv("fbs_teams_long.csv")
fbs_team_df['logo'] = fbs_team_df.logos.apply(lambda x: x[0])
fbs_team_df['logo']
fbs_team_df = fbs_team_df[['logo','school','mascot','conference','id']]
fbs_team_df.to_csv("fbs_teams_short.csv")