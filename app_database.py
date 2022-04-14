import pymongo
import threading
import os

from kucoin.client import Market
from app_exception_control import ExceptionC

class Database:

    def __init__(self):

        self.client = pymongo.MongoClient(os.environ['database_uri'])
        self.database_mongodb = self.client[os.environ['database']]
        self.client_market = Market()
        self.day_in_minutes = 60*24


    def clear(self):

        for name in self.database_mongodb.list_collection_names():

            self.database_mongodb[name].drop()


    def get_currency_days_before(self, currency, days):

        self.update_currency_days_before(currency, days)

        collection = self.database_mongodb[currency]

        tlast = int(list(collection.find().sort('time'))[-1]['time'])

        data = []

        for object in reversed(list(collection[currency].find({'time': {'$gt': tlast - int(days) * self.day_in_minutes}}).sort('time'))):

            data.append(object['price'])

        return data


    def get_currency(self, currency):

        self.update_currency(currency)

        data = []

        for object in reversed(list(self.database_mongodb[currency].find().sort('time'))):

            data.append(object['price'])

        return data


    def delete_currency_days_before(self, currency, days):

        self.update_currency(currency)

        collection = self.database_mongodb[currency]

        tlast = int(list(collection.find().sort('time'))[-1]['time'])

        collection.delete_many({'time': {'$lt': tlast - int(days) * self.day_in_minutes + 1}})


    def delete_currency(self, currency):

        collection = self.database_mongodb[currency]

        collection.drop()

    
    def update_currency_days_before(self, currency, days):

        self.update_currency(currency)

        collection = self.database_mongodb[currency]
        
        tfirst = int(list(collection.find().sort('time'))[0]['time'])
        tlast = int(list(collection.find().sort('time'))[-1]['time'])

        tstart = tlast - int(days) * self.day_in_minutes + 1
        tend = tfirst-1

        if tstart <= tend:

            collection.insert_many(self.get_minutes_prices(currency, tstart, tend))


    def update_currency(self, currency):

        collection = self.database_mongodb[currency]

        if collection.find_one({}) == None:

            collection.insert_one(self.get_last_minutes_prices(currency))

        tlast = int(list(collection.find().sort('time'))[-1]['time'])
        tnow = self.get_server_time_minutes()

        tstart = tlast+1
        tend = tnow-1

        if tstart <= tend:

            collection.insert_many(self.get_minutes_prices(currency, tstart, tend))


    def get_server_time_minutes(self):

        return ExceptionC.with_send(self.client_market.get_server_timestamp) // 1000 // 60


    def get_last_minutes_prices(self, currency):

        tnow = self.get_server_time_minutes()

        data = self.get_minutes_prices(currency, tnow-1, tnow-1)

        return data[0]
        

    def get_minutes_prices(self, currency, start, end):

        results = {}


        def get_kline(currency, start, end):
        
            while True:

                try:

                    results[start] = self.client_market.get_kline(symbol = currency + '-USDT', kline_type = '1min', startAt = str(start*60), endAt = str(end*60+1))

                    break

                except:

                    pass


        mthreads = []

        for i in reversed(range(start, end+1, self.day_in_minutes)):

            tstart = i
            tend = min(i + self.day_in_minutes - 1, end)

            mthreads.append(threading.Thread(target=get_kline, args=(currency, tstart, tend,)))

        for i in range(len(mthreads)):

            mthreads[i].start()

        for i in range(len(mthreads)):

            mthreads[i].join()

        data = []

        for i in reversed(range(start, end+1, self.day_in_minutes)):

            for j in range(len(results[i])):

                data.append({'time': str(int(results[i][j][0]) // 60), 'price': results[i][j][2]})

        return data


database = Database()