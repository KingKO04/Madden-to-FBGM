import requests
import time
from bs4 import BeautifulSoup
import concurrent.futures
import json
import numpy as np
import scipy.stats as stats
import pandas as pd

def process_player(name, profile_url):
    profile_response = requests.get(profile_url, headers=headers)
    profile_soup = BeautifulSoup(profile_response.text, "html.parser")

    # Extract rating names and values
    rating_names = profile_soup.find_all("span", class_="Stat_label__faUgX")
    rating_values = profile_soup.find_all("span", class_="Stat_value__TT86G")
    images = profile_soup.find_all("img", class_="Picture_image__L8suG")

    # Get all elements with the shared class
    attributes = profile_soup.find_all("span", class_="Typography_typography___mliz generated_body2__P92dE Typography_margins__GGnT6")  # Update class

    # Process attributes in order
    extracted = [attr.text.strip() for attr in attributes]

    ratings_dict = {}
    ratings_dict['Image'] = images[2]["src"]
    ratings_dict['Position'] = extracted[0]
    ratings_dict['Team'] = extracted[1]
    ratings_dict['Height'] = extracted[2]
    ratings_dict['Weight'] = extracted[3]
    ratings_dict['Archetype'] = extracted[4]
    ratings_dict['College'] = extracted[-4]
    ratings_dict['Age'] = extracted[-3]
    ratings_dict['Draft Year'] = extracted[-2]
    ratings_dict['Jersey Number'] = extracted[-1]
    for r_name, r_value in zip(rating_names, rating_values):
        if r_name.text.strip() == "General":
            continue
        ratings_dict[r_name.text.strip()] = r_value.text.strip()
    players_dict[name] = ratings_dict
    time.sleep(1)

    return name, ratings_dict

def match_distribution(target_data, source_data):
  return np.percentile(
      np.array(source_data),
      stats.rankdata(np.array(target_data)) / len(np.array(target_data)) * 100
      )

base_url = "https://www.ea.com"
ratings_url_template = "https://www.ea.com/en/games/madden-nfl/ratings?page={}"

# Fetch the main ratings page
headers = {"User-Agent": "Mozilla/5.0"}

player_profiles = {}
players_dict = {}

for page_num in range(1, 22):
  ratings_url = ratings_url_template.format(page_num)
  response = requests.get(ratings_url, headers=headers)
  soup = BeautifulSoup(response.text, "html.parser")

  # Find player profile links
  players = soup.find_all("a", class_="Table_profileCellAnchor__Zj6g4")

  for player in players:
      name = player.text.strip()
      profile_link = base_url + player["href"]  # Construct full URL
      player_profiles[name] = profile_link

with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(process_player, name, profile_url) for name, profile_url in player_profiles.items()]

    for future in concurrent.futures.as_completed(futures):
        name, ratings_dict = future.result()
        players_dict[name] = ratings_dict

