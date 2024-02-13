import requests
import pandas as pd
from datetime import date
import os

# LoL API Dev Portal: https://developer.riotgames.com/
# Dev Docs: https://developer.riotgames.com/docs/lol


key = "RGAPI-c5641ff5-8199-4fd1-b6d5-59427a1460bf"

def getUserInfo(username, tag):
    #Gets the user's info from their username for later use.
    response = requests.get("https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"+ username + "/" + tag + "?api_key=" + key).json()
    #response = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + username + "?api_key=" + key).json()
    return response.get("gameName"), response.get("tagLine"), response.get("puuid")

def saveUserInfo(username, tag):
    #Saves the user's info into the userList file to save on API calls later down the line.
    info = getUserInfo(username, tag)
    userDf = pd.read_csv("userList.csv", index_col=None)
    if info[0] in userDf["name"].to_list():
        #Updates the info if they are already in the list.
        index = int(userDf[userDf["name"]==info[0]].index[0])
        userDf.loc[index] = info
        userDf = userDf.to_csv("userList.csv", index=False)
        print("user Updated: " + info[0] + " - " + info[2])
    else:
        #Otherwise adds the user and their info to the list.
        userDf.loc[len(userDf)] = info
        userDf = userDf.to_csv("userList.csv", index=False)
        print("User Added: " + str(info[0]) + " - " + info[2])
    return

def getUserGameIds(username, puuid, matchCount):
    #Pulls the game IDs for the given player and stores them into a csv to be called on later individually.
    response = requests.get("https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?start=0&count=" + str(matchCount) + "&api_key="+key).json()
    currDate = [str(date.today())] * len(response)
    newGames = pd.DataFrame({"matchId": response, "scrapeDate": currDate})
    if username + "_matchList.csv" not in os.listdir("matchList"):
        newGames.to_csv("matchList/"+ username + "_matchList.csv", index=False)
        print("New user matchList added: " + username)
        return
    else:
        oldGames = pd.read_csv("matchList/" + username + "_matchList.csv", index_col=None)
        pd.concat([oldGames, newGames]).drop_duplicates("matchId").reset_index(drop=True).to_csv("matchList/"+ username + "_matchList.csv", index=False)
        print("Existing user matchList updated: " + username)
        return

def updateUserGameIds(matchCount):
    #Pulls the game IDs for all users in userList.
    df = pd.read_csv("userList.csv", index_col=None)
    for x in range(len(df.index)):
        getUserGameIds(df['name'][x], df["puuid"][x], matchCount)
    return

def getGameInfo(matchId, puuid):
    response = requests.get("https://americas.api.riotgames.com/lol/match/v5/matches/" + matchId + "/?api_key=" + key).json()
    personalInfo = []
    info = []
    
    #general game info
    info.append(matchId)
    info.append(response["info"]["gameDuration"]) 
    info.append(response["info"]["gameMode"]) 
    info.append(response["info"]["gameStartTimestamp"]) 
    
    #Loops 10 times to get the individual stats of each player and appends them to the list
    for x in range(10):
        if response["info"]["participants"][x]["puuid"] == puuid:
            #Stores personal stats
            personalInfo.append(response["info"]["participants"][x]["win"])
            personalInfo.append(response["info"]["participants"][x]["championName"])
            personalInfo.append(response["info"]["participants"][x]["championId"])
            personalInfo.append(response["info"]["participants"][x]["kills"])
            personalInfo.append(response["info"]["participants"][x]["deaths"])
            personalInfo.append(response["info"]["participants"][x]["assists"])

        info.append(response["info"]["participants"][x]["summonerName"])
        info.append(response["info"]["participants"][x]["puuid"])
        info.append(response["info"]["participants"][x]["championName"])
        info.append(response["info"]["participants"][x]["championId"])
        info.append(response["info"]["participants"][x]["win"])
        
        info.append(response["info"]["participants"][x]["kills"])
        info.append(response["info"]["participants"][x]["deaths"])
        info.append(response["info"]["participants"][x]["assists"])
        info.append(response["info"]["participants"][x]["goldEarned"])

        info.append(response["info"]["participants"][x]["physicalDamageDealtToChampions"])
        info.append(response["info"]["participants"][x]["magicDamageDealtToChampions"])
        info.append(response["info"]["participants"][x]["trueDamageDealtToChampions"])
        info.append(response["info"]["participants"][x]["totalDamageDealtToChampions"])
        info.append(response["info"]["participants"][x]["physicalDamageTaken"])
        info.append(response["info"]["participants"][x]["magicDamageTaken"])
        info.append(response["info"]["participants"][x]["trueDamageTaken"])
        info.append(response["info"]["participants"][x]["totalDamageTaken"])

        info.append(response["info"]["participants"][x]["item0"])
        info.append(response["info"]["participants"][x]["item1"])
        info.append(response["info"]["participants"][x]["item2"])
        info.append(response["info"]["participants"][x]["item3"])
        info.append(response["info"]["participants"][x]["item4"])
        info.append(response["info"]["participants"][x]["item5"])
        info.append(response["info"]["participants"][x]["item6"])

    return personalInfo + info

