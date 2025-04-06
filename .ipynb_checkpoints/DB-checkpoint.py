import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from collections import defaultdict
from itertools import combinations
from tqdm import tqdm


# tier, division 목록
tiers = ['CHALLENGER', 'GRANDMASTER', 'MASTER', 'DIAMOND', 'EMERALD', 'PLATINUM', 'GOLD', 'SILVER', 'BRONZE']
high_tier = tiers[:3]
low_tier = tiers[3:]
division = ['I', 'II', 'III', 'IV']

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

class Load:
    def __init__(self):
        load_dotenv()
        mongo_uri = os.getenv('MONGO_URI')

        if not mongo_uri:
            raise ValueError("MongoDB URI가 .env 파일에 설정되지 않았습니다.")

        client = MongoClient(mongo_uri)
        self.db = client['lol_data_hub']

    def get_all_collections(self):
        collections = self.db.list_collection_names()
        for collection in tqdm(collections, desc="Retrieving collections"):
            print(collection)

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def matches(self):
        return self.db['matches']

    def timelines(self):
        return self.db['timelines']

    def summoners(self):
        return self.db['summoners']

    def summoners_match_list(self):
        '''
        :return: {gameName, tagLine, match_ids}
        '''
        summoners_collection = self.summoners()
        dict_list = summoners_collection.find({}, {'_id':0, 'gameName':1, 'tagLine':1, 'match_ids':1})

        return dict_list

    def matchId_list(self):
        '''
        :return: [match_id]
        '''
        matches_collection = self.matches()
        dict_list = matches_collection.find({},
            {'game_id':1, '_id':0}
        )
        
        result = [item['game_id'] for item in dict_list]
        
        if result:
            return result
        else:
            return None
    
    def find_match(self, match_id):
        '''
        match_id에 따른 매치 정보 추출
        :return: matches.info
        '''
        matches_collection = self.matches()
        result = matches_collection.find_one(
            {'game_id':match_id}
        )

        if result:
            return result['info']
        else:
            return None

    def find_timelines(self, match_id):
        '''
        match_id에 따른 매치 정보 추출
        :return: timelines.info.frames
        participants index는 matches index + 1
        '''
        timeline_collection = self.timelines()
        result = timeline_collection.find_one(
            {'info.gameId': match_id}
        )
    

        if result:
            return result['info']['frames']
        else:
            return None

    def find_summoner(self, gameName, tagLine):
        '''
        gameName, tagLine에 따른 매치 정보 추출
        :return: {gameName, tagLine, match_ids}
        '''
        summoners_collection = self.summoners()
        dict_list = summoners_collection.find_one({'gameName': gameName, 'tagLine': tagLine})

        return dict_list