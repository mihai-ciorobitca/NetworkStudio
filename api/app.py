from flask import Flask, render_template, redirect, request, abort, send_from_directory
from supabase import create_client, Client
from flask_caching import Cache

config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

URL_BASE = 'https://qfvhxwctxqrtemtysrrx.supabase.co'
SECRET_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFmdmh4d2N0eHFydGVtdHlzcnJ4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxOTY2MzAzMiwiZXhwIjoyMDM1MjM5MDMyfQ.JZ9YSF8o-Jgmxv0ePW4suSsYyD_KmPIpgxqrPrjQpNA'

supabase_client: Client = create_client(URL_BASE, SECRET_KEY)

app = Flask(__name__, template_folder='templates')

app.config.from_mapping(config)
cache = Cache(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/travel-time-minimization')
def travel_time_minimization():
    return redirect('https://travel-time-minimization.vercel.app')

@app.route('/videos/', defaults={'name': None, 'season': None, 'episode': None, 'part': None})
@app.route('/videos/name/<name>/', defaults={'season': None, 'episode': None, 'part': None})
@app.route('/videos/name/<name>/part/<part>/', defaults={'season': None, 'episode': None})
@app.route('/videos/name/<name>/season/<season>/', defaults={'episode': None, 'part': None})
@app.route('/videos/name/<name>/season/<season>/episode/<episode>/', defaults={'part': None})
@cache.cached(timeout=10)
def video_route(name, season, episode, part):
    query = supabase_client.table('movies').select('*')
    
    if name:
        query = query.eq('name', name)
        if season:
            query = query.eq('season', season)
            if episode:
                query = query.eq('episode', episode)
                response = query.execute()
                return render_template('video.html', name=name, season=season, episode=episode, url=response.data[0]['link'])
            response = query.execute()
            episodes = sorted(list(set(map(lambda x: x["episode"], response.data))))
            return render_template('episodes.html', episodes=episodes, name=name, season=season)
        if part:
            query = query.eq('part', part)
            response = query.execute()
            return render_template('video.html', name=name, part=part, url=response.data[0]['link'])
        response = query.execute()
        if response.data[0].get('season') is not None:
            seasons = sorted(list(set(map(lambda x: x["season"], response.data))))
            return render_template('seasons.html', seasons=seasons, name=name)
        parts = sorted(list(set(map(lambda x: x["part"], response.data))))
        return render_template('parts.html', parts=parts, name=name)
    response = query.execute()
    names = sorted(list(set(map(lambda x: x["name"], response.data))))
    return render_template('names.html', names=names)
    

    

    
