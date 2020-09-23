from json import dumps
from lcu_driver import Connector
from riotwatcher import LolWatcher, ApiError
import time

connector = Connector()

f = open("riot-api-code.txt", 'r')
riotApiCode = f.readline()
f.close()
lol_watcher = LolWatcher(riotApiCode)


async def club_inactives(club_name):
    response = await connector.request('get', '/lol-clubs/v1/clubs/membership')
    response = await response.json()
    summoners = {}
    index = 0
    for i in range(len(response["activeClubs"])):
        if response["activeClubs"][i]["tag"].casefold() == club_name.casefold():
            index = i
            break
    i = 0
    json_members = response["activeClubs"][index]["members"]["activeMembers"]
    for friend in json_members:
        try:
            summoner = lol_watcher.summoner.by_name('euw1', friend['summonerName'])
            summoners[summoner['name']] = str(
                time.strftime('%Y-%m-%d', time.localtime(summoner['revisionDate'] // 1000)))
        except ApiError as err:
            if err.response.status_code == 429:
                print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
            elif err.response.status_code == 404:
                print("Summoner " + friend['gameName'] + " name not found.")
            else:
                raise
        print(str(i) + ": " + friend['summonerName'] + " done")
        i += 1
    sorted_summs = sorted(summoners.items(), key=lambda x: x[1])
    f = open("resources/00" + club_name + ".txt", "w+", encoding='utf-8')
    for friend in sorted_summs:
        print(friend[1] + "\t" + friend[0])
        f.write(friend[1] + "\t" + friend[0] + "\n")
    f.close()
    print("Finished, total: " + str(len(json_members)))


async def friendlist_inactives():
    response = await connector.request('get', '/lol-chat/v1/friends')
    response = await response.json()
    # print(json.dumps(response, indent=4, sort_keys=True))
    print(len(response))
    summoners = {}
    i = 0
    for friend in response:
        try:
            summoner = lol_watcher.summoner.by_name('euw1', friend['gameName'])
            summoners[summoner['name']] = str(
                time.strftime('%Y-%m-%d', time.localtime(summoner['revisionDate'] // 1000)))
        except ApiError as err:
            if err.response.status_code == 429:
                print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
            elif err.response.status_code == 404:
                print("Summoner " + friend['gameName'] + " name not found.")
            else:
                raise
        print(str(i) + ": " + friend['gameName'] + " done")
        i += 1
    sorted_summs = sorted(summoners.items(), key=lambda x: x[1])
    f = open("resources/00inactives.txt", "w+", encoding='utf-8')
    for friend in sorted_summs:
        print(friend[1] + "\t" + friend[0])
        f.write(friend[1] + "\t" + friend[0] + "\n")
    f.close()
    print("Finished, total: " + str(len(response)))


async def set_icon():
    # 55 29 66
    icon = await connector.request('put', '/lol-summoner/v1/current-summoner/icon', data=dumps({'profileIconId': 29}))
    # if HTTP status code is 201 the icon was applied successfully
    if icon.status == 201:
        print(f'Chinese icon was set correctly.')
    else:
        print('Unknown problem, the icon was not set.')


# fired when LCU API is ready to be used
@connector.event
async def connect():
    print('LCU API is ready to be used.')

    # check if the user is already logged into his account
    summoner = await connector.request('get', '/lol-summoner/v1/current-summoner')
    if summoner.status == 200:
        data = await summoner.json()

        # calls login method and update login.left_calls to 0
        # when login.left_calls is 0 the function can't be fired any more neither by websocket nor manually
        await login(None, None, data)

    else:
        print('Please login into your account to change your icon...')


# fired when League Client is closed (or disconnected from websocket)
@connector.event
async def disconnect():
    print('The client have been closed!')


# subscribe to the login websocket event, and calls the function only one time
@connector.ws_events(['/lol-summoner/v1/current-summoner'], event_types=['Update'], max_calls=1)
async def login(typ, uri, data):
    print('Logged as', data['displayName'])
    # await friendlist_inactives()
    await club_inactives("Nami")
    # await set_icon()


# opens websocket connection (may be used to wait until the client is closed)
connector.listen()
# starts everything
connector.start()
