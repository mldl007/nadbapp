import pymongo
import os
import pandas as pd


class DBOperations:
    """
    Reads news from MongoDB
    """
    def __init__(self):
        self.url = os.getenv('DB_URL')
        self.database = "rss_news_db"
        self.collection = "rss_news"
        self.__client = None
        self.__error = 0

    def __connect(self):
        try:
            self.__client = pymongo.MongoClient(self.url)
            _ = self.__client.list_database_names()
        except Exception as conn_exception:
            self.__error = 1
            self.__client = None
            raise

    def __read(self):
        try:
            db = self.__client[self.database]
            coll = db[self.collection]
            docs = []
            for doc in coll.find():
                docs.append(doc)
            rss_df = pd.DataFrame(docs)
        except Exception as insert_err:
            self.__error = 1
            rss_df = pd.DataFrame({'_id': '', 'title': '', 'url': '',
                                   'description': '', 'parsed_date': '',
                                   'src': ''}, index=[0])
        return rss_df

    def __close_connection(self):
        if self.__client is not None:
            self.__client.close()
            self.__client = None

    def read_news_from_db(self):
        rss_df = pd.DataFrame({'_id': '', 'title': '', 'url': '',
                               'description': '', 'parsed_date': '',
                               'src': ''}, index=[0])
        if self.url is not None:
            if self.__error == 0:
                self.__connect()
            if self.__error == 0:
                rss_df = self.__read()
            if self.__error == 0:
                print("Read Successful")
            if self.__client is not None:
                self.__close_connection()
        return rss_df
