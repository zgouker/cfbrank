import requests,pandas
game_request_get = requests.get(url="https://api.collegefootballdata.com/games?year=2019&seasonType=regular")
game_df =  pandas.io.json.json_normalize(game_request_get.json())
fbs_game_df = game_df[game_df.away_conference.notnull()&game_df.home_conference.notnull()&game_df.home_points.notnull()]
fbs_game_df_short = fbs_game_df[['away_team','away_points','home_team','home_points']]
fbs_game_df.to_csv("data/fbs_games_short.csv")