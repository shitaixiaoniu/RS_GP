#-*- coding:utf-8-*
import sys
import rs_utils as utils
import datetime
def candidate_cart_items(fin_str,fout_str):
    fout = open(fout_str,'w')
    user_dict = dict()
    with open(fin_str) as fin:
        for line in fin:
            #user,item,cate,rate,lasttime
            cols = line.strip().split(',')

            if cols[3] == '4':
                user_dict.setdefault(cols[0],[])
                user_dict[cols[0]].append(cols[1])
    for user in user_dict:
        print >> fout,'%s,%s' %(user,'#'.join(user_dict[user]))
    fout.close()
"""
根据最近有行为cate,以cate下的item作为候选
fin_str: data_xxx_xxx
fitem_str:item

"""
def candidate_items_by_recent_cate(fin_str,fitem_str,fout_str):
    splite_date = datetime.datetime(2014,12,8)
    cpair_dict = dict()
    user_history_dict= dict()
    with open(fin_str) as fin:
        for line in fin:
            #user,item,be,pos,cate,time
            cols = line.strip().split(',')
            user_history_dict.setdefault(cols[0],set())
            user_history_dict[cols[0]].add(cols[1])
            cur_date = datetime.datetime.strptime(cols[-1],'%Y-%m-%d %H')
            if cur_date >= splite_date:
                cpair = cols[0]+'#'+cols[-2]
                cpair_dict.setdefault(cpair,[0,0,0,0])
                behavior = int(cols[2])-1
                cpair_dict[cpair][behavior] += 1
    print 'one done'
    cate_dict = dict()
    with open(fitem_str) as fin:
        for line in fin:
            cols = line.strip().split(',')
            #item,pos,cate
            cate_dict.setdefault(cols[-1],set())
            cate_dict[cols[-1]].add(cols[0])
    print 'two done'
    fout = open(fout_str,'w')
    i = 0
    user_candidate_dict = dict()
    for cpair in cpair_dict:
        """
        i +=1
        if i%1000 == 0:
            print i
        """
        #点击数小于3，收藏，购物车，购买都为0 的cate去掉
        if cpair_dict[cpair][0] < 3 and cpair_dict[cpair][1] == 0 \
                and cpair_dict[cpair][2] == 0 and cpair_dict[cpair][3] == 0:
                    continue
        user,cate = cpair.split('#')
        user_candidate_dict.setdefault(user,set())
        user_candidate_dict[user] |= cate_dict[cate]
    print 'three done'
    for user in user_candidate_dict:
        candidate_item_set = user_candidate_dict[user]
        #去掉用户所以有行为的item
        candidate_item_set -= user_history_dict[user]
        print >> fout,'%s,%s' %(user,'#'.join(candidate_item_set))
    fout.close()
    print 'four done'
def main():
    begin_date = datetime.datetime(2014,11,18)
    end_date = datetime.datetime(2014,12,17)
    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
    cf_dir = utils.get_data_dir(utils.FLAG_CF)
    rule_dir = utils.get_data_dir(utils.FLAG_RULE)
    frate_str = '%s/rate_%s_%s' %(cf_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))  
    fraw_str = '%s/data_%s_%s' %(data_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))  
    fitem_str = '%s/item' %(data_dir)
    fres_str = '%s/candidate_history_cart' %(cf_dir)
    fres_cate_str = '%s/candidate_rule_cate' %(rule_dir)
    buy_date = datetime.datetime(2014,12,18)
    fbuy_str = '%s/data_buy_%s'%(data_dir,buy_date.strftime('%m%d'))
    #candidate_cart_items(frate_str,fres_str)
    #utils.evaluate_res(fres_str,fbuy_str,True)
    candidate_items_by_recent_cate(fraw_str,fitem_str,fres_cate_str)
    utils.evaluate_res_except_history(fres_cate_str,fbuy_str,True,fraw_str)
    
if __name__ == '__main__':
    main()
