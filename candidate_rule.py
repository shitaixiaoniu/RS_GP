#-*- coding:utf-8-*
import sys
import os
import rs_utils as utils
import data_model as dm
import datetime
import numpy as np
from item_cluster_in_cate import ICIC 
from base_candidate_with_item_cluster import BaseCIC


class CR(BaseCIC):
    """
    根据最近有行为cate,以cate下的item作为候选
    
    """
    def candidate_items_by_recent_cate(self,fout_str):
        user_score_dict = self.splite_user_model.user_score_dict
        user_history_dict = self.splite_user_model.user_history_dict
        min_score = 2
        min_item_num = 400
        fout = open(fout_str,'w')
        i = 0
        for user in user_score_dict:
            i +=1
            if i%1000 == 0:
                print i
            candidate_item_set = set()
            attr = user_score_dict[user]
            #过滤用户,分数低于阈值的过滤
            if attr.get_score() <= min_score:
                continue
            for cate in attr.get_all_cates():
                #过滤分数低于阈值的cate
                if attr.get_cate_score(cate) <= min_score:
                    continue
                """
                #cate的item数小于min_item_num 的cate 不要
                if len(cate_dict[cate]) <= min_item_num:
                    continue
                candidate_item_set |= cate_dict[cate]
                """
                candidate_item_set |=self.__get_candidate_item(attr,cate)
            #去掉用户所以有行为的item
            candidate_item_set -= user_history_dict[user]
            print >> fout,'%s,%s' %(user,'#'.join(candidate_item_set))
        fout.close()
        print 'two done'
    def __get_candidate_item(self,attr,cate):
        cate_dict = self.ci_model.cate_dict
        rs_num = 3000
        need_item_num = int(rs_num* attr.get_cate_prob(cate))
        if need_item_num  >= len(cate_dict[cate]):
            return cate_dict[cate]
        else:
            #对cate 下item 聚类
            item_labels_dict = self._cluster_item_in_cate(cate) 
            #根据历史行为 计算对各子聚类的喜好度
            label_score_dict = dict()
            for item in attr.get_items_by_cate(cate):
                label = str(item_labels_dict[item])
                if label  == '-1':
                    continue
                label_score_dict.setdefault(label,0)
                label_score_dict[label] += attr.get_item_score(item) 
            sorted_label_list = sorted(label_score_dict.items(), key=lambda x: x[1], reverse=True)
            label_item_dict = item2label(item_labels_dict)
            #根据由高到低排序的子类依次添加其对应的item 作为候选item
            candidate_item_set = set()
            for label,val in sorted_label_list:
                candidate_item_set |= label_item_dict[label]
                if len(candidate_item_set) >= need_item_num:
                    break
            return candidate_item_set

def item2label(item_labels_dict):
    label_item_dict = dict()
    for item in item_labels_dict:
        label = str(item_labels_dict[item])
        label_item_dict.setdefault(label,set())
        label_item_dict[label].add(item)
    return label_item_dict

    
def main():
    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
    cf_dir = utils.get_data_dir(utils.FLAG_CF)
    rule_dir = utils.get_data_dir(utils.FLAG_RULE)
    fraw_str = '%s/data_%s_%s' %(data_dir,utils.DATE_BEGIN.strftime('%m%d'),utils.DATE_END.strftime('%m%d'))  
    fitem_str = '%s/item' %(data_dir)
    fres_cate_str = '%s/test_candidate_rule_cate_%s_%s' %(rule_dir,utils.DATE_SPLIT.strftime('%m%d'),utils.DATE_END.strftime('%m%d'))
    fbuy_str = '%s/data_buy_%s'%(data_dir,utils.DATE_NEXT.strftime('%m%d'))
    bcr = CR(fraw_str,utils.DATE_SPLIT,fitem_str)
    bcr.candidate_items_by_recent_cate(fres_cate_str)
    utils.evaluate_res_except_history(fres_cate_str,fbuy_str,True,fraw_str)
    
if __name__ == '__main__':
    main()
