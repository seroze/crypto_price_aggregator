# Crypto aggregator

User Requirements: 
- Provide a UI where user can list down an instrument and it'll show it's price from kraken,coinbase, bitstamp
- Instrument price should be updated every 2s
- Store the price history in a database for analytics purpose 

Frontend: 
- UI page that takes in a symbol and displays it's live price from 3 sources
- UI page that takes in a symbol and displays it's price history 

Backend: 
- Api Interface
  - websocket api for displaying live price 
    - ws:/aggregator/v1/live_prices/symbols/{symbol} 
    
  - rest api for displaying historical price / should we use websocket here too Eg: to show last 30 prices
    - GET /aggregator/v1/get_historical_prices/symbols/{symbol}

- Component design
  - backend will have three async loops. 
    - async loop 1
      - fetch price for symbol from each of the three exchanges. Instead of waiting for one API call to finish before calling the next we wait for the slowest one to respond. 
        - what if one of the api is not responding (we'll timeout. Timout = 2s)
    - async loop 2 
      - async loop 1 will push price to an inmemory queue and this async loop 2 will dump it to sqlite database 
    - async loop 3 
      - async loop 3 will consume the same in-memory queue and publish the price to UI
