import random

hit_num = 20
miss_num = 10
num_num = 255

def make_list(hit_num, miss_num, num_num):
    blank_list = [i for i in range(0, num_num+1)]
    hit_list = []
    miss_list = []

    for i in range(hit_num):
        index_num = random.randint(0,num_num)
        hit_list.append(blank_list.pop(index_num))
        num_num -= 1

    for i in range(miss_num):
        index_num = random.randint(0,num_num)
        miss_list.append(blank_list.pop(index_num))
        num_num -= 1
    
    return blank_list, hit_list, miss_list

blank_list, hit_list, miss_list = make_list(hit_num, miss_num, num_num)