def updateGameInfo(username, puuid):
    matchList = pd.read_csv("matchList/" + username + "_matchList.csv", index_col=None)["matchId"]  
    columns = ["userWin", "userChamp", "userChampId", "userKills", "userDeaths", "userAssists",
            "matchId", "gameDurration", "gameMode", "gameStartTimestamp",
            
            "p0SummonerName", "p0Puuid", "p0ChampionName", "p0ChampionId", "p0Win",
            "p0Kills", "p0Deaths", "p0Assists", "p0GoldEarned",
            "p0PhysicalDamageDealtToChampions", "p0MagicDamageDealtToChampions", "p0TrueDamageDealtToChampions", "p0TotalDamageDealtToChampions",
            "p0PhysicalDamageTaken", "p0MagicDamageTaken", "p0TrueDamageTaken", "p0TotalDamageTaken",
            "p0Item0", "p0Item1", "p0Item2", "p0Item3", "p0Item4", "p0Item5", "p0Item6",
            
            "p1SummonerName", "p1Puuid", "p1ChampionName", "p1ChampionId", "p1Win",
            "p1Kills", "p1Deaths", "p1Assists", "p1GoldEarned",
            "p1PhysicalDamageDealtToChampions", "p1MagicDamageDealtToChampions", "p1TrueDamageDealtToChampions", "p1TotalDamageDealtToChampions",
            "p1PhysicalDamageTaken", "p1MagicDamageTaken", "p1TrueDamageTaken", "p1TotalDamageTaken",
            "p1Item0", "p1Item1", "p1Item2", "p1Item3", "p1Item4", "p1Item5", "p1Item6",
            
            "p2SummonerName", "p2Puuid", "p2ChampionName", "p2ChampionId", "p2Win",
            "p2Kills", "p2Deaths", "p2Assists", "p2GoldEarned",
            "p2PhysicalDamageDealtToChampions", "p2MagicDamageDealtToChampions", "p2TrueDamageDealtToChampions", "p2TotalDamageDealtToChampions",
            "p2PhysicalDamageTaken", "p2MagicDamageTaken", "p2TrueDamageTaken", "p2TotalDamageTaken",
            "p2Item0", "p2Item1", "p2Item2", "p2Item3", "p2Item4", "p2Item5", "p2Item6",
            
            "p3SummonerName", "p3Puuid", "p3ChampionName", "p3ChampionId", "p3Win",
            "p3Kills", "p3Deaths", "p3Assists", "p3GoldEarned",
            "p3PhysicalDamageDealtToChampions", "p3MagicDamageDealtToChampions", "p3TrueDamageDealtToChampions", "p3TotalDamageDealtToChampions",
            "p3PhysicalDamageTaken", "p3MagicDamageTaken", "p3TrueDamageTaken", "p3TotalDamageTaken",
            "p3Item0", "p3Item1", "p3Item2", "p3Item3", "p3Item4", "p3Item5", "p3Item6",

            "p4SummonerName", "p4Puuid", "p4ChampionName", "p4ChampionId", "p4Win",
            "p4Kills", "p4Deaths", "p4Assists", "p4GoldEarned",
            "p4PhysicalDamageDealtToChampions", "p4MagicDamageDealtToChampions", "p4TrueDamageDealtToChampions", "p4TotalDamageDealtToChampions",
            "p4PhysicalDamageTaken", "p4MagicDamageTaken", "p4TrueDamageTaken", "p4TotalDamageTaken",
            "p4Item0", "p4Item1", "p4Item2", "p4Item3", "p4Item4", "p4Item5", "p4Item6",

            "p5SummonerName", "p5Puuid", "p5ChampionName", "p5ChampionId", "p5Win",
            "p5Kills", "p5Deaths", "p5Assists", "p5GoldEarned",
            "p5PhysicalDamageDealtToChampions", "p5MagicDamageDealtToChampions", "p5TrueDamageDealtToChampions", "p5TotalDamageDealtToChampions",
            "p5PhysicalDamageTaken", "p5MagicDamageTaken", "p5TrueDamageTaken", "p5TotalDamageTaken",
            "p5Item0", "p5Item1", "p5Item2", "p5Item3", "p5Item4", "p5Item5", "p5Item6",

            "p6SummonerName", "p6Puuid", "p6ChampionName", "p6ChampionId", "p6Win",
            "p6Kills", "p6Deaths", "p6Assists", "p6GoldEarned",
            "p6PhysicalDamageDealtToChampions", "p6MagicDamageDealtToChampions", "p6TrueDamageDealtToChampions", "p6TotalDamageDealtToChampions",
            "p6PhysicalDamageTaken", "p6MagicDamageTaken", "p6TrueDamageTaken", "p6TotalDamageTaken",
            "p6Item0", "p6Item1", "p6Item2", "p6Item3", "p6Item4", "p6Item5", "p6Item6",

            "p7SummonerName", "p7Puuid", "p7ChampionName", "p7ChampionId", "p7Win",
            "p7Kills", "p7Deaths", "p7Assists", "p7GoldEarned",
            "p7PhysicalDamageDealtToChampions", "p7MagicDamageDealtToChampions", "p7TrueDamageDealtToChampions", "p7TotalDamageDealtToChampions",
            "p7PhysicalDamageTaken", "p7MagicDamageTaken", "p7TrueDamageTaken", "p7TotalDamageTaken",
            "p7Item0", "p7Item1", "p7Item2", "p7Item3", "p7Item4", "p7Item5", "p7Item6",

            "p8SummonerName", "p8Puuid", "p8ChampionName", "p8ChampionId", "p8Win",
            "p8Kills", "p8Deaths", "p8Assists", "p8GoldEarned",
            "p8PhysicalDamageDealtToChampions", "p8MagicDamageDealtToChampions", "p8TrueDamageDealtToChampions", "p8TotalDamageDealtToChampions",
            "p8PhysicalDamageTaken", "p8MagicDamageTaken", "p8TrueDamageTaken", "p8TotalDamageTaken",
            "p8Item0", "p8Item1", "p8Item2", "p8Item3", "p8Item4", "p8Item5", "p8Item6",

            "p9SummonerName", "p9Puuid", "p9ChampionName", "p9ChampionId", "p9Win",
            "p9Kills", "p9Deaths", "p9Assists", "p9GoldEarned",
            "p9PhysicalDamageDealtToChampions", "p9MagicDamageDealtToChampions", "p9TrueDamageDealtToChampions", "p9TotalDamageDealtToChampions",
            "p9PhysicalDamageTaken", "p9MagicDamageTaken", "p9TrueDamageTaken", "p9TotalDamageTaken",
            "p9Item0", "p9Item1", "p9Item2", "p9Item3", "p9Item4", "p9Item5", "p9Item6"]
    if username + "_matchData.csv" not in os.listdir("matchData"):
        #Creates a new match data file if it doesnt already exist
        info = getGameInfo(matchList[0], puuid)
        matchDf = pd.DataFrame(info).T
        matchDf.columns = columns
        matchList.pop(0)
        for matchId in matchList:
            newMatchDf = pd.DataFrame(getGameInfo(matchId, puuid)).T
            newMatchDf.columns = columns
            matchDf = pd.concat([matchDf, newMatchDf])
        matchDf.to_csv("matchData/" + username + "_matchData.csv", index=False)
        print("Created " + username + " match data file ("+ str(len(matchList)) +" new matches).")
        return
    else:
        #Updates an already existing match data file
        oldMatchDf = pd.read_csv("matchData/" + username + "_matchData.csv", index_col = None)
        newMatchList = list(set(matchList) - set(oldMatchDf["matchId"]))
        for matchId in newMatchList:
            newMatchDf = pd.DataFrame(getGameInfo(matchId, puuid)).T
            newMatchDf.columns = columns
            oldMatchDf = pd.concat([oldMatchDf, newMatchDf])
        oldMatchDf.to_csv("matchData/" + username + "_matchData.csv", index=False)
        print("Updated " + username + " match data updated (" + str(len(newMatchList)) + " new matches).")
        return