fbgm_players = []
for player in players_dict:
  current = players_dict[player]
  fbgm_players.append({})
  i = len(fbgm_players) - 1

  name = player.split(' ', 1)
  fbgm_players[i]['firstName'] = name[0]
  fbgm_players[i]['lastName'] = name[1]
  fbgm_players[i]['born'] = {"year" : 2024 - int(players_dict[player]['Age'])}
  fbgm_players[i]['draft'] = {"year" : 2024 - int(players_dict[player]['Draft Year'])}
  fbgm_players[i]['college'] = current['College']

  match current['Team']:
    case "Arizona Cardinals":
      fbgm_players[i]['tid'] = 0
    case "Atlanta Falcons":
      fbgm_players[i]['tid'] = 1
    case "Baltimore Ravens":
      fbgm_players[i]['tid'] = 2
    case "Buffalo Bills":
      fbgm_players[i]['tid'] = 3
    case "Carolina Panthers":
      fbgm_players[i]['tid'] = 4
    case "Chicago Bears":
      fbgm_players[i]['tid'] = 5
    case "Cincinnati Bengals":
      fbgm_players[i]['tid'] = 6
    case "Cleveland Browns":
      fbgm_players[i]['tid'] = 7
    case "Dallas Cowboys":
      fbgm_players[i]['tid'] = 8
    case "Denver Broncos":
      fbgm_players[i]['tid'] = 9
    case "Detroit Lions":
      fbgm_players[i]['tid'] = 10
    case "Green Bay Packers":
      fbgm_players[i]['tid'] = 11
    case "Houston Texans":
      fbgm_players[i]['tid'] = 12
    case "Indianapolis Colts":
      fbgm_players[i]['tid'] = 13
    case "Jacksonville Jaguars":
      fbgm_players[i]['tid'] = 14
    case "Kansas City Chiefs":
      fbgm_players[i]['tid'] = 15
    case "Las Vegas Raiders":
      fbgm_players[i]['tid'] = 16
    case "Los Angeles Chargers":
      fbgm_players[i]['tid'] = 17
    case "Los Angeles Rams":
      fbgm_players[i]['tid'] = 18
    case "Miami Dolphins":
      fbgm_players[i]['tid'] = 19
    case "Minnesota Vikings":
      fbgm_players[i]['tid'] = 20
    case "New England Patriots":
      fbgm_players[i]['tid'] = 21
    case "New Orleans Saints":
      fbgm_players[i]['tid'] = 22
    case "NY Giants":
      fbgm_players[i]['tid'] = 23
    case "NY Jets":
      fbgm_players[i]['tid'] = 24
    case "Philadelphia Eagles":
      fbgm_players[i]['tid'] = 25
    case "Pittsburgh Steelers":
      fbgm_players[i]['tid'] = 26
    case "San Francisco 49ers":
      fbgm_players[i]['tid'] = 27
    case "Seattle Seahawks":
      fbgm_players[i]['tid'] = 28
    case "Tampa Bay Buccaneers":
      fbgm_players[i]['tid'] = 29
    case "Tennessee Titans":
      fbgm_players[i]['tid'] = 30
    case "Washington Commanders":
      fbgm_players[i]['tid'] = 31
    case _:
      fbgm_players[i]['tid'] = -1

  feet, inches = current['Height'].split('"')[0].split("'")
  fbgm_players[i]['hgt'] = int(feet) * 12 + int(inches)

  fbgm_players[i]['imgURL'] = current["Image"]
  fbgm_players[i]['jerseyNumber'] = current['Jersey Number']
  fbgm_players[i]['weight'] = int(current['Weight'].split('l')[0])

  match current['Position']:
    case "Quarterback":
      fbgm_players[i]['pos'] = "QB"
    case "Halfback":
      fbgm_players[i]['pos'] = "RB"
    case "Wide Receiver":
      fbgm_players[i]['pos'] = "WR"
    case "Fullback" | "Tight End":
      fbgm_players[i]['pos'] = "TE"
    case "Left Tackle" | "Left Guard" | "Center" | "Right Guard" | "Right Tackle":
      fbgm_players[i]['pos'] = "OL"
    case "Left Edge" | "Defensive Tackle" | "Right Edge":
      fbgm_players[i]['pos'] = "DL"
    case "Weak Backer" | "Mike Backer" | "Sam Backer":
      fbgm_players[i]['pos'] = "LB"
    case "Cornerback":
      fbgm_players[i]['pos']= "CB"
    case "Strong Safety" | "Free Safety":
      fbgm_players[i]['pos'] = "S"
    case "Kicker":
      fbgm_players[i]['pos'] = "K"
    case _:
      fbgm_players[i]['pos'] = "P"

  ratings = [{}]
  ratings[0]['hgt'] = int(round((fbgm_players[i]['hgt'] - 64) / 18 * 100))
  ratings[0]['stre'] = int(round(.71 * int(current['Strength']) +
                                 .15 * int(current['Trucking']) +
                                 .14 * int(current['Impact Blocking'])))
  ratings[0]['spd'] = int(round(.53 * int(current['Speed']) +
                                .21 * int(current['Acceleration']) +
                                .11 * int(current['Agility']) +
                                .1 * int(current['Change Of Direction']) +
                                .05 * int(current['Pursuit'])))
  ratings[0]['endu'] = int(round(.8 * int(current['Stamina']) +
                                 .1 * int(current['Toughness']) +
                                 .05 * int(current['Strength']) +
                                 .05 * int(current['Injury'])))
  ratings[0]['thv'] = int(round(.4 * int(current['Awareness']) +
                                .15 * int(current['Play Action']) +
                                .15 * int(current['Throw Under Pressure']) +
                                .1 * int(current['Break Sack']) +
                                .1 * int(current['BC Vision']) +
                                .1 * int(current['Throw on the Run'])))
  ratings[0]['thp'] = int(round(.85 * int(current['Throw Power']) +
                                .1 * int(current['Strength']) +
                                .05 * int(current['Throw Accuracy Deep'])))
  ratings[0]['tha'] = int(round(.4 * int(current['Throw Accuracy Short']) +
                                .3 * int(current['Throw Accuracy Mid']) +
                                .15 * int(current['Throw Accuracy Deep']) +
                                .1 * int(current['Throw on the Run']) +
                                .05 * int(current['Play Action'])))
  ratings[0]['bsc'] = int(current['Carrying'])
  ratings[0]['elu'] = int(round(.25 * int(current['Juke Move']) +
                               .19 * int(current['Spin Move']) +
                               .19 * int(current['Change Of Direction']) +
                               .13 * int(current['Break Tackle']) +
                               .12 * int(current['Acceleration']) +
                               .06 * int(current['Agility']) +
                               .06 * int(current['BC Vision'])))
  ratings[0]['rtr'] = int(round(.3 * int(current['Short Route Running']) +
                                .3 * int(current['Medium Route Running']) +
                                .2 * int(current['Deep Route Running']) +
                                .1 * int(current['Change Of Direction']) +
                                .05 * int(current['Agility']) +
                                .05 * int(current['Release'])))
  ratings[0]['hnd'] = int(round(.75 * int(current['Catching']) +
                                .18 * int(current['Catch In Traffic']) +
                                .07 * int(current['Spectacular Catch'])))
  ratings[0]['rbk'] = int(round(.4 * int(current['Run Block']) +
                                .2 * int(current['Run Block Power']) +
                                .2 * int(current['Run Block Finesse']) +
                                .2 * int(current['Lead Block'])))
  ratings[0]['pbk'] = int(round(.5 * int(current['Pass Block']) +
                                .25 * int(current['Pass Block Power']) +
                                .25 * int(current['Pass Block Finesse'])))
  ratings[0]['pcv'] = int(round(.4 * int(current['Man Coverage']) +
                                .4 * int(current['Zone Coverage']) +
                                .1 * int(current['Press']) +
                                .1 * int(current['Play Recognition'])))
  ratings[0]['tck'] = int(round(.6 * int(current['Tackle']) +
                                .15 * int(current['Hit Power']) +
                                .1 * int(current['Pursuit']) +
                                .1 * int(current['Block Shedding']) +
                                .03 * int(current['Finesse Moves']) +
                                .02 * int(current['Power Moves'])))
  ratings[0]['prs'] = int(round(.6 * int(current['Block Shedding']) +
                                .3 * int(current['Finesse Moves']) +
                                .1 * int(current['Power Moves'])))
  ratings[0]['rns'] = int(round(.6 * int(current['Block Shedding']) +
                                .2 * int(current['Power Moves']) +
                                .2 * int(current['Pursuit'])))
  ratings[0]['kpw'] = ratings[0]['ppw'] = int(current['Kick Power'])
  ratings[0]['kac'] = ratings[0]['pac'] = int(current['Kick Accuracy'])

  fbgm_players[i]['ratings'] = ratings

