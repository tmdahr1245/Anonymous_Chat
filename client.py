from socket import *
import tkinter
import threading
import time
import tkinter.messagebox
import sys
import functools
import ctypes
import platform

msg = ""
nick = ""
room_number = -1
ip = '127.0.0.1'
port = 8080

def exit_room(*args):
	if args[0] == "chat":
		global room_number, member_list_button
		global frame, text, scrollbar, entry, send_button, room_exit_button
		frame.destroy()
		text.destroy()
		scrollbar.destroy()
		entry.destroy()
		send_button.destroy()
		room_exit_button.destroy()
		member_list_button.destroy()
        
		window.title("익명 채팅방 : " + nick)
		clientSock.send("thread_exit".encode('utf-8'))
		time.sleep(0.2)
		clientSock.send("out".encode('utf-8'))
        
		menu("exit_room")
		room_number = -1

def sendMsg(*args):
	global entry_text, entry, nick
	if entry.get() == "":
		tkinter.messagebox.showwarning(title = "WARNING",message = "메세지를 입력해 주세요.")
	elif len(entry.get()) > 1000:
		tkinter.messagebox.showwarning(title = "WARNING",message = "최대 메세지(1000byte)")
	else:		
		msg = nick + " : " + entry.get()
		clientSock.send(msg.encode('utf-8'))
		entry_text.set("")

def recvMsg():
	count = 2
	while 1:
		count += 1
		data = clientSock.recv(1024)
		plus = 0

		tmp = data.decode('utf-8')
		for i in range(len(tmp)):
			if tmp[i] == '\n':
				plus += 1

		if data.decode('utf-8')[:6] == "member":
			member = data.decode('utf-8').split("|")
			member_list = nick + "(나)\n"
			if member[1] != "none":
				for i in range(1,len(member)):
					member_list += (member[i] + "\n")
			tkinter.messagebox.showwarning(title="현재 방 인원",message = member_list)
			count -= 1
			continue
			
		global msg,text
		msg = data.decode('utf-8')
		if msg=="HS{EXIT}":
			break
		if msg[5:8] == "new" or msg[5:8] == "out":
			other = msg[9:]
			if msg[5:8] == "new":
				other = other + "님이 입장하였습니다."
			elif msg[5:8] == "out":
				other = other + "님이 퇴장하였습니다."
			text.config(state = 'normal')
			text.insert(tkinter.END, "\n" + other)
			text.see("end")
			text.config(state = 'disabled')
			start = str(count) + ".0"
			end = str(count) + "." + str(len(other))
			text.tag_add("other", start, end)
			text.tag_configure("other", justify = 'center')
			text.tag_config("other", foreground = "gray")
		else:
			try:	
				if msg[5:9] == "ping":
					break
				room_num = int(msg[:5])
			except ValueError:
				break
			if room_num == room_number:
				flag = False
				msg = msg[5:]
				tmp = msg.split(":")[0]
				if tmp == (nick + " "):
					msg = msg.replace(msg.split(":")[0], "나 ")
					flag = True
				text.config(state = 'normal')
				text.insert(tkinter.END, "\n" + msg)
				text.see("end")
				text.config(state = 'disabled')
				if(flag):
					start = str(count)
					start = start + ".0"
					end = str(count + plus)
					end = end + "." + str(len(msg))
					text.tag_add("me", start, end)
					text.tag_configure("me", justify = 'right')
					text.tag_config("me", foreground = "red")
				count += plus

def memberList(*args):
	clientSock.send("member".encode('utf-8'))
	return	

def chat(*args):
	global text, entry_text, entry
	global listbox, room_list_button, back_button, member_list_button
	global frame, scrollbar, send_button, room_exit_button
	
	if args[0] == "get_room":
		listbox.destroy()
		room_list_button.destroy()
		back_button.destroy()
	
	elif args[0] == "make_room":
		pass

	window.title(args[1])

	frame=tkinter.Frame(window)
	frame.pack(fill="both", expand=True)

	text = tkinter.Text(frame)
	text.insert(tkinter.CURRENT, "")
	scrollbar = tkinter.Scrollbar(frame, command = text.yview)
	text.config(state = 'disabled')
	text.configure(yscrollcommand = scrollbar.set, background = "#92ddff")
	scrollbar.pack(side="right", fill="y")
	text.pack(side = "left", fill = "both", expand = True)
	
	en = "방에 입장하였습니다."
	text.config(state = 'normal')
	text.insert(tkinter.END, "\n" + en)
	text.see("end")
	text.config(state = 'disabled')
	start = str(2) + ".0"
	end = str(2) + "." + str(len(en))
	text.tag_add("en", start, end)
	text.tag_configure("en", justify = 'center')
	text.tag_config("en", foreground = "gray")
	
	entry_text = tkinter.StringVar()
	entry = tkinter.Entry(window, textvariable = entry_text, relief = tkinter.SOLID, width = 15)
	entry.bind("<Return>", sendMsg)
	entry.pack()

	send_button = tkinter.Button(window, text = "보내기", command = sendMsg, bg = "#92ddff", width = 14, relief = tkinter.GROOVE)
	send_button.pack()

	member_list_button = tkinter.Button(window, text = "현재 방 인원", command = memberList, bg = "#92ddff", width = 14, relief = tkinter.GROOVE)
	member_list_button.pack()

	room_exit_button = tkinter.Button(window, text = "방 나가기", command = functools.partial(exit_room,"chat"), bg = "#92ddff", width = 14, relief = tkinter.GROOVE)
	room_exit_button.pack()

	r = threading.Thread(target = recvMsg, daemon = True)
	r.start()

