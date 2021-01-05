from riotwatcher import LolWatcher
import time

f = open("resources/00inactives.txt", "w+")
lol_watcher = LolWatcher('')
print("Hey")

for i in range(2):
    summoner = lol_watcher.summoner.by_name('euw1', 'Thorasine')
    print(str(i) + ": " + summoner['name'] + '\t' +
          time.strftime('%Y-%m-%d',time.localtime(summoner['revisionDate'] // 1000)))
    f.write(str(i) + ": " + summoner['name'] + '\t' +
            time.strftime('%Y-%m-%d',time.localtime(summoner['revisionDate'] // 1000)) + '\n')
f.close()
