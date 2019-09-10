import requests, googlehomepush, time, datetime, json, os, codecs, logging

custom_alarms = {'08:00': 'Yusuf and Mariam, we have to leave now',
                 '07:30': 'Attention please, we have 30 minutes'}

# We don't want to read prayer times from the web all the time, so we cache it
# for every day
current_dir = os.path.abspath(os.path.dirname(__file__))
today = datetime.datetime.today()
today_file = os.path.join(current_dir, today.strftime('%d-%m-%Y.prayer_times'))

logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler(os.path.join(current_dir, today.strftime('%d-%m-%Y.log')))
handler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

logger.info('Today file: %s', today_file)

# Delete old prayer times cache files
for f in os.listdir(current_dir):
    if f.endswith('.prayer_times') and os.path.abspath(f) != today_file:
        logging.info('Deleting: %s', f)
        os.remove(f)

if os.path.exists(today_file):
    logger.info('Today file exists. Reading from it.')
    prayer_times = json.load(codecs.open(today_file, encoding='utf-8'))
else:
    logger.info('Reading prayer times from the server')
    url = today.strftime(
            'http://api.aladhan.com/v1/timings/'
            '%d-%m-%Y'
            '?latitude=47.3718341'
            '&longitude=8.5382787'
            '&method=2')
    prayer_times = requests.get(url).json()
    json.dump(prayer_times, codecs.open(today_file, 'wb', encoding='utf-8'))

# Remove non-azan timing
for p in ['Sunset', 'Midnight', 'Imsak', 'Sunrise']:
    del prayer_times['data']['timings'][p]

# If now is a prayer time, then cast azan sound
now = datetime.datetime.now().strftime('%H:%M')
gh = googlehomepush.GoogleHome('Kitchen speaker')
if now in prayer_times['data']['timings'].values():
    logger.info('Casting azan at: %s', now)
    gh.cc.set_volume(.35)
    gh.play(
        'https://ia800303.us.archive.org/5/items/Naseer.Al.Qtami.Azan/'
        'Naseer.Al.Qtami.Azan.mp3',
        'audio/mp3')
    gh.cc.set_volume(.5)
elif now in custom_alarms:
    gh.say(custom_alarms[now])
else:
    logger.info('%s is not azan time', now)
