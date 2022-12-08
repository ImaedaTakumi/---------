# socket サーバを作成
import socket
import threading
import random
import sys
import struct
import time

# IPアドレス
host = "127.0.0.1"

# ポート番号
port = 8080

# 接続最大数
maxclient = 5

# クライアント情報
clients = []

# ポイント
point = [0] * 5

# 拡張機能のOn・Off
exp_Flag = False

end_counter = 3

hit_quantity = 50
miss_quantity = 20
blank_quantity = 255

class PointSendThreading(threading.Thread):
    def __init__(self, clients):
        self.clients = clients
        self.flag = True
        threading.Thread.__init__(self)

    def run(self):
        while self.flag:
            sleep_seconds = 5
            time.sleep(sleep_seconds)
            for c in clients:
                c[0].sendto(get_senddata(c[0], c[1], 1, 0), c[1])
    
    def close(self):
        self.flag = False

class SendDataThreading(threading.Thread):
    def __init__(self, con, address):
        threading.Thread.__init__(self)
        self.con = con
        self.address = address
        self.flag = True

    def run(self):
        userid = clients.index((self.con, self.address))
        while self.flag:
            try:
                # データを受け取る最大6byte
                data = self.con.recv(6)
                recvdata = struct.unpack(">BBBBBB", data)

                print("[受信] userid:{}, recvdata:{}".format(userid, recvdata))

                num_list = list(reversed(recvdata))
                num_list = list(map(int, num_list))
                num_list = sorted(set(num_list), key=num_list.index)

                # 入力された数値
                if exp_Flag:
                    num_list = num_list[:num_quantity]
                    print("ユーザID{}が”{}”と入力しました。".format(userid, num_list))
                    ad_point = expansion_count(num_list)
                    print("ユーザーID{}, {}ポイント獲得".format(userid, ad_point))
                    if (point[userid] + ad_point > 0):
                        point[userid] += ad_point
                    else:
                        point[userid] = 0
                
                else:
                    print("ユーザID{}が”{}”と入力しました。".format(userid, num_list[0]))
                    ad_point = nomal_count(num_list[0])
                    print("ユーザーID{}, {}ポイント獲得".format(userid, ad_point))
                    if (point[userid] + ad_point > 0):
                        point[userid] += ad_point
                    else:
                        point[userid] = 0
                
                print(point)

            except ConnectionResetError:
                remove_conection(self.con, self.address)
                break
            except struct.error:
                break

    def close(self):
        self.flag = False

def make_list(hit_quantity, miss_quantity, blank_quantity):
    blank_list = [i for i in range(0, blank_quantity+1)]
    hit_list = []
    miss_list = []

    for i in range(hit_quantity):
        index_num = random.randint(0,blank_quantity)
        hit_list.append(blank_list.pop(index_num))
        blank_quantity -= 1

    for i in range(miss_quantity):
        index_num = random.randint(0,blank_quantity)
        miss_list.append(blank_list.pop(index_num))
        blank_quantity -= 1
    
    return blank_list, hit_list, miss_list

blank_list, hit_list, miss_list = make_list(hit_quantity, miss_quantity, blank_quantity)

#点数計算(通常)
def nomal_count(input_num):
    global blank_list, hit_list, miss_list
    if input_num in hit_list:
        point = 10
        blank_list.append(hit_list.pop(hit_list.index(input_num)))
    elif input_num in miss_list:
        point = -10
        blank_list.append(miss_list.pop(miss_list.index(input_num)))
    else:
        point = -1
    
    return point

#点数計算(拡張)
def expansion_count(input_list):
    global blank_list, hit_list, miss_list
    point = 0
    hit_count = 0
    for num in input_list:
        if num in hit_list:
            point += 10
            blank_list.append(hit_list.pop(hit_list.index(num)))
            hit_count += 1
        elif num in miss_list:
            point -= 10
            blank_list.append(miss_list.pop(miss_list.index(num)))
        else:
            point -= 1
    
    if hit_count > 1:
        point += hit_count*3

    return point