def make_room_process(*args):
	global room_name_label, room_name_entry, room_name_button, room_number
	room_name = room_name_entry.get()
    
	if room_name == "":
		tkinter.messagebox.showwarning(title = "WARNING", message = "방 제목을 입력해 주세요.")
		return
	if len(room_name) > 15:
		tkinter.messagebox.showwarning(title = "WARNING", message = "방 제목은 최대 15글자 입니다.")
		return

	packet = "make " + room_name
	clientSock.send(packet.encode("utf-8"))
	
	time.sleep(0.2)

	room_number = int(clientSock.recv(1024).decode('utf-8'))

	if room_number == -1:
		tkinter.messagebox.showwarning(title = "WARNING", message = "방 제목이 중복됩니다.")
	else:
		room_name_label.destroy()
		room_name_entry.destroy()
		room_name_button.destroy()
		back_button.destroy()

		chat("make_room", room_name)

def back_func(*args):
	global back_button
	if args[0] == "make_room":
		global room_name_label, room_name_entry, room_name_button
		room_name_button.destroy()
		room_name_entry.destroy()
		room_name_label.destroy()
		back_button.destroy()
		menu("back_func")
	
	elif args[0] == "get_room":
		global listbox, room_list_button
		listbox.destroy()
		room_list_button.destroy()
		back_button.destroy()
		menu("back_func")

def make_room(*args):
	global make_room_button, enter_room_button, room_name_label, room_name_entry, room_name_button, back_button
	make_room_button.destroy()
	enter_room_button.destroy()

	room_name_label = tkinter.Label(window, text = "방제목", width = 15, bg = "#92ddff")
	room_name_label.pack()

	room_name_entry = tkinter.Entry(window, text = "", relief = tkinter.SOLID, width = 15)
	room_name_entry.bind("<Return>", make_room_process)
	room_name_entry.pack()

	room_name_button = tkinter.Button(window, text = "입력", command = make_room_process, bg = "#92ddff", width = 14, relief = tkinter.GROOVE)
	room_name_button.pack()

	back_button = tkinter.Button(window, text = "뒤로가기", command = functools.partial(back_func, "make_room"), bg = "#92ddff", width = 14, relief = tkinter.GROOVE)
	back_button.pack()

def enter_room(*args):
	global listbox, room_number
	
	packet = "enter " + listbox.get(tkinter.ACTIVE)
	packet = packet[::-1]
	idx = 0
	while True:
		if packet[idx] == '[':
			idx += 2
			break
		idx += 1
        
	packet = packet[idx:]
	packet = packet[::-1]
	clientSock.send(packet.encode('utf-8'))
	time.sleep(0.2)
	room_number = int(clientSock.recv(1024).decode('utf-8'))
    
	if room_number == -1:
		tkinter.messagebox.showwarning("WARNING", "선택하신 방이 사라졌습니다.")
		menu("enter_room")
	else:
		time.sleep(0.2)
		packet = "new " + nick
		clientSock.send(packet.encode('utf-8'))
		room_name = listbox.get(tkinter.ACTIVE)
		for i in range(len(room_name)):
			if room_name[i] == '[':
				idx = i
		chat("get_room", room_name[:idx-1])

def get_room():
	global make_room_button, enter_room_button, listbox, room_list_button, back_button
	room_list = ""
	make_room_button.destroy()
	enter_room_button.destroy()
	redirect_flag = False
	clientSock.send("list".encode('utf-8'))

	while True:
		room_list = clientSock.recv(1024).decode('utf-8')
		if room_list == "list|none":
			tkinter.messagebox.showwarning("WARNING", "개설된 방이 없습니다.")
			menu("get_room")
			redirect_flag = True
			break
		if room_list[:5] == "list|":
			room_list = room_list[5:]
			break

	if redirect_flag == False:
		room_list = room_list.split("|")
		cnt = 0
		listbox = tkinter.Listbox(window, selectmode = 'extended', width = 30, height = 0, background = "#92ddff")
		for name in room_list:
			listbox.insert(cnt, name)
		listbox.pack()
		room_list_button = tkinter.Button(window, text = "입장하기", command = functools.partial(enter_room,"get_room"), width = 29, background = "#92ddff", relief = tkinter.GROOVE)
		room_list_button.pack()
		back_button = tkinter.Button(window, text = "뒤로가기", command = functools.partial(back_func, "get_room"), width = 29, background = "#92ddff", relief = tkinter.GROOVE)
		back_button.pack()

