from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import pickle
import os

app = FastAPI()

# Define the request body with default dates
class PredictionRequest(BaseModel):
    start_date: str = "1996-04-01"
    end_date: str = "2018-04-01"

# Check if the model file exists
model_file = 'arima_model.pkl'
if not os.path.exists(model_file):
    # Example data for training the model
    # Replace this with your actual data
    data = pd.Series(np.random.randn(100), index=pd.date_range('2000-01-01', periods=100, freq='M'))
    
    # Train the ARIMA model
    model = ARIMA(data, order=(11, 0 , 12))
    model_fit = model.fit()
    
    # Save the model to a file
    with open(model_file, 'wb') as pkl_file:
        pickle.dump(model_fit, pkl_file)
else:
    # Load the trained ARIMA model
    with open(model_file, 'rb') as pkl_file:
        model_fit = pickle.load(pkl_file)

@app.post('/predict/')
def predict(request: PredictionRequest):
    start_date = request.start_date
    end_date = request.end_date

    # Generate date range for prediction
    date_range = pd.date_range(start=start_date, end=end_date, freq='MS')

    # Make predictions
    predictions = model_fit.predict(start=len(model_fit.data.endog), end=len(model_fit.data.endog) + len(date_range) - 1)
    predictions = np.exp(predictions)  # Reverse log transformation if needed

    # Create a response dictionary
    response = {str(date): float(pred) for date, pred in zip(date_range, predictions)}

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)