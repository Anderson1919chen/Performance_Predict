import numpy as np
import model

from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__) #建立Application 物件
CORS(app)

#建立首頁回應方式
@app.route("/")
def index(): 
    return "Hello test"

@app.route('/predict', methods = ['POST'])
def postInput():
    # 取得前端數值
    insertValues = request.get_json()
    x1 = insertValues['distance']
    x2 = insertValues['weather']
    x3 = insertValues['temperature']
    input = np.array([x1, x2, x3])
    print(input)

    return jsonify({'return': 'ok!'})






if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 3000, debug = True)