from flask import Flask, render_template, json, make_response, request
from collections import defaultdict, Counter, OrderedDict
from datetime import datetime
from urllib import quote
import requests
import os
from flask_sillywalk import SwaggerApiRegistry, SwaggerRegistryError, ApiErrorResponse, ApiParameter

app = Flask(__name__)

url = os.environ.get("URL", "0.0.0.0:8891")
registry = SwaggerApiRegistry(app, baseurl="http://{0}/api/hi".format(url))
register = registry.register
registerModel = registry.registerModel

@app.route('/')
def rs():
    hit_r, today = common()

    return render_template("statics.html",
                                hit_r=hit_r,
                                preview = 'img',
                                month=today.month,
                                day= today.day
                           )


@app.route('/h_b/<s>')
def h_age_rs(s):
    today = datetime.today()
    interval="H"
    limit=today.hour+25 # ago -24H

    std_r = orderedDicHitRankForAge(b=15, s=s, interval=interval, limit=limit)
    date_band = return_map_by_graph(std_r, 0)
    hit_r = return_map_by_graph(std_r, 1)

    return render_template("hourly_age_s.html",
                           hit_r=hit_r,
                           month=today.month,
                           day=today.day,
                           s=s,
                           date_band=date_band
                           )


@app.route('/b/<s>')
def age_rs(s):
    today = datetime.today()
    limit =  today.day

    hit_r_15 = orderedDicHitRankForAge(b=15, s=s, limit=limit)
    hit_r_24 = orderedDicHitRankForAge(b=24, s=s, limit=limit)

    b = [15,24,27,37,47,57]
    return render_template("age_s.html",
                           hit_r=[hit_r_15, hit_r_24],
                           month=today.month,
                           day=today.day,
                           s=s,
                           b=b
                           )


def common(interval="d"):
    today = datetime.today()

    limit=today.day
    url = "http://sweb.w.com:5000/counter/hi/test/s_r/r"
    params = {"k":50, "interval":interval, "limit":limit}

    data=requests.get(url, params=params).content
    json_data = json.loads(data)['data']

    hit_r_map = []
    for dd in json_data:
        time = dd['time']
        for r in dd['rs']:
            score = r['score']
            url = r['id']
            hit_r_map.append( (url, (time.split()[0], score) ) )

    hit_r = orderedDictHitRank(hit_r_map)

    return hit_r, today


def orderedDicHitRankForAge(b=30, s="F", interval="d", limit='1'):
    url = "http://sweb.w.com:5000/counter/hi/test/s_r/r"
    params = {"k":50, "interval":interval, "limit":limit, ":b":b, ":s":s}

    data=requests.get(url, params=params).content
    json_data = json.loads(data)['data']
    if interval == 'd': return  dayly(json_data)
    else: return hourly(json_data)

def dayly(json_data):
    hit_r_map = []
    for dd in json_data:
        time = dd['time']
        for r in dd['rs']:
            score = r['score']
            url = r['id']
            hit_r_map.append( (url, (time.split()[0], score) ) )

    hit_r = orderedDictHitRank(hit_r_map)
    return hit_r


def hourly(json_data):
    hit_r_map = []
    for dd in json_data:
        time = dd['time']
        total = dd['total']
        hit_r_map.append( ( time.encode("UTF-8"), total) )

    return hit_r_map


def return_map_by_graph(hit_r_map, type=0):
    h_map = []
    for time in hit_r_map:
        if type == 0:
            dt = time[type].split('-')
            dt_arr = ( dt[1], dt[2:][0])
            h_map.append( "-".join(dt_arr) )
        else:
            h_map.append(time[type])

    return h_map


def orderedDictHitRank(map_list):
    d = defaultdict(list)
    for k,v in map_list:
        d[k].append(v)

    return OrderedDict(sorted(d.items(), key=lambda t: len(t[1]),reverse=True ) ).items()

class HappyBirthdayException(Exception):
    pass


@registerModel()
class SomeCrazyClass(object):
    """This is just the most crazy class!"""

    def __init__(self, name, age, birthday="tomorrow"):
        self.name = name
        self.age = age
        self.birthday = birthday

    def say_happy_birthday(self):
        raise HappyBirthdayException("Chances are it's not your birthday.")


@register(
    "/api/hi/cheese/<cheeseName>",
    parameters=[
        ApiParameter(
            name="cheeseName",
            description="The name of the cheese to fetch",
            required=True,
            dataType="str",
            paramType="path",
            allowMultiple=False)],
    notes='For getting cheese, you know...',
    responseMessages=[
        ApiErrorResponse(400, "Sorry, we're fresh out of that cheese."),
        ApiErrorResponse(418, "I'm actually a teapot")
    ])
def get_cheese(cheeseName):
    """Gets cheese, just like the name says."""
    return json.dumps(
        {"response": "OK", "message": "Sorry, we're fresh out of {0}!".format(
            cheeseName)
        })


@register(
    "/api/hi/holyHandGrenade/<number>",
    method="GET",
    parameters=[
        ApiParameter(
            name="number",
            description="The number of hand grenades to get",
            required=True,
            dataType="int",
            paramType="path",
            allowMultiple=False)])
def get_a_holy_hand_grenade(number):
    """Gets one or more holy hand grenades, just like the name says."""
    return json.dumps("Fetching {0} holy hand grenades".format(number))


@register(
    "/api/hi/holyHandGrenade/<number>",
    method="POST",
    parameters=[
        ApiParameter(
            name="number",
            description="The number of seconds to wait",
            required=True,
            dataType="int",
            paramType="path",
            allowMultiple=False),
        ApiParameter(
            name="target",
            description="At whom should I thrown the hand grenade?",
            required=False,
            dataType="str",
            paramType="query",
            allowMultiple=False)])
def toss_the_grenade(number):
    """Toss the holy hand grenade after {number} seconds."""
    target = request.args.get("target", "FOO")
    return json.dumps(
        "Waiting {0} seconds to toss the grenade at {1}.".format(
            number,
            target))


# @app.after_request
# def after_request(data):
#     response = make_response(data)
#     response.headers['Content-Type'] = 'application/json'
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers[
#         'Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS , PUT'
#     return response

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=8819)

