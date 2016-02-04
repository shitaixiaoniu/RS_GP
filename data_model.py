# -*- coding:utf-8 -*-
import datetime
import numpy as np

class UserHistoryDataModel:
    def __init__(self,fin_str,splite_date):
        self.user_score_dict = dict()
        self.user_history_dict= dict()
        with open(fin_str) as fin:
            for line in fin:
                #user,item,be,pos,cate,time
                cols = line.strip().split(',')
                self.user_history_dict.setdefault(cols[0],set())
                self.user_history_dict[cols[0]].add(cols[1])
                cur_date = datetime.datetime.strptime(cols[-1],'%Y-%m-%d %H')
                if cur_date >= splite_date:
                    self.user_score_dict.setdefault(cols[0],UserCateAttr())
                    behavior = int(cols[2])-1
                    #self.user_score_dict[cols[0]].update_cate_info(cols[-2],cols[1],behavior)
                    self.user_score_dict[cols[0]].update_cate_info(cols[-2],cols[1],behavior,cols[-1],cols[3])
        self.user_list = self.user_score_dict.keys()
        self.user_ix_dict = dict()
        for ix,user in enumerate(self.user_list):
            self.user_ix_dict[user] = ix
class CateItemDataModel:
    def __init__(self,fitem_str):
        self.cate_dict = dict()
        with open(fitem_str) as fin:
            for line in fin:
                #item,pos,cate
                cols = line.strip().split(',')
                self.cate_dict.setdefault(cols[-1],set())
                self.cate_dict[cols[-1]].add(cols[0])
class UserCateAttr:
    def __init__(self):
        self.cate_dict = dict()
        self.item_dict = dict()
        #用户的地理位置,每个位置的[lasttime,total_num]
        self.pos_dict  = dict() 
        self.score = None
    def update_cate_info(self,cate,item,behavior,time = None,pos = None):
        self.cate_dict.setdefault(cate,set())
        self.item_dict.setdefault(item,[0]*4)
        self.cate_dict[cate].add(item)
        self.item_dict[item][behavior] +=1
        #计算地理位置
        if pos is not None and pos != '':
            #前4位
            pos = pos[:3]
            if pos not in self.pos_dict:
                self.pos_dict[pos] = [time,1]
            else:
                if time > self.pos_dict[pos][0]:
                    self.pos_dict[pos][0] = time
                self.pos_dict[pos][1] += 1

    def get_cate_score(self,cate):
        score = 0
        if cate not in self.cate_dict:
            return 0
        for item in self.cate_dict[cate]:
            score += self.get_item_score(item) 
        return score
    def get_score(self):
        if self.score is None:
            score = 0
            for cate in self.cate_dict:
                score += self.get_cate_score(cate)
            self.score = score
        return self.score
    def get_score_mean(self):
        return float(self.get_score())/len(self.cate_dict)
    def get_cate_prob(self,cate):
        if cate not in self.cate_dict:
            return 0.0
        total_score = self.get_score()
        cate_prob= self.get_cate_score(cate)/float(total_score)
        return cate_prob 
    def get_all_cates(self):
        return self.cate_dict.keys()
    def get_items_by_cate(self,cate):
        if cate not in self.cate_dict:
            return None
        return self.cate_dict[cate]
    def get_item_score(self,item):
        if item not in self.item_dict:
            return 0
        behavior = np.array(self.item_dict[item])
        #behavior 大于5的限定为5
        #behavior = np.where(behavior>5,5,behavior)
        weight = np.array([1,2,3,4])
        score = np.sum(behavior*weight)
        return score
    def get_last_pos(self):
        if not self.pos_dict:
            return None
        return max(self.pos_dict.items(),key = lambda x :x[1][0])[0]
    def get_most_frequent_pos(self):
        if not self.pos_dict:
            return None
        return max(self.pos_dict.items(),key = lambda x :x[1][1])[0]
    def get_all_pos(self):
        if not self.pos_dict:
            return None
        return self.pos_dict.keys()
