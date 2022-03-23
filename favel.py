#first, we import the required libraries
import threading, os, time, requests, yaml
from tkinter.filedialog import askopenfilename
from tkinter import Tk
from concurrent.futures import ThreadPoolExecutor
from console.utils import set_title
from timeit import default_timer as timer
from datetime import timedelta, datetime
from colored import fg

#if results folder doesnt exist, make one
if not os.path.exists("Results"):
	os.mkdir("Results")

class vars: #we store basically every variable in this class called vars
	threads = None
	timeout = None
	proxies = []
	remaining = []
	current_proxy = 0
	combos = []
	errors = 0
	valid = 0
	invalid = 0
	blocked = 0
	total = 0
	checked = 0
	cpm = 0
	proxy_type = 'http'
	combos_name = ''
	min_members = None
	max_verification = None
	starttime = None
	capture_message = None
	color_scheme = None
	refresh_delay = None

#if settings file doesnt exist, make one with default settings
if not os.path.exists("settings.yaml"):
	with open("settings.yaml", "w") as f:
		f.write('Threads: 200\nTimeout: 6 #seconds\nMinimum Members: 500\nMaximum Verification Level: 4\nColor Scheme Hex: 0236c7\nUI Refresh Delay: 1 #seconds\n'+r'Capture Message: "------------------------------------\n > Code: {code}\n > Server Name: {server_name}\n > Members: {member_count}\n > Verification Level: {verification_level}\n" #placeholders: code, server_name, server_description, server_id, member_count, verification_level, boosters | newline = \n | use placeholders like this: "placeholder: {put placeholder here}"')

with open("settings.yaml", "r") as f: #load settings from the settings file and store them inside the vars class
	settings = yaml.safe_load(f)
	vars.threads = settings['Threads']
	vars.timeout = settings['Timeout']
	vars.min_members = settings['Minimum Members']
	vars.max_verification = settings['Maximum Verification Level']
	vars.capture_message = settings['Capture Message']
	try:
		vars.color_scheme = fg(f"#{settings['Color Scheme Hex']}")
	except:
		vars.color_scheme = fg("#0236c7")
	try:
		vars.refresh_delay = int(settings['UI Refresh Delay'])
	except:
		try:
			vars.refresh_delay = float(settings['UI Refresh Delay'])
		except:
			vars.refresh_delay = 1

