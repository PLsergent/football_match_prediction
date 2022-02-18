"""
Get data from the api https://www.sportmonks.com/
Scotland league ID: 501
Season ID: 17141 (2020/2021)
All round IDs for the season
Every game statistics for the season

Author: Pierre-Louis Sergent
"""

API_TOKEN = "TBO9kWQvlpRUUzwqbIpmQYxHpNaIc84wkKNSxWgZlHB39zDRILwq5S0BzZ2M"
# For anyone who uses the code bellow be aware that there is a limite of 180call/hours with this token.

import requests
import json

class SportmonksAPI:

    def __init__(self, season_id=17141, league_id=501) -> None:
        """Get every game statistic to train our model
        :Keywords:
            league_id : int
            season_id : int
            rounds : list
                Every round of the season with start and end date, used to determine the begin and the end of the season
            start_of_season : string
            end_of_season : string
            fixtures_of_season : list
                Contains data on every game of the season.
            rows_data : list(lists)
                Contains every rows that will be used in the dataframe
            
        """
        self.league_id = league_id
        self.season_id = season_id

        self.rounds = self.api_call(f"rounds/season/{season_id}")

        self.start_of_season = self.rounds[0]["start"]
        self.end_of_season = self.rounds[-1]["end"]
        self.fixtures_of_season = self.api_call(f"fixtures/between/{self.start_of_season}/{self.end_of_season}", include="stats")

        self.rows_data = self.get_games_data()

    def api_call(self, endpoint, **kwargs):
        page = 1
        final_response = []

        kwargs_str = ""
        for key, value in kwargs.items():
            kwargs_str += f"&{key}={value}"

        # Make multiple calls to the api if there is a pagination
        while(True):
            print(f"Api call: page{page} for {endpoint}")
            url = f"https://soccer.sportmonks.com/api/v2.0/{endpoint}?api_token={API_TOKEN}{kwargs_str}&leagues={self.league_id}&page={page}"
            response = json.loads(requests.request("GET", url).text)
            if type(response["data"]) is dict: response["data"] = [response["data"]]

            final_response += response["data"]

            if "pagination" in response["meta"]:
                if page != response["meta"]["pagination"]["total_pages"]:
                    page += 1
                    continue
            break
        return final_response

    def get_games_data(self):
        """
        columns = ["team_ids", "round_ids", "shots_total", "shots_ongoal", "shots_offgoal", "shots_insidebox", "shots_outsidebox",
            "passes_total", "passes_percentage", "attacks_total", "attacks_dangerous", "fouls", "corners", "possession_time",
            "yellow_cards", "red_cards", "saves", "substitutions", "tackles", "penalties", "injuries", "results"]
        """
        rows_results = []
        for game in self.fixtures_of_season:
            data = game["stats"]["data"]

            # We initialize two rows with the team id and the round id
            # One row for each team
            local_team_row = [game["localteam_id"], game["round_id"]]
            visitor_team_row = [game["visitorteam_id"], game["round_id"]]

            # data[0] contains data about the local team
            local_team_stats = [data[0]["shots"]["total"],
                                data[0]["shots"]["ongoal"],
                                data[0]["shots"]["offgoal"],
                                data[0]["shots"]["insidebox"],
                                data[0]["shots"]["outsidebox"],
                                data[0]["passes"]["total"],
                                data[0]["passes"]["percentage"],
                                data[0]["attacks"]["attacks"],
                                data[0]["attacks"]["dangerous_attacks"],
                                data[0]["fouls"],
                                data[0]["corners"],
                                data[0]["possessiontime"],
                                data[0]["yellowcards"],
                                data[0]["redcards"],
                                data[0]["saves"],
                                data[0]["substitutions"],
                                data[0]["tackles"],
                                data[0]["penalties"],
                                data[0]["injuries"]]

            # data[1] contains data about the visitor team
            visitor_team_stats = [data[1]["shots"]["total"],
                                data[1]["shots"]["ongoal"],
                                data[1]["shots"]["offgoal"],
                                data[1]["shots"]["insidebox"],
                                data[1]["shots"]["outsidebox"],
                                data[1]["passes"]["total"],
                                data[1]["passes"]["percentage"],
                                data[1]["attacks"]["attacks"],
                                data[1]["attacks"]["dangerous_attacks"],
                                data[1]["fouls"],
                                data[1]["corners"],
                                data[1]["possessiontime"],
                                data[1]["yellowcards"],
                                data[1]["redcards"],
                                data[1]["saves"],
                                data[1]["substitutions"],
                                data[1]["tackles"],
                                data[1]["penalties"],
                                data[1]["injuries"]]
            
            # To improve to relevancy of our data, we are comparing the stats of the two teams
            # by doing a simple substraction, so in the end we have the difference between the stats of the two teams
            local_team_row += [a - b if a and b != None else None for a, b in zip(local_team_stats, visitor_team_stats)]
            visitor_team_row += [b - a if a and b != None else None for a, b in zip(local_team_stats, visitor_team_stats)]
            
            # Draw = 0, Win = 1, Loss = -1
            if game["winner_team_id"] == None:
                local_output, visitor_output = 0, 0
            elif game["winner_team_id"] == game["localteam_id"]:
                local_output, visitor_output = 1, -1
            else:
                local_output, visitor_output = -1, 1

            local_team_row.append(local_output)
            visitor_team_row.append(visitor_output)

            rows_results.extend([local_team_row, visitor_team_row])

        return rows_results