player_ratings = pd.read_csv("PlayerRatings/PlayerRatings.csv")
for i in range(1, 19):
  temp = pd.read_csv(f"PlayerRatings/PlayerRatings ({i}).csv")
  player_ratings = pd.concat([player_ratings, temp], ignore_index=True)

player_ratings = player_ratings.iloc[:, range(9, 29)]
attributes_arrays = {
    col: player_ratings[col].to_numpy() for col in player_ratings.columns
    }

i = 0
attributes = []
while i < len(fbgm_players):
  j = 0
  for attribute in fbgm_players[i]['ratings'][0]:
    if attribute == "hgt":
      continue
    if i == 0:
      attributes.append(np.array([]))

    attributes[j] = np.append(attributes[j], fbgm_players[i]['ratings'][0][attribute])
    j += 1
  i += 1

for i in range(len(attributes)):
  attributes[i] = np.round(match_distribution(
      attributes[i],
      attributes_arrays[player_ratings.columns[i]]
      ))

for i in range(len(fbgm_players)):
  for j in range(len(fbgm_players[0]['ratings'][0])):
    if j != 0:
      fbgm_players[i]['ratings'][0][list(fbgm_players[0]['ratings'][0].keys())[j]] = attributes[j - 1][i]
    j += 1
  i += 1