def updateAllGameInfo(gameCount):
    userDf = pd.read_csv("userList.csv", index_col=None)
    updateUserGameIds(gameCount)
    for x in range(len(userDf.index)):
        updateGameInfo(userDf["name"][x], userDf["puuid"][x])
    return

def championTable(username, gameMode="ARAM"):
    #Returns a dataframe with all played champions statistics
    df = pd.read_csv("matchData/" + username + "_matchData.csv", index_col=None)
    df = df[df["gameMode"] == gameMode]
    df["date"] = pd.to_datetime(df["gameStartTimestamp"], unit='ms')
    df = df[df["date"] >= "2024-01-10 00:00:00.000"]
    championList = pd.unique(df["userChamp"])
    gameCountList, winCountList, killCountList, deathCountList, assistCountList, kdaList = [], [], [], [], [], []
    for champ in championList:
        champDf = df[df["userChamp"] == champ]
        gameCount = len(champDf["userChamp"])
        gameCountList.append(gameCount)
        winCountList.append(round(len(champDf[champDf["userWin"]==True])/gameCount, 2))
        killCountList.append(round(champDf["userKills"].sum()/gameCount, 2))
        deathCountList.append(round(champDf["userDeaths"].sum()/gameCount, 2))
        assistCountList.append(round(champDf["userAssists"].sum()/gameCount, 2))
        kdaList.append(round((champDf["userAssists"].sum() + champDf["userKills"].sum())/(champDf["userDeaths"].sum()),2))
    champTable = pd.DataFrame({"champion": championList, "winRate": winCountList, "gameCount": gameCountList, "kda": kdaList, "AvgKills": killCountList,
                               "AvgDeaths": deathCountList, "AvgAssists": assistCountList}).sort_values(by=["gameCount", "winRate"], ascending=False).reset_index(drop=True)
    return champTable