# サーバをスタートする
def server_start():
    # AF = IPv4 という意味
    # TCP/IP の場合は、SOCK_STREAM を使う
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # IPアドレスとポートを指定
        s.bind((host, port))
        # 接続
        s.listen(maxclient)
        # connection するまで待つ
        counter = 0
        while counter < maxclient:
            # クライアントと接続。返り値は2つ返ってくる
            con, address = s.accept()
            counter += 1
            # クライアントの情報をリストに格納
            global clients
            clients.append((con, address))
            userid = clients.index((con, address))
            print(con, address)
            print("[接続] ユーザID{}".format(userid))

            reception = int(input("これ以上ユーザを受け付けますか？(0:いいえ, 1:はい)\n"))
            if (reception == 1):
                pass
            else:
                break

        game_start()
        
# ゲーム開始
def game_start():
    thread = PointSendThreading(clients)
    thread.start()

    for c in clients:
        # スレッド処理開始
        client_threads = SendDataThreading(c[0], c[1])
        client_threads.start()
        c[0].sendto(get_senddata(c[0], c[1], 0, num_quantity), c[1])

    while True:
        a = input('\nゲームを開始します.(q:終了)')
        if (a == "q"):
            client_threads.close()
            thread.close()
            end_game()
            break

# 送信データを返す。
def get_senddata(con, address, w_type, num_quantity):
    # ユーザIDを取得
    userid = clients.index((con, address))

    p = point[userid]
    w = w_type
    x = 0
    y = 0
    z = 0
    a = 0
    b = 0

    if w_type == 0:  # ゲーム開始
        x = num_quantity
        y = 0
        z = 0
        a = 0
        b = 0

    elif w_type == 1:  # 判定
        if userid == 0:
            x = p
            y = point[1]
            z = point[2]
            a = point[3]
            b = point[4]
        elif userid == 1:
            x = p
            y = point[0]
            z = point[2]
            a = point[3]
            b = point[4]
        elif userid == 2:
            x = p
            y = point[0]
            z = point[1]
            a = point[3]
            b = point[4]
        elif userid == 3:
            x = p
            y = point[0]
            z = point[1]
            a = point[2]
            b = point[4]
        elif userid == 4:
            x = p
            y = point[0]
            z = point[1]
            a = point[2]
            b = point[3]
    elif w_type == 128:  # 終了
        if userid == 0:
            x = p
            y = point[1]
            z = point[2]
            a = point[3]
            b = point[4]
        elif userid == 1:
            x = p
            y = point[0]
            z = point[2]
            a = point[3]
            b = point[4]
        elif userid == 2:
            x = p
            y = point[0]
            z = point[1]
            a = point[3]
            b = point[4]
        elif userid == 3:
            x = p
            y = point[0]
            z = point[1]
            a = point[2]
            b = point[4]
        elif userid == 4:
            x = p
            y = point[0]
            z = point[1]
            a = point[2]
            b = point[3]
        
    data = struct.pack(">BBBBBB", w, x, y, z, a, b)
    return data

# ゲーム終了
def end_game():
    global clients
    print("ゲームを終了します.")
    for c in clients:  # クライアントに終了を伝える
        c[0].sendto(get_senddata(c[0], c[1], 128, 0), c[1])

# クライアントと接続を切る
def remove_conection(con, address):
    userid = clients.index((con, address))
    print("[切断] ユーザID{}".format(userid))
    con.close()
    clients.remove((con, address))

if __name__ == "__main__":
    print("アタリ：{}, ハズレ：{}".format(hit_list, miss_list))
    print("拡張機能をOnにしますか?\n1 (On) or 0 (Off)")
    num = int(input())
    if num == 1:
        print("On\n")
        exp_Flag = True
    elif num == 0:
        print("Off\n")
        exp_Flag = False
    else:
        print("その他が入力されました.\n拡張機能はOffです.\n")
        exp_Flag = False
       
    if exp_Flag:
        print("いくつの数字の入力を受け付けますか?\n(2~6の数字を入力してください。)")
        num_quantity = int(input())
    else:
        num_quantity = 1
    
    server_start()

    socket.close
    sys.exit