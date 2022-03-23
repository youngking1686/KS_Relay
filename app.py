from flask import Flask, request, render_template, jsonify
import asyncio, aiohttp, requests

app = Flask(__name__)
webhooks_urls = ['https://pa-ks1.herokuapp.com', 'https://pa-po-ks.herokuapp.com'] ##[me, pooranan]

async def post(post_url, payload, session):
    async with session.post(post_url, data = payload) as resp:
        resps = await resp.json(content_type=None)
        return resps['message']

async def pa_post(payload):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in webhooks_urls:
            try:
                post_url = url + '/ks_webhook'
                tasks.append(asyncio.ensure_future(post(post_url, payload, session)))
            except:
                continue
        all_resps = await asyncio.gather(*tasks)
        print(all_resps)
        messa = 'posted: ' + ": ".join(all_resps)
        return messa

@app.route('/pa_ks_wbhr',  methods=['POST'])
def pa_ks_wbhr():
    payload = request.data
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) #only for windows
    # asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy()) #For linux CHANGE before moving the code!
    resp = asyncio.run(pa_post(payload))
    return resp

@app.route('/pa_ks_heartbeat')
def pa_ks_heartbeat():
    responses = []
    for url in webhooks_urls:
        url1 = url + '/ks_check'
        resp = requests.post(url1, data=None)
        try:
            responses.append(resp.json())
        except:
            responses.append(f"No response from {url}")
    return jsonify(responses)

@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)