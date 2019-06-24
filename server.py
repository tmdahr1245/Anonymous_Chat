from socket import *
import threading
from datetime import *
import time
import sys

clientSocks = []#[connectionSock, "현재 있는 방번호", last_time, nickname]
room_list = []#[방이름, 방번호]
room_num = 1

def sendMsg(data, connectionSock):
	global clientSocks

	if data.decode('utf-8') == "ping":
		return

	cur_num = -1
	for client in clientSocks:
		if client[0] == connectionSock:
			cur_num = client[1]

	for client in clientSocks:
		if client[1] != cur_num:
			continue
		if client[0] == connectionSock:
			tmp = data.decode('utf-8')
			if tmp[:3] == "new":
				continue
			elif tmp[:3] == "out":
				continue
			elif tmp.find(":") == -1:
				continue
			print(data.decode('utf-8'))
			msg = data
		else:
			msg = data
		try:
			#packet format => [00000]
			room_number = -1
			for i in clientSocks:
				if i[0] == connectionSock:
					room_number = i[1]
					break
			tmp = ""
			for i in range(5 - len(str(room_number))):
				tmp += "0"
			tmp += str(room_number)
			msg = msg.decode('utf-8')
			msg = tmp + msg
			msg = msg.encode('utf-8')
			client[0].send(msg)
		except BrokenPipeError:
			clientSocks.remove(client)
		except ConnectionResetError:
			clientSocks.remove(client)
            
def connection_check(connectionSock, addr):
	while True:
		time.sleep(0.5)
		now = int(datetime.now().timestamp())
		for client in clientSocks:
			if client[0] == connectionSock:
				if now - client[2] > 1:
					roomP = 0
					for cli in clientSocks:
						if cli[1] == client[1] and cli[0] != client[0]:
							roomP += 1
					if roomP == 0:
						for room in room_list:
							if room[1] == client[1]:
								room_list.remove(room)
								break		
					data = "out " + client[3]
					sendMsg(data.encode('utf-8'), connectionSock)
					clientSocks.remove(client)
					connectionSock.close()
					print(str(addr), '에서 접속이 종료었습니다.')
					return
				break

def communication(connectionSock, addr):
	global room_num
	t = threading.Thread(target = connection_check, args = (connectionSock, addr, ))
	t.start()
	while True:
		try:
			data = connectionSock.recv(1024)
			data = data.decode('utf-8')
		except ConnectionResetError:
			break
		except OSError:
			break
		if len(data) != 0:
			if data == "list":
				packet = "list|"
				for i in room_list:
					roomP = 0
					for client in clientSocks:
						if client[1] == i[1]:
							roomP += 1
					packet = packet + i[0] + " [" + str(roomP) + "]"
					packet = packet + "|"
				if packet != "list|":
					packet = packet[0:len(packet)-1]
				else:
					packet = "list|none"
				connectionSock.send(packet.encode('utf-8'))
			elif data[0:4] == "nick":
				flag = True
				for client in clientSocks:
					if client[3] == data[5:]:
						connectionSock.send("nono".encode('utf-8'))
						flag = False
						break
				if flag:
					for client in clientSocks:
						if client[0] == connectionSock:
							client[3] = data[5:]
							connectionSock.send("okok".encode('utf-8'))
							break
			elif data[0:4] == "make":
				isExist = False
				for room in room_list:
					if room[0] == data[5:]:
						isExist = True
				if isExist:
					connectionSock.send(str(-1).encode('utf-8'))
				else:
					room_list.append([data[5:], room_num])
					for i in clientSocks:
						if i[0] == connectionSock:
							i[1] = room_num
					connectionSock.send(str(room_num).encode('utf-8'))
					room_num += 1
					print(room_list)
			elif data[:5] == "enter":
				room_name = data[6:]
				IS_Flag = True
				for room in room_list:
					if room[0] == room_name:
						IS_Flag = False
				if IS_Flag:
					connectionSock.send(str(-1).encode('utf-8'))
				else:
					print(room_name + " 방에 입장했습니다.")
					for client in clientSocks:
						if client[0] == connectionSock:
							for room in room_list:
								if room[0] == room_name:
									client[1] = room[1]
									connectionSock.send(str(client[1]).encode('utf-8'))
									break
							break
					print(room_list)
			elif data == "member":
				packet = "member|"
				cur_room = -1
				for client in clientSocks:
					if client[0] == connectionSock:
						cur_room = client[1]
						break
				for client in clientSocks:
					if client[1] == cur_room and client[0] != connectionSock:
						packet += client[3]
						packet += "|"
				if packet != "member|":
					packet = packet[0:len(packet)-1]
				else:
					packet += "none"
				connectionSock.send(packet.encode('utf-8'))
			elif data == "out":
				for client in clientSocks:
					if client[0] == connectionSock:
						roomP = 0
						for cli in clientSocks:
							if cli[1] == client[1] and cli[0] != client[0]:
								roomP += 1
						if roomP == 0:
							for room in room_list:
								if room[1] == client[1]:
									room_list.remove(room)
									break
						packet = "out " + client[3]
						sendMsg(packet.encode('utf-8'),connectionSock)
						client[1] = -1
						break
			elif data == "ping":
				for client in clientSocks:
					if client[0] == connectionSock:
						client[2] = int(datetime.now().timestamp())
						break
			elif data == "thread_exit":
				connectionSock.send("HS{EXIT}".encode('utf-8'))
			else:
				sendMsg(data.encode('utf-8'), connectionSock)
		else:
			break
            
def server_command():#for debug
	while True:
		command = input()
		if command == "client list":
			print(clientSocks)
		elif command == "room list":
			print(room_list)
		elif command == "exit":
			sys.exit(1)

def room_check():
	while True:
		time.sleep(1)
		for room in room_list:
			cnt = 0
			for client in clientSocks:
				if room[1] == client[1]:
					cnt += 1
			if cnt == 0:
				room_list.remove(room)

if __name__=="__main__":
	serverSock = socket(AF_INET, SOCK_STREAM)
	serverSock.bind(('', 8080))
	serverSock.listen(1)

	c = threading.Thread(target = server_command)
	c.start()

	r = threading.Thread(target = room_check)
	r.start()

	while True:
		connectionSock, addr = serverSock.accept()
		print(str(addr),'에서 접속이 확인되었습니다.')
		clientSocks.append([connectionSock, -1, int(datetime.now().timestamp()), ""])
		t = threading.Thread(target = communication, args = (connectionSock,addr,))
		t.start()