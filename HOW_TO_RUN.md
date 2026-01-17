# How to run this app 


./.venv/bin/python main.py # this doesn't start the code 

./.venv/bin/uvicorn main:app --reload # this starts the loop, but this is not really need as we have add __main__ method 

source .venv/bin/activate
