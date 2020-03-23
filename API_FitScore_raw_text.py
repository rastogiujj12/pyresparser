### Dependencies
from flask import Flask, request, jsonify
from sklearn.externals import joblib
import traceback
import pandas as pd
import numpy as np
import json
from utils import *

# Your API definition
app = Flask(__name__)

@app.route('/fit_score', methods=['POST'])
def fit_score():
    try:
        b_data = request.data
        b_data = b_data.decode()

        data = b_data.split('\n')
        
        a, b = data[0], data[1]
        a = a.replace("\\","")
        b = b.replace("\\","")
        a = a[2:len(a)-2]
        b = b[1:len(b)-2]

        candidate_dataframe = pd.read_json(a)
        JD_dataframe = pd.read_json(b)

        flag = 0
        try:
            scores, report = get_results(candidate_dataframe, JD_dataframe)
            print(scores,'\n\n\n',report)

        except:
            flag = 1

        
        if flag == 0:
            return jsonify({'Results': scores, 'Report': report})
        else:
            return str(-1)

    except:

        return jsonify({'trace': traceback.format_exc()})
    
if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) # This is for a command-line input
    except:
        port = 12345 # If you don't provide any port the port will be set to 12345

    
    app.run(port=port, debug=True)