def exit_program():
	global window
	window.quit()
	sys.exit(0)

def menu(*args):
	global label, nickname, button, make_room_button, enter_room_button, nick
    
	if args[0] == "get_room" or args[0] == "exit_room" or args[0] == "back_func":
		pass
	elif args[0] == "enter_room":
		global listbox, room_list_button, back_button
		listbox.destroy()
		room_list_button.destroy()
		back_button.destroy()
	elif args[0] == "main":
		nick = nickname.get()
		if nick == "":
			tkinter.messagebox.showwarning(title = "WARNING", message = "별명을 입력해 주세요.")
			return
		if len(nick) > 8:
			tkinter.messagebox.showwarning(title = "WARNING", message = "별명은 최대 8글자 입니다.")
			return
		for i in range(len(nick)):
			if nick[i] == " ":
				tkinter.messagebox.showwarning(title = "WARNING", message = "별명에 공백은 들어갈수 없습니다.")
				return


		clientSock.send(("nick " + nick).encode('utf-8'))
		data = clientSock.recv(1024).decode('utf-8')
		if data == "nono":
			tkinter.messagebox.showwarning(title="WARNING",message = "중복된 별명입니다.")
			return
		window.title("익명 채팅방 : " + nick)

		label.destroy()
		nickname.destroy()
		button.destroy()
	
	make_room_button = tkinter.Button(window, text = "방 만들기", command = make_room, width = 145, height = 14, bg = "#92ddff", relief = tkinter.RIDGE)
	make_room_button.pack()

	enter_room_button = tkinter.Button(window, text = "대화 참여하기", command = get_room, width = 145, height = 14, bg = "#92ddff", relief = tkinter.RIDGE)
	enter_room_button.pack()

def connection_fail():
	global window
	try:
		while True:
			time.sleep(0.5)
			clientSock.send("ping".encode("utf-8"))
	except BrokenPipeError:
		tkinter.messagebox.showwarning(title = "WARNING", message = "인터넷 연결에 문제가 있거나\n채팅서버가 종료되었을 수 있습니다.")
		window.quit()
		sys.exit(0)
	except ConnectionAbortedError:
		tkinter.messagebox.showwarning(title = "WARNING", message = "인터넷 연결에 문제가 있거나\n채팅서버가 종료되었을 수 있습니다.")
		window.quit()
		sys.exit(0)
	except ConnectionResetError:
		tkinter.messagebox.showwarning(title = "WARNING", message = "인터넷 연결에 문제가 있거나\n채팅서버가 종료되었을 수 있습니다.")
		window.quit()
		sys.exit(0)

def start():
	global label, nickname, button, loading
	time.sleep(2)
	loading.destroy()

	label = tkinter.Label(window, text = "별명", width = 15, bg = "#92ddff")
	label.pack()

	nickname = tkinter.Entry(window, text = "", relief = tkinter.SOLID, width = 15)
	nickname.bind("<Return>", functools.partial(menu,"main"))
	nickname.pack()

	button = tkinter.Button(window, text = "입력", command = functools.partial(menu,"main"), width = 14, bg = "#92ddff", relief = tkinter.GROOVE)
	button.pack(side = "top")

def cmd_destroy():
	ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def conn_serv(Sock):
	try:
		Sock.connect((ip, port))
		return True
	except ConnectionRefusedError:
		tkinter.messagebox.showwarning(title = "WARNING", message = "서버가 구동되지 않았습니다.")
		return False
	except ConnectionResetError:
		tkinter.messagebox.showwarning(title = "WARNING", message = "서버가 구동되지 않았습니다.")
		return False

def load_func(window):
	global loading

	window.title("익명 채팅방")
	window.geometry("290x440+500+200")
	window.configure(background = "#92ddff")
	window.iconbitmap('./img/icon.ico')
	window.minsize(290, 440)
	window.maxsize(290, 440)

	loading = tkinter.Label(window, text = "")
	if platform.system() == "Windows":
		loading.img = tkinter.PhotoImage(file = './img/image.png')
	else:
		loading.img = tkinter.PhotoImage(file = './img/image.gif')
	loading.config(image = loading.img, compound = 'bottom') 
	loading.pack()
	
	st = threading.Thread(target = start, daemon = True)
	st.start()
	
	t = threading.Thread(target = connection_fail, daemon = True)
	t.start()

if __name__=="__main__":
	clientSock = socket(AF_INET, SOCK_STREAM)
	window = tkinter.Tk()
	
	if platform.system() == "Windows":
		cmd_destroy()
	if conn_serv(clientSock):
		load_func(window)
		window.mainloop()
