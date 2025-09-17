from flask import Flask,Response,render_template
from flask_caching import Cache
from bs4 import BeautifulSoup
import httpx

app=Flask(__name__)
app.config['CACHE_TYPE']='SimpleCache'
cache=Cache(app)

data=httpx.get("https://tarc.rideralerts.com/InfoPoint/rest/Routes/GetVisibleRoutes").json()
routes=",".join(str(r.get("RouteId")) for r in data)
data=httpx.get("https://tarc.rideralerts.com/InfoPoint/rest/Stops/GetAllStops").json()
stops={s.get("StopId"):[[s.get("Latitude"),s.get("Longitude")],s.get("Name"),1 if s.get("IsTimePoint") else 0] for s in data}

@app.route("/")
def index():
    return render_template("map.html",stops=stops)

@app.route("/tarc.csv")
@cache.cached(timeout=5)
def tarc():
    d=httpx.get("https://tarc.rideralerts.com/InfoPoint/rest/Vehicles/GetAllVehiclesForRoutes?routeIDs=0,"+routes).json()
    return "\n".join(f"{v['Latitude']},{v['Longitude']},{v['RouteId']},{v['Name']},{v['Destination']},{v['Heading']},{v['Speed']},{v['DirectionLong']},{v['LastUpdated'][6:16]}" for v in d)

@app.route('/<int:stop>.csv')
@cache.cached(timeout=5)
def stop(stop):
    if stop not in stops:return "not a stop"
    response=httpx.post("https://tarc.rideralerts.com/InfoPoint/Stops/Detail",json={"StopID":stop})
    if response.status_code==200:
        table=BeautifulSoup(response.content,"html.parser").find("table")
        if table:
            csv=[",".join([h.get_text(strip=True) for h in table.find_all("th")])]
            for row in table.find_all("tr")[1:]:
                csv.append(",".join([c.get_text(strip=True) for c in row.find_all("td")]))
            return Response("\n".join(csv),mimetype="text/plain")
        else:
            return "no stop information"
    return "fetch failed"
