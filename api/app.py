from flask import Flask, render_template, redirect, request, abort, send_from_directory
from supabase import create_client, Client
from flask_caching import Cache
from dotenv import load_dotenv
from os import getenv

load_dotenv()

config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

url_base = getenv("URL_BASE")
secret_key = getenv("SECRET_KEY")

supabase_client: Client = create_client(url_base, secret_key)

app = Flask(__name__, template_folder='templates')

app.config.from_mapping(config)
cache = Cache(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/travel-time-minimization')
def travel_time_minimization():
    return redirect('https://travel-time-minimization.vercel.app')

@app.errorhandler(404)
def page_404(_):
    return render_template('page_404.html')

@app.route('/videos/', defaults={'name': None, 'season': None, 'episode': None, 'part': None})
@app.route('/videos/name=<name>/', defaults={'season': None, 'episode': None, 'part': None})
@app.route('/videos/name=<name>/part=<part>/', defaults={'season': None, 'episode': None})
@app.route('/videos/name=<name>/season=<season>/', defaults={'episode': None, 'part': None})
@app.route('/videos/name=<name>/season=<season>/episode=<episode>/', defaults={'part': None})
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
    

    

    
