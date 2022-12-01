# クライアントを作成

import socket
import threading
import sys
import struct

#IPアドレス
host = "127.0.0.1"

#ポート番号
port = 8080

endflag = 1

class PointSendThreading(threading.Thread):
    def __init__(self, server):
        self.input_str = ""
        self.s = server
        self.flag = True
        threading.Thread.__init__(self)

    def run(self):
        while self.flag:
            input_num = list(map(int, input().split()))
            send_num = [0 for i in range(6)]

            for i, num in enumerate(input_num):
                send_num[len(send_num)-i-1] = num
            
            num0 = send_num[0]
            num1 = send_num[1]
            num2 = send_num[2]
            num3 = send_num[3]
            num4 = send_num[4]
            num5 = send_num[5]

            if self.flag == False:
                break

            # #送信用データをbyte型 に変換
            #w, x, y, z, a, bの順番でパックする
            data = struct.pack(">BBBBBB", num0,num1,num2,num3,num4,num5)
            # 送信
            s.send(data)
            print('”{}”を送信しました.\n'.format(send_num))
    
    def close(self):
        self.flag = False

def game_start(d):
    global thread
    print("ゲームが開始されました.\n")
    print(f"数字を{num_quantity}つ入力をして下さい。\n")
    #サーバからの受信用スレッドを作成
    handle_thread = threading.Thread(target=handler, args=(s,), daemon=True)
    handle_thread.start()
    thread = PointSendThreading(s)
    thread.start()
    #スレッドの処理が終わるのを待つ
    handle_thread.join()

#サーバからメッセージを受信
def handler(s):
    while True:
        data = s.recv(6)
        recvdata = struct.unpack(">BBBBBB", data)

        #print(recvdata)
        if recvdata[0] == 1:#判定を受け取ったら
            point = recvdata[1]
            print("\n得点{}\n".format(point))

            print("その他のクライアントの得点.")
            other1 = recvdata[2]
            print("得点{}".format(other1))
            other2 = recvdata[3]
            print("得点{}".format(other2))
            other3 = recvdata[4]
            print("得点{}".format(other3))
            other4 = recvdata[5]
            print("得点{}".format(other4))

        #ゲーム終了が送られてきた時
        if recvdata[0] == 128:
            point = recvdata[1]
            other1 = recvdata[2]
            other2 = recvdata[3]
            other3 = recvdata[4]
            other4 = recvdata[5]

            break
    end_game(point, other1, other2, other3, other4)

def end_game(point, other1, other2, other3, other4):
    global endflag, thread
    thread.close()
    endflag = 0
    print("\nゲームが終了しました.")  
    print("あなたの得点は{}です.\n".format(point))

    print("その他のクライアントの得点.")
    print("得点{}".format(other1))
    print("得点{}".format(other2))
    print("得点{}".format(other3))
    print("得点{}".format(other4))

    #ゲームが終了したら切断する
    remove_conection(endflag)


def remove_conection(endflag):
    if endflag == 0:
        print("[切断] 通信が切断されました.")
        print("Enterを押すと終了します.")
        s.close()
        sys.exit()


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #サーバを指定
        s.connect((host, port))
        print("サーバに接続しました.")
        print("ゲームが開始されるまで少々お待ちください。\n")

        #受け取ったバイナリをbyte型に変換
        data = s.recv(6)
        recvdata = struct.unpack(">BBBBBB", data)

        #ゲーム開始を受け取ったら
        if recvdata[0] == 0:
            try:
                if recvdata[1] == 0:
                    num_quantity = 1
                else:
                    num_quantity = recvdata[1]
                game_start(s)
            except ValueError:  
                s.close()
                sys.exit()
            except OSError:
                s.close()
                sys.exit()
            finally:
                s.close()
                print("終了します.")