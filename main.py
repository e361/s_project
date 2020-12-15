from kademlia.kad import DHT
from user import User, MouthPiece, Handler
from chat import Chatroom

if __name__ == "__main__":
    chat = Chatroom()
    if chat.bootPeer:
        local = DHT(host = chat.host, port = chat.port, id = chat.peerId, seeds = [chat.bootPeer], info = chat.username)
    else:
        local = DHT(host = chat.host, port = chat.port, id = chat.peerId, info = chat.username)

    user = User(Handler, local)
    chat.probe(local, user)
    chat.retrieve(user)
    
    while True:
        try:
            instruction = input("""選擇功能: \n\t1. 搜尋聊天室用戶 
                    \n\t2. 創造群組
                    \n\t3. 離開群組
                    \n\t4. 聊天
                    \n\t5. 顯示聊天室群組 
                    \n\t6. 邀請進入群組 ===============\n """)

            if instruction == '1':
                for users in local.peers():
                    print("線上用戶: {}, ip: {}".format(users['info'], users['host']))
                chat.probe(local, user)

            if instruction == '2':
                user.createRoom()

            if instruction == '3':
                print(list(user.room.keys() ))
                roomId = input("想要離開的大廳?")
                targets = user.iterUsers(chat, roomId)
                user.leave(targets, roomId)

            if instruction == '4':
                target = input("想傳給誰? 或想傳給哪個群組??")
                message = input("想傳些什麼??")
                if target in user.room:
                    targets = user.iterUsers(chat, target)
                    user.sendMessage(targets, message, target)
                else:
                    targets = [chat.network[target]]
                    user.sendMessage(targets, message)
                print(targets)

            if instruction == '5':
                print("目前群組: ")
                for roomId in user.room:
                    print("{}, {}".format(roomId, user.room[roomId]))
                if not user.room:
                    print("沒有群組")

            if instruction == '6':
                username = input("想邀請誰??")
                print(list(user.room.keys()))
                roomId = input("大廳名字??")
                user.room[roomId].append(username)
                targets = user.iterUsers(chat, roomId)
                user.invite(targets, roomId)

        except EOFError:
            pass
        except KeyboardInterrupt:
            break
    chat.offline(user) 