confs = [
    {"cid": 0, "name": "AFC"},
    {"cid": 1, "name": "NFC"}
]

divs = [
    {"did": 0, "cid": 0, "name": "East"},
    {"did": 1, "cid": 0, "name": "North"},
    {"did": 2, "cid": 0, "name": "South"},
    {"did": 3, "cid": 0, "name": "West"},
    {"did": 4, "cid": 1, "name": "East"},
    {"did": 5, "cid": 1, "name": "North"},
    {"did": 6, "cid": 1, "name": "South"},
    {"did": 7, "cid": 1, "name": "West"}
]

gameAttributes = {
    "completionFactor": .95,
    "confs": confs,
    "divs": divs,
    "draftAges": [20, 26],
    "draftPickAutoContract": True,
    "draftPickAutoContractPercent": 20,
    "draftPickAutoContractRounds": 7,
    "fantasyPoints": "ppr",
    "fourthDownFactor": 1.15,
    "intFactor": .9,
    "luxuryPayroll": 330000,
    "maxContract": 60000,
    "maxRosterSize": 53,
    "minContract": 850,
    "minPayroll": 250000,
    "minRosterSize": 46,
    "numSeasonsFutureDraftPicks": 3,
    "rookieContractLengths": [4],
    "salaryCap": 280000
}

