# Amherst Price Patrol

Amherst PricePatrol is a Gen-AI tool that compares grocery prices across stores like Walmart and Aldi. Using real-time data, it helps users find the best deals with fair, quantity-based comparisons.

## Prerequisites

To successfully run this application make sure you have these two api-keys

1. OpenAI

Get your openAI api-key from https://openai.com/index/openai-api/ 

This is a paid service but such is life

2. AgentQL

This one is free and honestly kinda cool!

You can get the api-key from https://www.agentql.com/

## To run the streamlit code

- First clone this repo
```
git clone https://github.com/nithyar15/brokeinamherst.git
```

- Run the requirements.txt file 
```
sudo pip install -r requirements.txt
```

- Once that's done we can run the application!
```
streamlit run app.py
```

-If prompted add your openAI api-key and you should be good to go

## To run the webscraping tool

- First we need to enter the webscraper directory
```
cd webscraper
```

- Install AgentQL using pip and initialize it. When prompted add the api-key
```
sudo pip install agentql
agentql init
```

- Once that's done you can run webscraper.py as a normal python file. The csv file with the data will be generated in the same directory
```
python webscraper.py
```

