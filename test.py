from flask import Flask, render_template, request, jsonify,make_response
from common.logs import log
from common.gemini1 import Gemini_model
import pandas as pd



app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index3.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        df=None
        data= request.get_json()      
        user_message = data.get('message', '').strip()      
        if not user_message:
            return jsonify({'response': "Please enter a valid message."})      
        response = Gemini_model("gemini-1.5-pro").generate_query(user_message)
       
        
        if isinstance(response,list):
          
            df=pd.DataFrame(response).columns.tolist()
            columns_str = ','.join(df)     
                
            if len(df)>1:            
                response_data = {'response': response}
                resp = make_response(jsonify(response_data))
                resp.set_cookie('columns',columns_str, max_age=60*60*24,domain="10.1.35.112:5000")                             
                return resp
            else:
                natural_response=Gemini_model("gemini-1.5-flash").generate_natural_response(response,user_message)               
                
                return jsonify({'response': natural_response})
        elif isinstance(response,dict):

            return jsonify({'response': "No Data Found"})

        else:
            if isinstance(response, str):
               
                return jsonify({'response': response})
            else:
                return jsonify({'response': "An unexpected error occurred. Please try again later."})
        
    except Exception as e:
        log(f"Error in get_response: {e}")
        return jsonify({'response': "An unexpected error occurred. Please try again later."})  
    

    

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0",port=5000)