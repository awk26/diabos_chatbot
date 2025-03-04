from flask import Flask, render_template, request, jsonify,make_response
from common.logs import log
from common.gemini1 import Gemini_model
from common.charts import charts
import pandas as pd



app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index3.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        chart = False
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'response': "Please enter a valid message."})

        chart, chart_type = charts(user_message)
        response = Gemini_model("gemini-1.5-pro").generate_query(user_message)

        if isinstance(response, list):
            df = pd.DataFrame(response)
            columns_str = ','.join(df.columns.tolist())

            if len(df.columns) > 1:
                if chart:
                    chart_image = Gemini_model("gemini-1.5-flash").generate_chart(df)
                    
                    response_data = {
                        'response': response,
                        'chartData': chart_image,
                        'chart_type': chart_type
                    }
                else:
                    response_data = {'response': response}

                resp = make_response(jsonify(response_data))
                resp.set_cookie('columns', columns_str, max_age=60*60*24, domain="127.0.0.1")
                return resp

            else:
                natural_response = Gemini_model("gemini-1.5-flash").generate_natural_response(response, user_message)
                return jsonify({'response': natural_response})

        else:
            return jsonify({'response': "No Data Found"})

    except Exception as e:
        print("Error:", e)
        return jsonify({'response': "An unexpected error occurred."})

    

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0",port=5000)