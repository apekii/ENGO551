import pandas as pd
from sqlalchemy import create_engine

# read csv file
books = pd.read_csv('books.csv')

# check that csv file properly imported as dataframe
print(books.head())

# connect to database
engine = create_engine('postgresql://auruxcdprcbthb:7ff31e2174704980e587ea5a91ef8b11a63b69ffe29b034a6b42a8c7318272e9'
                       '@ec2-3-222-127-58.compute-1.amazonaws.com:5432/da76or2kuol1r')

# import books to table
books.to_sql('books_csv', engine)
