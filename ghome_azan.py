import requests, googlecontroller, time, datetime, json, os, sys, codecs, logging

current_dir = os.path.abspath(os.path.dirname(__file__))
today = datetime.datetime.today()

logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler(os.path.join(current_dir, today.strftime('%d-%m-%Y.log')))
handler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

config_file = os.path.join(current_dir, "config.json")

if not os.path.exists(config_file):
    logger.error('config.json does not exist')
    sys.exit(1)

config = json.load(open(config_file))

# We don't want to read prayer times from the web all the time, so we cache it
# for every day

today_file = os.path.join(current_dir, today.strftime('%d-%m-%Y.prayer_times'))
logger.info('Today file: %s', today_file)

# Delete old prayer times cache files
for f in os.listdir(current_dir):
    if f.endswith('.prayer_times') and os.path.abspath(f) != today_file:
        logging.info('Deleting: %s', f)
        os.remove(f)

if os.path.exists(today_file):
    logger.info('Reading prayer times from local file cache.')
    prayer_times = json.load(codecs.open(today_file, encoding='utf-8'))
else:
    logger.info('Reading prayer times from the server')
    url = today.strftime(
            'http://api.aladhan.com/v1/timings/' +
            '%d-%m-%Y' +
            '?latitude=' + config['latitude'] +
            '&longitude=' + config['longitude'] +
            '&method=2')
    prayer_times = requests.get(url).json()
    json.dump(prayer_times, codecs.open(today_file, 'wb', encoding='utf-8'))

# Remove non-azan timing
for p in ['Sunset', 'Midnight', 'Imsak', 'Sunrise']:
    del prayer_times['data']['timings'][p]

# If now is a prayer time, then cast azan sound
now = datetime.datetime.now().strftime('%H:%M')
gh = googlecontroller.GoogleAssistant(host=config['ip_address'])
if now in prayer_times['data']['timings'].values() or '--test' in sys.argv:
    logger.info('Casting azan at: %s', now)
    #gh.volume(35)
    gh.play(
        'https://ia800303.us.archive.org/5/items/Naseer.Al.Qtami.Azan/'
        'Naseer.Al.Qtami.Azan.mp3',
        'audio/mp3')
    #gh.volume(100)
else:
    logger.info('%s is not azan time', now)
