#-*- coding:utf-8 -*-
import sys
import os
import datetime
import math
import scikits.crab as crab 
def set_pair_attr_default_dict():
    attr_dict = dict()
    attr_dict['cate'] =''
    attr_dict['rate'] = 0
    attr_dict['lasttime'] = datetime.datetime(2014,11,18)
    return attr_dict
def update_item_attr_dict(attr_dict,cols):
    #user_id,item_id,behavior_type,postion,cate,time
    attr_dict['cate'] = cols[-2]
    #点击行为
    if cols[2]=='1'and attr_dict['rate'] <2:
        attr_dict['rate'] += 1
    elif cols[2] != '1' and attr_dict['rate'] < int(cols[2])+1:
        attr_dict['rate'] = int(cols[2])+1
    cur_date = datetime.datetime.strptime(cols[-1],'%Y-%m-%d %H')
    if cur_date > attr_dict['lasttime']:
        attr_dict['lasttime'] = cur_date

def dict2str(attr_dict):
    attr_list = [str(attr_dict[key]) for key in ['cate','rate','lasttime']]
    return ','.join(attr_list)
"""
构建物品评分数据
点击一次：1
点击>=2:2
收藏：3
加购物车：4
购买：5
取最高分item的分数
输入：data_[beg_date]_[end_date]
输出：userid,itemid,cate,rate,last_time(最后一次item的行为时间)
"""
def build_item_rate_data(fin_str,fout_str):
    pair_dict = dict()
    with open(fin_str) as fin:
        for line in fin:
            #user_id,item_id,behavior_type,postion,cate,time
            cols = line.strip().split(',')
            pair = '%s#%s' %(cols[0],cols[1])
            pair_dict.setdefault(pair,set_pair_attr_default_dict())
            #更新attr
            update_item_attr_dict(pair_dict[pair],cols)
    fout = open(fout_str,'w')
    for pair in pair_dict:
        user,item = pair.split('#')
        print >> fout,'%s,%s,%s' %(user,item, dict2str(pair_dict[pair]))
    fout.close()
"""
input :fin_str:
    userid,itemid,cate,rate,last_time(最后一次item的行为时间) 
    theta: 时间衰减函数 rate = rate * exp(-theta * t) t为到特定时间【12.17】的天数
output:crab.Bunch
    'data', the full data in the shape:
        {user_id: { item_id: (rating, timestamp),
            item_id2: (rating2, timestamp2) }, ...} and
    'user_ids': the user labels with respective ids in the shape:               {user_id: label, user_id2: label2, ...} and
    'item_ids': the item labels with respective ids in the shape:
             {item_id: label, item_id2: label2, ...} and
    DESCR, the full description of the dataset.
"""

def load_rate_data(fin_str,theta = 0.0)
    #设为2014-12-17 23
    split_date = datetime.datetime(2014,12,17,23)
    item_ids_list = []
    user_ids_list = []
    data_dict= dict()
    with open(fin_str) as fin:
        for line in fin:
        #userid,itemid,cate,rate,lasttime
            cols = line.strip().split(',')
            cur_date = datetime.datetime.strptime(cols[-1],'%Y-%m-%s %H:%M:%S')
            days_delta = (split_date-cur_date).days
            #带时间衰减的分数
            rate = int(cols[-2]) * math.exp(-theta * days_delta)
            if cols[0] not in user_ids_list:
                user_ids_list.append(cols[0])
            if cols[1] not in item_ids_list:
                item_ids_list.append(cols[1])
            u_ix = user_ids_list.index(cols[0])+1
            i_ix = item_ids_list.index(cols[1])+1
            data_dict.setdefault(u_ix,dict())
            data_dict[u_ix][i_ix] = rate

    item_dict = dict()
    for no,item_id in enumerate(item_ids_list):
        item_dict[no+1] = item_id

    user_dict = dict()
    for no ,user_id in enumerate(user_ids_list):
        user_dict[no+1] = user_id
    return crab.datasets.Bunch(data = data_dict, item_ids = item_dict, user_ids=user_dict,DESCR='user_item_rate')
"""
user_base_cf 产生候选item
"""
def predict_user_based(raw_data):
    model = crab.models.MatrixPreferenceDataModel(raw_data.data)
    # top k先暂时不要
    similarity = crab.similarities.UserSimilarity(model,crab.metrics.pearson_correlation)
    # 统计一下用户的相似用户的分布情况
    print >> sys.stdout,'user num %d' %(len(raw_data.user_ids))
    simi_num_dict =
    for u_ix in raw_data.user_ids:
        simi_list = similarity[u_ix]

    recommender = crab.recommenders.knn.UserBasedRecommender(model,similarity,with_prefercence = True)
    for u_ix in raw_data.user_ids:
        # 推荐的 howmany 先暂时不填
        rs_list = recommender.recommend(u_ix)