def userListTable(gameMode="ARAM"):
    #Returns a dataframe that has all users' stats in user list.
    userList = pd.read_csv("userList.csv", index_col=None)
    userListList = userList["name"].to_list()
    gameCountList, winRateList, killList, deathList, assistList, kdaList = [], [], [], [], [], []
    for user in userListList:
        df = pd.read_csv("matchData/" + user + "_matchData.csv", index_col=None)
        df = df[df["gameMode"] == gameMode]
        df["date"] = pd.to_datetime(df["gameStartTimestamp"], unit='ms')
        df = df[df["date"] >= "2024-01-10 00:00:00.000"]
        gameCount = len(df["userChamp"])
        gameCountList.append(gameCount)
        winRateList.append(round(len(df[df["userWin"]==True])/gameCount, 2))
        killList.append(round(df["userKills"].sum()/gameCount, 2))
        deathList.append(round(df["userDeaths"].sum()/gameCount, 2))
        assistList.append(round(df["userAssists"].sum()/gameCount, 2))
        kdaList.append(round((df["userAssists"].sum() + df["userKills"].sum())/(df["userDeaths"].sum()),2))
    userTable = pd.DataFrame({"name": userListList, "winRate": winRateList, "gameCount": gameCountList, "kda": kdaList, "AvgKills": killList, 
                              "AvgDeaths": deathList, "AvgAssists": assistList}).reset_index(drop=True)
    return userTable

#Add user to user list
#saveUserInfo("Jackpot", "monte")

#Update all match data for users in user list
updateAllGameInfo(100)

#Final Tables
#print(championTable("Jackpot"))
#print(userListTable())