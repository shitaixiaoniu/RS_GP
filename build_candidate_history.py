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
def main():

    begin_date = datetime.datetime(2014,11,18)
    end_date = datetime.datetime(2014,12,17)
    data_dir = utils.get_data_dir(utils.FLAG_TRAIN_TEST) 
    cf_dir = utils.get_data_dir(utils.FLAG_CF)
    frate_str = '%s/rate_%s_%s' %(cf_dir,begin_date.strftime('%m%d'),end_date.strftime('%m%d'))  
    fres_str = '%s/candidate_history_cart' %(cf_dir)
    buy_date = datetime.datetime(2014,12,18)
    fbuy_str = '%s/data_buy_%s'%(data_dir,buy_date.strftime('%m%d'))
    candidate_cart_items(frate_str,fres_str)
    utils.evaluate_res(fres_str,fbuy_str,True)
    
if __name__ == '__main__':
    main()