class main: #this class is basically the brain of the program
	def __init__(self):
		self.start()

	def clear(self):
		os.system('cls') #simply clears console (calling this function requires 12 characters while calling the os command
						 #						 for clearing console requires 16, i think by saving those 4 characters we achieve a lot)

	def logo(self):
		self.clear()
		print(f'''{vars.color_scheme}                                                     Favel\u001b[0m\n''') #i was too lazy to copy and paste something from an art gen

	def check(self, keyword): #the keyword argument is the discord invite code
		try:
			proxy = vars.proxies[vars.current_proxy]
		except:
			vars.current_proxy = 0
			proxy = vars.proxies[vars.current_proxy]
		while 1: #repeat the process until we either get valid or invalid
			while 1: #repeat until we get reply
				try:
					a = requests.get(f'https://discord.com/api/v9/invites/{keyword}?with_counts=true', proxies={'http': f"{vars.proxy_type}://{proxy}", 'https': f"{vars.proxy_type}://{proxy}"}, timeout=vars.timeout, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36', 'pragma': 'no-cache', 'accept': '*/*'}) #sends the check request to the discord api
					break
				except: #if request fails
					vars.current_proxy += 1
					vars.errors += 1
					try:
						proxy = vars.proxies[vars.current_proxy]
					except:
						vars.current_proxy = 0
						proxy = vars.proxies[vars.current_proxy]

			if '"message": "Unknown Invite"' in a.text: #if account is invalid
				vars.invalid += 1
				break
			elif "guild" in a.text and int(a.json()['approximate_member_count']) >= vars.min_members and int(a.json()['guild']['verification_level']) <= vars.max_verification: #if account is valid and meets the criteria
				code = keyword
				server_name = a.json()['guild']['name']
				server_description = a.json()['guild']['description']
				server_id = a.json()['guild']['id']
				member_count = a.json()['approximate_member_count']
				verification_level = a.json()['guild']['verification_level']
				boosters = a.json()['guild']['premium_subscription_count']
				vars.valid += 1
				with open(f'Results\\{vars.starttime}\\capture.txt', "a", errors="replace") as f:
					try:
						exec(f'f.write(f{repr(vars.capture_message)})') #writes the capture message to the capture output file
					except Exception as e:
						with open("capture_error.log", "w") as f:
							f.write(f"{e}\n\nCapture message: {repr(vars.capture_message)}")
				with open(f"Results\\{vars.starttime}\\valid.txt", "a", errors="replace") as f:
					f.write(f"{keyword}\n")
				break
			elif "Access denied | " in a.text or " Cloudflare" in a.text: #if request has been blocked by cloudflare
				vars.blocked += 1
				#we dont set quit to true because we want the checker to check the code again
		vars.checked += 1 #adds +1 to checked variable so we can count remaining for ui
		threading.Thread(target=self.cpm,).start() #adds +1 cpm (i know its bad to use threads for counting cpm, ill write a better counter if i have time)
		vars.remaining.remove(keyword) #removes code from remaining list so we dont check it again

	def cpm(self):
		vars.cpm += 1 #adds one to cpm variable
		time.sleep(60)#waits 60 seconds
		vars.cpm -= 1 #removes the added cpm

	def start(self):
		self.logo()
		Tk().withdraw() #we create a tkinter ui and instantly hide it, this is needed for the file loading
		print('                                                Loading Proxies...')
		loaded = False
		while not loaded: #loop until user selects file
			time.sleep(0.5)
			try:
				with open(askopenfilename(), 'r', errors='replace') as f:
					lines = f.readlines()
					for item in lines:
						vars.proxies.append(item.strip())
				loaded = True
			except:
				time.sleep(1)
		self.logo()
		print(f'''                                                  Proxy type:
                                                  {vars.color_scheme}<\u001b[0m1{vars.color_scheme}>\u001b[0m HTTP
                                                  {vars.color_scheme}<\u001b[0m2{vars.color_scheme}>\u001b[0m SOCKS4
                                                  {vars.color_scheme}<\u001b[0m3{vars.color_scheme}>\u001b[0m SOCKS5\n''')
		ptype = input(f'                                                  {vars.color_scheme}<\u001b[0mQ{vars.color_scheme}>\u001b[0m ')
		if "1" in ptype:
			vars.proxy_type = "http"
		elif "2" in ptype:
			vars.proxy_type = "socks4"
		elif "3" in ptype:
			vars.proxy_type = "socks5"
		temp_proxies = []
		if '@' in vars.proxies[0]: #if proxies are auth proxies
			for item in vars.proxies:
				temp_proxies.append(item.split('@')[1]+"@"+item.split('@')[0]) #reverses auth proxy format, because for whatever reason the requests library requires it to be backwards
			vars.proxies = temp_proxies
			print('\nAuth proxy format:         '+str(temp_proxies[0]))
			print('Make sure it matches this: user:pass@ip:port')
			input()
		loaded = False
		self.logo()
		print('                                                Loading Keywords...')
		while not loaded:
			time.sleep(0.5)
			vars.combos_name = askopenfilename()
			try:
				with open(vars.combos_name, 'r', errors='replace') as f:
					lines = f.readlines()
					for item in lines:
						vars.combos.append(item.strip())
				loaded = True
			except:
				time.sleep(1)
		vars.starttime = datetime.today().strftime("%d-%m-%Y %H-%M-%S")
		if not os.path.exists(f"Results\\{vars.starttime}"):
			os.mkdir(f"Results\\{vars.starttime}")
		vars.total = len(vars.combos)
		vars.remaining = vars.combos
		with ThreadPoolExecutor(max_workers=vars.threads) as exe:
			self.clear()
			print("Starting threads...")
			for item in vars.combos:
				if item.strip() != "": #if line is not empty
					exe.submit(self.check, item) #submits the thread to the threadpool
				vars.current_proxy += 1
			threading.Thread(target=self.screen,).start() #after the threads have been added to the threadpool, we display the ui
			                                              #the reason why we dont display the ui before adding the threads to the threadpool is because
			                                              #it would be incredibly laggy, and would make adding threads even slower

	def screen(self):
		greenicon = '\u001b[32m[\u001b[0m~\u001b[32m]\u001b[0m'
		yellowicon = '\u001b[33m[\u001b[0m~\u001b[33m]\u001b[0m'
		redicon = '\u001b[31m[\u001b[0m~\u001b[31m]\u001b[0m'
		blueicon = f'{vars.color_scheme}[\u001b[0m~{vars.color_scheme}]\u001b[0m'
		start = timer()
		while 1:
			self.logo()
			print('')
			print(f'                                                {greenicon} Valid ( {vars.valid} )')
			print(f'                                                {yellowicon} Invalid ( {vars.invalid} )')
			print(f'\n                                                {redicon} Errors ( {vars.errors} )')
			print(f'                                                {redicon} Blocked ( {vars.blocked} )')
			print(f'\n                                                {blueicon} CPM ( {vars.cpm} )')
			print(f'                                                {blueicon} Remaining ( {vars.total-vars.checked} )')
			set_title(f'Favel Invite Checker | CPM: {vars.cpm} | {str(timedelta(seconds=timer()-start)).split(".")[0]} | Nandi') #its not cool to replace my name with yours
			time.sleep(vars.refresh_delay)
			os.system('cls')

if __name__ == '__main__':
	main()