teams = [
    {
        "tid": 0,
        "cid": 1,
        "did": 7,
        "region": "Arizona",
        "name": "Cardinals",
        "abbrev": "ARI",
        "pop": 4.1,
        "stadiumCapacity": 63400,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/ari.png",
        "colors": ["#97233F", "#000000", "#FFB612"]
    },
    {
        "tid": 1,
        "cid": 1,
        "did": 6,
        "region": "Atlanta",
        "name": "Falcons",
        "abbrev": "ATL",
        "pop": 6.3,
        "stadiumCapacity": 71000,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/atl.png",
        "colors": ["#A71930", "#000000", "#A5ACAF"]
    },
    {
        "tid": 2,
        "cid": 0,
        "did": 1,
        "region": "Baltimore",
        "name": "Ravens",
        "abbrev": "BAL",
        "pop": 2.8,
        "stadiumCapacity": 71008,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/bal.png",
        "colors": ["#241773", "#000000", "#9E7C0C"]
    },
    {
        "tid": 3,
        "cid": 0,
        "did": 0,
        "region": "Buffalo",
        "name": "Bills",
        "abbrev": "BUF",
        "pop": 1.2,
        "stadiumCapacity": 71608,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/buf.png",
        "colors": ["#0038D", "#C60C30", "#FFFFFF"]
    },
    {
        "tid": 4,
        "cid": 1,
        "did": 6,
        "region": "Carolina",
        "name": "Panthers",
        "abbrev": "CAR",
        "pop": 2.8,
        "stadiumCapacity": 74867,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/car.png",
        "colors": ["#0085CA", "#101820", "#BFC0BF"]
    },
    {
        "tid": 5,
        "cid": 1,
        "did": 5,
        "region": "Chicago",
        "name": "Bears",
        "abbrev": "CHI",
        "pop": 9.3,
        "stadiumCapacity": 61500,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/chi.png",
        "colors": ["#0B162A", "#C83803", "FFFFFF"]
    },
    {
        "tid": 6,
        "cid": 0,
        "did": 1,
        "region": "Cincinnati",
        "name": "Bengals",
        "abbrev": "CIN",
        "pop": 2.3,
        "stadiumCapacity": 65515,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/cin.png",
        "colors": ["#FB4F14", "#000000", "#FFFFFF"]
    },
    {
        "tid": 7,
        "cid": 0,
        "did": 1,
        "region": "Cleveland",
        "name": "Browns",
        "abbrev": "CLE",
        "pop": 2.2,
        "stadiumCapacity": 67431,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/cle.png",
        "colors": ["#311D00", "#FF3C00", "#FFFFFF"]
    },
    {
        "tid": 8,
        "cid": 1,
        "did": 4,
        "region": "Dallas",
        "name": "Cowboys",
        "abbrev": "DAL",
        "pop": 8.1,
        "stadiumCapacity": 100000,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/dal.png",
        "colors": ["#003594", "#041E42", "#869397"]
    },
    {
        "tid": 9,
        "cid": 0,
        "did": 3,
        "region": "Denver",
        "name": "Broncos",
        "abbrev": "DEN",
        "pop": 3,
        "stadiumCapacity": 76125,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/den.png",
        "colors": ["#FB4F14", "#002244", "#FFFFFF"]
    },
    {
        "tid": 10,
        "cid": 1,
        "did": 5,
        "region": "Detroit",
        "name": "Lions",
        "abbrev": "DET",
        "pop": 4.3,
        "stadiumCapacity": 65000,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/det.png",
        "colors": ["#0076B6", "#B0B7BC", "#000000"]
    },
    {
        "tid": 11,
        "cid": 1,
        "did": 5,
        "region": "Green Bay",
        "name": "Packers",
        "abbrev": "GB",
        "pop": 0.33,
        "stadiumCapacity": 81441,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/gb.png",
        "colors": ["#203731", "#FFB612", "#FFFFFF"]
    },
    {
        "tid": 12,
        "cid": 0,
        "did": 2,
        "region": "Houston",
        "name": "Texans",
        "abbrev": "HOU",
        "pop": 7.5,
        "stadiumCapacity": 72220,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/hou.png",
        "colors": ["#03202F", "#A71930", "#FFFFFF"]
    },
    {
        "tid": 13,
        "cid": 0,
        "did": 2,
        "region": "Indianapolis",
        "name": "Colts",
        "abbrev": "IND",
        "pop": 2.1,
        "stadiumCapacity": 70000,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/ind.png",
        "colors": ["#002C5F", "#A2AAAD", "#FFFFFF"]
    },
    {
        "tid": 14,
        "cid": 0,
        "did": 2,
        "region": "Jacksonville",
        "name": "Jaguars",
        "abbrev": "JAC",
        "pop": 1.7,
        "stadiumCapacity": 67814,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/jac.png",
        "colors": ["#101820", "#D7A22A", "#9F792C"]
    },
    {
        "tid": 15,
        "cid": 0,
        "did": 3,
        "region": "Kansas City",
        "name": "Chiefs",
        "abbrev": "KC",
        "pop": 2.2,
        "stadiumCapacity": 76416,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/kc.png",
        "colors": ["#E31837", "#FFB81C", "#FFFFFF"]
    },
    {
        "tid": 16,
        "cid": 0,
        "did": 3,
        "region": "Las Vegas",
        "name": "Raiders",
        "abbrev": "LV",
        "pop": 2.3,
        "stadiumCapacity": 65000,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/lv.png",
        "colors": ["#000000", "#A5ACAF", "FFFFFF"]
    },
    {
        "tid": 17,
        "cid": 0,
        "did": 3,
        "region": "Los Angeles",
        "name": "Chargers",
        "abbrev": "LAC",
        "pop": 12.8,
        "stadiumCapacity": 70240,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/lac.png",
        "colors": ["#0080C6", "#FFC20E", "#FFFFFF"]
    },
    {
        "tid": 18,
        "cid": 1,
        "did": 7,
        "region": "Los Angeles",
        "name": "Rams",
        "abbrev": "LAR",
        "pop": 12.8,
        "stadiumCapacity": 70240,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/lar.png",
        "colors": ["#003594", "#FFA300", "#FF8200"]
    },
    {
        "tid": 19,
        "cid": 0,
        "did": 0,
        "region": "Miami",
        "name": "Dolphins",
        "abbrev": "MIA",
        "pop": 6.2,
        "stadiumCapacity": 65000,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/mia.png",
        "colors": ["#008E97", "#FC4C02", "#005778"]
    },
    {
        "tid": 20,
        "cid": 1,
        "did": 5,
        "region": "Minnesota",
        "name": "Vikings",
        "abbrev": "MIN",
        "pop": 3.7,
        "stadiumCapacity": 66860,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/min.png",
        "colors": ["#4F2683", "FFC62F", "FFFFFF"]
    },
    {
        "tid": 21,
        "cid": 0,
        "did": 0,
        "region": "New England",
        "name": "Patriots",
        "abbrev": "NE",
        "pop": 4.9,
        "stadiumCapacity": 64628,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/ne.png",
        "colors": ["#002244", "#C60C30", "#B0B7BC"]
    },
    {
        "tid": 22,
        "cid": 1,
        "did": 6,
        "region": "New Orleans",
        "name": "Saints",
        "abbrev": "NO",
        "pop": 0.96,
        "stadiumCapacity": 73208,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/no.png",
        "colors": ["#D3BC8D", "#101820", "#FFFFFF"]
    },
    {
        "tid": 23,
        "cid": 1,
        "did": 4,
        "region": "New York",
        "name": "Giants",
        "abbrev": "NYG",
        "pop": 19.5,
        "stadiumCapacity": 82500,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/nyg.png",
        "colors": ["#0B2265", "#A71930", "#A5ACAF"]
    },
    {
        "tid": 24,
        "cid": 0,
        "did": 0,
        "region": "New York",
        "name": "Jets",
        "abbrev": "NYJ",
        "pop": 19.5,
        "stadiumCapacity": 82500,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/nyj.png",
        "colors": ["#125740", "#000000", "#FFFFFF"]
    },
    {
        "tid": 25,
        "cid": 1,
        "did": 4,
        "region": "Philadelphia",
        "name": "Eagles",
        "abbrev": "PHI",
        "pop": 6.2,
        "stadiumCapacity": 67594,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/phi.png",
        "colors": ["#004C54", "#A5ACAF", "#ACC0C6"]
    },
    {
        "tid": 26,
        "cid": 0,
        "did": 1,
        "region": "Pittsburgh",
        "name": "Steelers",
        "abbrev": "PIT",
        "pop": 2.4,
        "stadiumCapacity": 68400,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/pit.png",
        "colors": ["#FFB612", "#101820", "#003087"]
    },
    {
        "tid": 27,
        "cid": 1,
        "did": 7,
        "region": "San Francisco",
        "name": "49ers",
        "abbrev": "SF",
        "pop": 4.6,
        "stadiumCapacity": 68500,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/sf.png",
        "colors": ["#AA0000", "#B3995D", "#FFFFFF"]
    },
    {
        "tid": 28,
        "cid": 1,
        "did": 7,
        "region": "Seattle",
        "name": "Seahawks",
        "abbrev": "SEA",
        "pop": 4,
        "stadiumCapacity": 68740,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/sea.png",
        "colors": ["#002244", "#69BE28", "#A5ACAF"]
    },
    {
        "tid": 29,
        "cid": 1,
        "did": 6,
        "region": "Tampa Bay",
        "name": "Buccaneers",
        "abbrev": "TB",
        "pop": 3.3,
        "stadiumCapacity": 69218,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/tb.png",
        "colors": ["#D50A0A", "#FF7900", "#FF7900"]
    },
    {
        "tid": 30,
        "cid": 0,
        "did": 2,
        "region": "Tennessee",
        "name": "Titans",
        "abbrev": "TEN",
        "pop": 2.1,
        "stadiumCapacity": 69143,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/ten.png",
        "colors": ["#0C2340", "#4B92DB", "#C8102E"]
    },
    {
        "tid": 31,
        "cid": 1,
        "did": 4,
        "region": "Washington",
        "name": "Commanders",
        "abbrev": "WAS",
        "pop": 6.3,
        "stadiumCapacity": 62000,
        "imgURL": "https://a.espncdn.com/i/teamlogos/nfl/500-dark/was.png",
        "colors": ["#5A1414", "#FFB612", "#FFFFFF"]
    }
]

data = {
    "players" : fbgm_players,
    "teams" : teams,
    "gameAttributes" : gameAttributes
}

with open("Madden 25 to Football GM.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)
