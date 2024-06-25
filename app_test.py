from flask import Flask, redirect, request, url_for
import requests

app = Flask(__name__)

# 設定 OAuth 參數
client_id = '128710'
client_secret = '17c4ffa2cc7e5447d6ea221ea174f682a9a4b3c2'
redirect_uri = 'http://localhost:5000/callback'

authorization_base_url = 'https://www.strava.com/oauth/authorize'
token_url = 'https://www.strava.com/oauth/token'
athlete_url = 'https://www.strava.com/api/v3/athlete'


@app.route('/')
def index():
    return '''
    <a href="/login">Connect with Strava</a>
    '''

@app.route('/login')
def login():
    scope = 'read'
    authorization_url = f"{authorization_base_url}?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        try:
            # 交換授權碼以獲取訪問令牌
            token_response = requests.post(token_url, data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code'
            })
            token_response.raise_for_status()
            token_json = token_response.json()
            access_token = token_json.get('access_token')

            # 使用 access token 獲取用戶資料
            athlete_response = requests.get(athlete_url, headers={
                'Authorization': f'Bearer {access_token}'
            })
            athlete_response.raise_for_status()
            athlete_json = athlete_response.json()

            return f"User Data: {athlete_json}"
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {str(e)}"
    else:
        return 'Error: No code provided'



if __name__ == '__main__':
    app.run(debug=True)
