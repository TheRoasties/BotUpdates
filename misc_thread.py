from globalvars import *
from code_modules.function import *
from code_modules.weapon_shop import *
from code_modules.bionic_shop import *

global driver
global lock_webdriver

from code_modules.online_time_record import *
from code_modules.check_messages import *
from code_modules.launder import *
from code_modules.city_list import *
from code_modules.mayor import *
from code_modules.obituaries import *
from code_modules.bank_career import *
from code_modules.mechanic import *
from code_modules.hospital import *
from code_modules.fire_inspection import *
from code_modules.journal import *
from code_modules.lawyer import *
from code_modules.judge import *
from code_modules.mortician_autopsy import *
from code_modules.mortician_smuggle import *
from code_modules.customs_blindeye import *
from code_modules.blackmarket_gangster_exp import *
from code_modules.gym import *
from code_modules.casino import *
from earn_thread import *
from code_modules.blackmarket import *
from code_modules.vehicle_get_status import *
from code_modules.profile_check import *
from code_modules.boys_work_mechanic import *
from code_modules.boys_work_hospital import *
from code_modules.police_case import *
from code_modules.police_911 import *


def withdraw_money_misc(lock_webdriver, running_thread, waiting_thread_list, desired_money_on_hand, your_clean_money):
	if int(your_clean_money) < int(desired_money_on_hand):
		print_function('withdraw_money_misc - withdraw queued')
		thread_add_to_queue(running_thread, waiting_thread_list, priority_thread_earn)
		print_function('withdraw_money_misc - withdraw running')
		withdraw_amount = int(your_clean_money) - int(desired_money_on_hand)
		withdraw_amount -= withdraw_amount % 1000
		withdraw_amount = abs(withdraw_amount)
		withdraw_money(lock_webdriver, running_thread, withdraw_amount)
		print_function('withdraw_money_misc - withdraw finished')
		thread_remove_from_queue(running_thread, waiting_thread_list)
	elif (int(your_clean_money) > int(config['Misc']['ExcessMoneyOnHand'])) and (int(config['Misc']['ExcessMoneyOnHand']) > int(desired_money_on_hand)):
		# DEPOSIT MONEY IF TOO MUCH ON HAND - WILL NOT WITHDRAW IF USER ERROR OF
		print_function('withdraw_money_misc - deposit queued')
		thread_add_to_queue(running_thread, waiting_thread_list, priority_thread_earn)
		print_function('withdraw_money_misc - deposit running')
		element_click(lock_webdriver, "XPATH", "//*[@id='wrapper']/div[@id='nav_right']/div[@id='display'][3]/form", running_thread)
		print_function('withdraw_money_misc - deposit finished')
		thread_remove_from_queue(running_thread, waiting_thread_list)
	return


def consume_drugs(lock_webdriver, waiting_thread_list, running_thread):
	if config.getboolean('Drugs', 'ConsumeCoke'):
		if globals()['timers'].__dict__['consume_drugs_timer'] is None:
			try:
				consume_drugs_timer = read_file("env/consume_drugs_timer.txt")
				try:
					consume_drugs_timer = datetime.datetime.strptime(consume_drugs_timer, '%Y-%m-%d %H:%M:%S.%f')
				except:
					consume_drugs_timer = datetime.datetime.strptime(consume_drugs_timer, '%Y-%m-%d %H:%M:%S')
			except:
				consume_drugs_timer = datetime.datetime.utcnow()
		else:
			consume_drugs_timer = globals()['timers'].__dict__['consume_drugs_timer']

		time_difference = datetime.datetime.utcnow() - consume_drugs_timer
		if not '-' in str(time_difference):
			# ADDED AT PRIORITY 8 SO IT DOES OTHER STUFF FIRST. CHANGES PRIORITY TO THE SAME AS EARN SO ITS NOT INTERRUPTED ONCE RUNNING
			print_function('consume_drugs - queued')
			thread_add_to_queue(running_thread, waiting_thread_list, '8')
			print_function('consume_drugs - running')

			# MAKE SURE QUICK EARN AVAILABLE
			if element_found(lock_webdriver, "XPATH", ".//*[@id='nav_left']/p[5]/a[2]/img"):
				pass
			else:
				print_function('CONSUME DRUGS - NO QUICK EARN AVAILABLE')
				print_function('consume_drugs - finished')
				thread_remove_from_queue(running_thread, waiting_thread_list)
				return

			go_to_page(lock_webdriver, "ConsumeDrugs", running_thread)
			drugs_table = element_get_attribute(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='account_holder']/div[@id='account_profile']/div[@id='holder_content']", "innerHTML")
			consumed_24 = regex_match_between('Drugs consumed in the last 24 hours:', '\n', drugs_table)
			consumed_24 = re.sub('[^0-9]', "", consumed_24)
			coke_count = 0
			drugs_max = 0
			click_index = 0
			total_earns = int(config['Drugs']['TotalEarns'])
			if int(total_earns) >= 7000:
				drugs_max = 165
			elif int(total_earns) >= 5000:
				drugs_max = 132
			elif int(total_earns) >= 3000:
				drugs_max = 99
			elif int(total_earns) >= 1500:
				drugs_max = 66
			elif int(total_earns) < 1500:
				drugs_max = 33

			drugs_table_split = drugs_table.split('<div onclick')
			for item in drugs_table_split:
				if 'type=Cocaine' in item:
					item_split = item.splitlines()
					coke_count = item_split[3]
					coke_count = regex_match_between('>', '<', coke_count)
					click_index += 1
					break
				elif (('Marijuana' in item) or ('Ecstasy' in item) or ('Acid' in item) or ('Speed' in item) or ('Ice' in item) or ('Heroin ' in item)):
					click_index += 1
				else:
					continue

			running_thread[0] = str(priority_thread_earn) + inspect.stack()[0][3]
			drugs_finished = True
			while True:
				if (int(coke_count) == 0) or (int(consumed_24) >= int(drugs_max)):
					break
				else:
					print_function('CONSUME DRUGS - ' + str(consumed_24) + ' OF ' + str(drugs_max) + ' || coke remaining: ' + str(coke_count))

				# CONSUME COKE
				print_function(str(inspect_stack()) + 'CONSUME DRUGS - EARN QUICK - click cocaine')
				element_click(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='account_holder']/div[@id='account_profile']/div[@id='holder_content']/div[@id='consumables']/div[" + str(click_index) + "]", running_thread)

				# QUICK EARN
				print_function(str(inspect_stack()) + 'CONSUME DRUGS - EARN QUICK - click earn arrow')
				element_click(lock_webdriver, "XPATH", ".//*[@id='nav_left']/p[5]/a[2]/img", running_thread)

				print_function(str(inspect_stack()) + ' EARN QUICK - click earn bar')
				try:
					element_click(lock_webdriver, "NAME", "lastearn", running_thread)
					# OLD METHOD element_click(lock_webdriver, "XPATH", ".//*[@id='docTipsLayer']/div[@class='tipClass']/form/input", running_thread)
				except:
					continue

				WhichEarn = config['Earn']['WhichEarn']
				if WhichEarn == 'Streetfight':
					if 'Streetfight' in running_thread[4]:
						pass
					else:
						streetfight_options(lock_webdriver, running_thread)

						new_journal_entries = element_get_attribute(lock_webdriver, "XPATH",
																	"//*[@id='nav_left']/div[2]/a[1]/span", "outerHTML")
						new_journal_entries = re.sub('[^0-9]', "", new_journal_entries)
						if new_journal_entries == '':
							new_journal_entries = 0
						if int(new_journal_entries) > 0:
							drugs_finished = False
							break

						driver.get("https://mafiamatrix.com/profile/consumables.asp")
						driver.get("https://mafiamatrix.com/profile/consumables.asp")
				elif WhichEarn == 'Pimp':
					if 'Pimp' in running_thread[4]:
						pass
					else:
						pimp_options(lock_webdriver, running_thread)

						new_journal_entries = element_get_attribute(lock_webdriver, "XPATH",
																	"//*[@id='nav_left']/div[2]/a[1]/span", "outerHTML")
						new_journal_entries = re.sub('[^0-9]', "", new_journal_entries)
						if new_journal_entries == '':
							new_journal_entries = 0
						if int(new_journal_entries) > 0:
							drugs_finished = False
							break

						driver.get("https://mafiamatrix.com/profile/consumables.asp")
						driver.get("https://mafiamatrix.com/profile/consumables.asp")
				elif WhichEarn == 'Whore':
					if 'Whore' in running_thread[4]:
						pass
					else:
						whore_options(lock_webdriver, running_thread)

						new_journal_entries = element_get_attribute(lock_webdriver, "XPATH",
																	"//*[@id='nav_left']/div[2]/a[1]/span", "outerHTML")
						new_journal_entries = re.sub('[^0-9]', "", new_journal_entries)
						if new_journal_entries == '':
							new_journal_entries = 0
						if int(new_journal_entries) > 0:
							drugs_finished = False
							break

						driver.get("https://mafiamatrix.com/profile/consumables.asp")
						driver.get("https://mafiamatrix.com/profile/consumables.asp")
				elif WhichEarn == 'Joyride':
					if 'Joyride' in running_thread[4]:
						pass
					else:
						joyride_options(lock_webdriver, running_thread)

						new_journal_entries = element_get_attribute(lock_webdriver, "XPATH",
																	"//*[@id='nav_left']/div[2]/a[1]/span", "outerHTML")
						new_journal_entries = re.sub('[^0-9]', "", new_journal_entries)
						if new_journal_entries == '':
							new_journal_entries = 0
						if int(new_journal_entries) > 0:
							drugs_finished = False
							break

						driver.get("https://mafiamatrix.com/profile/consumables.asp")
						driver.get("https://mafiamatrix.com/profile/consumables.asp")

				consumed_24 = int(consumed_24) + 1
				coke_count = int(coke_count) - 1

			if drugs_finished:
				waiting_thread_list.append('9zterminate_earn_thread')
				print_function('9zterminate_earn_thread THREAD QUEUED' + str(waiting_thread_list), "GREEN")

				random_timer = random.randrange(1440, 1680)
				globals()['timers'].__dict__['consume_drugs_timer'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=random_timer)
				write_file("env/consume_drugs_timer.txt", str(datetime.datetime.utcnow() + datetime.timedelta(minutes=random_timer)))

				print_function('CONSUME DRUGS - FINISHED')
			else:
				print_function('CONSUME DRUGS - TEMPORARILY INTERRUPTED. LIKELY JOURNAL WHEN UNLOCKING SECRETS')
			print_function('consume_drugs - finished')
			thread_remove_from_queue(running_thread, waiting_thread_list)
	return


def update_unlocked_aggs(lock_webdriver, running_thread, waiting_thread_list):
	# CHECK UNLOCKED AGGS TIMER
	if 'CS:' in str(running_thread[4]):
		print_function("update_unlocked_aggs - skip as pending CS")
		return
	elif 'TIMEAGGS' in str(running_thread[3]):
		for item in running_thread[3]:
			if 'TIMEAGGS' in item:
				time_next_aggs_check = regex_match_between('TIMEAGGS:', None, item)
				try:
					time_next_aggs_check = datetime.datetime.strptime(time_next_aggs_check, '%Y-%m-%d %H:%M:%S')
				except:
					time_next_aggs_check = datetime.datetime.strptime(time_next_aggs_check, '%Y-%m-%d %H:%M:%S.%f')
				time_difference = time_next_aggs_check - datetime.datetime.utcnow()
				if '-' in str(time_difference):
					print_function('update_unlocked_aggs - queued - saved timer ready' + str(time_next_aggs_check))
					thread_add_to_queue(running_thread, waiting_thread_list, priority_thread_agg)
					print_function('update_unlocked_aggs - running')

					print_function('OPENING AGGS MENU FOR UNLOCKS')
					go_to_page(lock_webdriver, "AggsMenu", running_thread)

					print_function('update_unlocked_aggs - finished')
					thread_remove_from_queue(running_thread, waiting_thread_list)
	else:
		print_function('update_unlocked_aggs - queued - no saved timer')
		thread_add_to_queue(running_thread, waiting_thread_list, priority_thread_agg)
		print_function('update_unlocked_aggs - running')

		print_function('OPENING AGGS MENU FOR UNLOCKS')
		go_to_page(lock_webdriver, "AggsMenu", running_thread)

		print_function('update_unlocked_aggs - finished')
		thread_remove_from_queue(running_thread, waiting_thread_list)
	return


def middle_drugs(lock_webdriver, running_thread, waiting_thread_list):
	print_function('middle_drugs - queued')
	thread_add_to_queue(running_thread, waiting_thread_list, priority_thread_career)
	print_function('middle_drugs - running')
	go_to_page(lock_webdriver, "Drug_Deal", running_thread)

	supplier_list_raw = element_get_attribute(lock_webdriver, 'XPATH',
						  ".//*[@id='content']/div[@id='shop_holder']/div[@id='holder_content']/table[@class='column_title']",
						  'innerHTML')

	suppliers = []
	supplier_list = supplier_list_raw.splitlines()
	for supplier_line in supplier_list:
		if 'deals.asp' in supplier_line:
			supplier = regex_match_between('id=\d\d\d\d">', '</a>', supplier_line)
			print_function(supplier)
			suppliers.append(supplier)

	print_function('suppliers: ' + str(suppliers))
	for supplier in suppliers:
		element_click(lock_webdriver, "LINK", str(supplier), running_thread)
		drugs_table_raw = element_get_attribute(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='shop_holder']/div[@id='holder_content']/table", "innerHTML")

		weed_stock = 0
		weed_price = 0
		heroin_stock = 0
		heroin_price = 0
		coke_stock = 0
		coke_price = 0

		for drugs_table_entry in drugs_table_raw.split("<tr>"):
			if 'marijuana.gif' in str(drugs_table_entry):
				print_function('drugs table weed: ' + str(drugs_table_entry))
				drugs_table_line = drugs_table_entry.split("<td ")
				weed_price = drugs_table_line[3]
				weed_price = regex_match_between(';', '&', weed_price)
				weed_price = re.sub('[^0-9]', "", weed_price)
				weed_stock = drugs_table_line[4]
				weed_stock = regex_match_between(';', '&', weed_stock)
				weed_stock = re.sub('[^0-9]', "", weed_stock)
			elif 'heroin.gif' in str(drugs_table_entry):
				print_function('drugs table heroin: ' + str(drugs_table_entry))
				drugs_table_line = drugs_table_entry.split("<td ")
				heroin_price = drugs_table_line[3]
				heroin_price = regex_match_between(';', '&', heroin_price)
				heroin_price = re.sub('[^0-9]', "", heroin_price)
				heroin_stock = drugs_table_line[4]
				heroin_stock = regex_match_between(';', '&', heroin_stock)
				heroin_stock = re.sub('[^0-9]', "", heroin_stock)
			elif 'cocaine.gif' in str(drugs_table_entry):
				print_function('drugs table coke: ' + str(drugs_table_entry))
				drugs_table_line = drugs_table_entry.split("<td ")
				coke_price = drugs_table_line[3]
				coke_price = regex_match_between(';', '&', coke_price)
				coke_price = re.sub('[^0-9]', "", coke_price)
				coke_stock = drugs_table_line[4]
				coke_stock = regex_match_between(';', '&', coke_stock)
				coke_stock = re.sub('[^0-9]', "", coke_stock)

		print_function('WEED: ' + str(weed_stock) + ' @ ' + str(weed_price) + ' | H: ' + str(heroin_stock) + ' @ ' + str(heroin_price) + ' | COKE: ' + str(coke_stock) + ' @ ' + str(coke_price))
		if (int(coke_stock) > 0) or (int(heroin_stock) > 0) or (int(weed_stock) > 0):
			# TRY BUY
			temp_capacity = int(config['Drugs']['CarryCapacity'])

			# BUY COKE
			if int(coke_stock) > 0:
				if int(coke_stock) > int(temp_capacity):
					coke_stock = temp_capacity
				temp_capacity = int(temp_capacity) - int(coke_stock)
				if int(coke_stock) > 0:
					clearkeys(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='shop_holder']/div[@id='holder_content']/table/tbody/tr[10]/td[@class='display_border'][5]/input[@class='input']")
					sendkeys(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='shop_holder']/div[@id='holder_content']/table/tbody/tr[10]/td[@class='display_border'][5]/input[@class='input']", str(coke_stock))

			# BUY HEROIN
			if int(heroin_stock) > 0:
				if int(heroin_stock) > int(temp_capacity):
					heroin_stock = temp_capacity
				temp_capacity = int(temp_capacity) - int(heroin_stock)
				if int(heroin_stock) > 0:
					clearkeys(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='shop_holder']/div[@id='holder_content']/table/tbody/tr[9]/td[@class='display_border'][5]/input[@class='input']")
					sendkeys(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='shop_holder']/div[@id='holder_content']/table/tbody/tr[9]/td[@class='display_border'][5]/input[@class='input']", str(heroin_stock))

			# BUY WEED
			if int(weed_stock) > 0:
				if int(weed_stock) > int(temp_capacity):
					weed_stock = temp_capacity
				temp_capacity = int(temp_capacity) - int(weed_stock)
				if int(weed_stock) > 0:
					clearkeys(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='shop_holder']/div[@id='holder_content']/table/tbody/tr[4]/td[@class='display_border'][5]/input[@class='input']")
					sendkeys(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='shop_holder']/div[@id='holder_content']/table/tbody/tr[4]/td[@class='display_border'][5]/input[@class='input']", str(weed_stock))

			# CLICK BUY
			element_click(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='shop_holder']/div[@id='holder_content']/table/tbody/tr[@class='nohover'][4]/td[@class='s1'][2]/input[@class='submit']", running_thread)

			if element_found(lock_webdriver, "ID", "success"):
				results = element_get_attribute(lock_webdriver, "ID", "success", "innerHTML")
			elif element_found(lock_webdriver, "ID", "fail"):
				results = element_get_attribute(lock_webdriver, "ID", "fail", "innerHTML")

			if ('same city' in str(results)) or ('their Home City' in str(results)):
				go_to_page(lock_webdriver, "Drug_Deal", running_thread)
			elif ('You are now carrying drugs' in str(results)):
				# make variable of the drugs we hold
				input('bought drugs')
			else:
				print_function('new middle buy results: ' + str(results))
				input('done')
				break
		else:
			go_back(lock_webdriver)

	print_function('middle_drugs - finished')
	thread_remove_from_queue(running_thread, waiting_thread_list)
	return


def vehicle_cancel_repair(lock_webdriver, running_thread, waiting_thread_list):
	print_function('vehicle_cancel_repair - queued')
	thread_add_to_queue(running_thread, waiting_thread_list, priority_thread_career)
	print_function('vehicle_cancel_repair - running')

	open_city(lock_webdriver, running_thread)

	# OPEN CONSTRUCTION
	element_click(lock_webdriver, "XPATH", ".//*[@class='business vehicle_repair_shop']", running_thread)

	# CONSTRUCTION TORCHED
	if element_found(lock_webdriver, "ID", "fail"):
		results = element_get_attribute(lock_webdriver, "ID", "fail", "innerHTML")
		if 'while under going repairs' in str(results):
			# SET TIMER FOR RECHECK LATER
			print_function('REPAIR - CONSTRUCTION TORCHED')
			random_timer = random.randrange(20, 30)
			globals()['timers'].__dict__['repair_timer'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=random_timer)

			print_function('vehicle_cancel_repair - finished')
			thread_remove_from_queue(running_thread, waiting_thread_list)
			profile_check(lock_webdriver, running_thread, waiting_thread_list, None)
			return

	url_check = get_url(lock_webdriver)
	if 'repairs.asp' in url_check:
		# ON CORRECT PAGE

		if element_found(lock_webdriver, "XPATH", ".//*[@id='show_vehrepairs']/table[@id='username_content']/tbody/tr[4]/td[@class='box']/div[@id='respect_bar']"):
			results = element_get_attribute(lock_webdriver, "XPATH", ".//*[@id='show_vehrepairs']/table[@id='username_content']/tbody/tr[4]/td[@class='box']/div[@id='respect_bar']", "innerHTML")
			results = re.sub('[^0-9]', "", results)

			if int(results) == 0:
				# BROKEN DOWN
				if element_found(lock_webdriver, "XPATH", ".//*[@id='show_vehrepairs']/div[@id='success']/a"):
					print_function('VEHICLE CANCEL REPAIR - FULLY BROKEN DOWN & ALREADY AWAITING REPAIR')
					variables_list = running_thread[4]
					for item in running_thread[4]:
						if 'Vehicle:' in item:
							try:
								variables_list.remove(item)
							except:
								pass
					variables_list.append('Vehicle:BrokenDownAwaitingRepair')
					running_thread[4] = variables_list
					print_function('UPDATED VARIABLES FOR VEHICLE: ' + str(running_thread[4]))
					write_file("env/variables.txt", running_thread[4])
				else:
					print_function('REPAIR - PUT IN FOR REPAIRS')
					select_dropdown_option(lock_webdriver, "XPATH", ".//*[@id='show_vehrepairs']/form/p[2]/select[@class='dropdown']", "Yes")
					element_click(lock_webdriver, "XPATH", ".//*[@class='input']", running_thread)

					# CHECK VEHICLE PUT IN FOR REPAIR
					variables_list = running_thread[4]
					for item in running_thread[4]:
						if 'Vehicle:' in item:
							try:
								variables_list.remove(item)
							except:
								pass

					if element_found(lock_webdriver, "ID", "success"):
						results = element_get_attribute(lock_webdriver, "ID", "success", "innerHTML")
						if 'in for repairs' in results:
							variables_list.append('Vehicle:BrokenDownAwaitingRepair')
							running_thread[4] = variables_list
							print_function('UPDATED VARIABLES FOR VEHICLE: ' + str(running_thread[4]))
							write_file("env/variables.txt", running_thread[4])
			else:
				# CANCEL REPAIR
				if element_found(lock_webdriver, "XPATH", ".//*[@id='show_vehrepairs']/div[@id='success']/a"):
					element_click(lock_webdriver, "XPATH", ".//*[@id='show_vehrepairs']/div[@id='success']/a", running_thread)

					# REPAIR NOT NEEDED
					print_function('REPAIR - NOT NEEDED')
					variables_list = running_thread[4]
					for item in running_thread[4]:
						if 'Vehicle:' in item:
							try:
								variables_list.remove(item)
							except:
								pass
					variables_list.append('Vehicle:Repaired')
					running_thread[4] = variables_list
					print_function('UPDATED VARIABLES FOR VEHICLE: ' + str(running_thread[4]))
					write_file("env/variables.txt", running_thread[4])
				else:
					# REPAIR NOT NEEDED
					print_function('REPAIR - NOT NEEDED')
					variables_list = running_thread[4]
					for item in running_thread[4]:
						if 'Vehicle:' in item:
							try:
								variables_list.remove(item)
							except:
								pass
					variables_list.append('Vehicle:Repaired')
					running_thread[4] = variables_list
					print_function('UPDATED VARIABLES FOR VEHICLE: ' + str(running_thread[4]))
					write_file("env/variables.txt", running_thread[4])
		else:
			print_function('REPAIR - NOT NEEDED')
			variables_list = running_thread[4]
			for item in running_thread[4]:
				if 'Vehicle:' in item:
					try:
						variables_list.remove(item)
					except:
						pass
			variables_list.append('Vehicle:Repaired')
			running_thread[4] = variables_list
			print_function('UPDATED VARIABLES FOR VEHICLE: ' + str(running_thread[4]))
			write_file("env/variables.txt", running_thread[4])

	print_function('vehicle_cancel_repair - finished')
	thread_remove_from_queue(running_thread, waiting_thread_list)
	return


def suicide_killswitch(lock_webdriver, running_thread, waiting_thread_list):
	thread_add_to_queue(running_thread, waiting_thread_list, 1)
	driver.get("https://mafiamatrix.com/profile/suicide.asp")
	driver.get("https://mafiamatrix.com/profile/suicide.asp")
	sendkeys(lock_webdriver, "XPATH", ".//*[@id='account_profile']/div[@id='holder_content']/form/p[4]/input[@class='input'][1]", config['Auth']['password'])
	element_click(lock_webdriver, "XPATH", ".//*[@id='account_profile']/div[@id='holder_content']/form/p[4]/input[@class='input'][2]", running_thread)
	discord_message(config['Auth']['discord_id'] + "@here SUICIDE KILLSWITCH ENGAGED")
	sys.exit("Suicide Killswitch HUEHUEHUE")
	thread_remove_from_queue(running_thread, waiting_thread_list)
	return

def event_halloween(lock_webdriver, running_thread, waiting_thread_list, which_event):
	print_function('event - queued')
	thread_add_to_queue(running_thread, waiting_thread_list, priority_thread_earn)
	print_function('event - running')

	url_check = get_url(lock_webdriver)
	if 'main.asp' in url_check:
		pass
	else:
		click_refresh(lock_webdriver, running_thread)

	if which_event == 'Halloween':
		element_click(lock_webdriver, "XPATH", ".//*[@class='halloweenboss acceptbutton']", running_thread)
	elif which_event == 'Christmas':
		element_click(lock_webdriver, "XPATH", ".//*[@class='christmasboss acceptbutton']", running_thread)
	elif which_event == 'Easter':
		element_click(lock_webdriver, "XPATH", ".//*[@class='easterboss acceptbutton']", running_thread)

	if element_found(lock_webdriver, "XPATH", ".//*[@class='declinebutton']"):
		# ATTACK BOSS
		element_click(lock_webdriver, "XPATH", ".//*[@class='declinebutton']", running_thread)
		globals()['timers'].__dict__['event_timer'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=get_timer(lock_webdriver, 'Event', running_thread))
	else:
		# NO BOSS IN CITY
		random_timer = random.randrange(840, 1260) # 15 - 20 mins
		globals()['timers'].__dict__['event_timer'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=random_timer)
		print_function('NO BOSS IN CITY')
	print_function('event - finished')
	thread_remove_from_queue(running_thread, waiting_thread_list)
	return


def boys_work_fire(lock_webdriver, running_thread, waiting_thread_list, boys_list, online_list, your_character_name, current_city, home_city):
	# fire need to count fires per city?
	# also timer for fires inspection per city (incase foreign businesses)
	# profile track businesses owned and use that
	boys_fire = False
	for boys_name in boys_list:
		if boys_name == str(your_character_name):
			continue
		elif boys_name in online_list:
			print_function(str(boys_name) + ' fire')
			boys_fire = True

	if boys_fire:
		pass
		if ( (home_city == current_city) and (current_city != None) ):
			if 'profile-house:None' in str(running_thread[4]):
				pass
			else:
				fire_inspection_timer = read_file("env/fireinspection_house_timer.txt")
				fire_inspection_timer = datetime.datetime.strptime(fire_inspection_timer, '%Y-%m-%d %H:%M:%S.%f')
				time_difference = datetime.datetime.utcnow() - fire_inspection_timer
				if not '-' in str(time_difference):
					thread_add_to_queue(running_thread, waiting_thread_list, priority_thread_action)

					open_city(lock_webdriver, running_thread)
					element_click(lock_webdriver, "XPATH", ".//*[@class='fire_station']", running_thread)

					# OPEN INSPECTIONS
					element_click(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='account_holder']/div[@id='account_nav']/ul/li[5]/a", running_thread)

					# REQUEST INSPECTION
					if element_found(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='account_holder']/div[@id='account_profile']/div[@id='holder_content']/form/p/input[@class='input']"):
						element_click(lock_webdriver, "XPATH", ".//*[@id='content']/div[@id='account_holder']/div[@id='account_profile']/div[@id='holder_content']/form/p/input[@class='input']", running_thread)
					else:
						# NO HOUSE. GOT HERE IN ERROR
						random_timer = random.randrange(1443, 1563)  # 24 - 26 hours
						write_file("env/fireinspection_house_timer.txt", str(datetime.datetime.utcnow() + datetime.timedelta(minutes=random_timer)))
						thread_remove_from_queue(running_thread, waiting_thread_list)
						return

					# UPDATE BOYS
					sqs = boto3.resource('sqs',
										 region_name='ap-southeast-2',
										 aws_access_key_id='AKIAVJNIZJYFC24IQCMU',
										 aws_secret_access_key='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',
										 )
					for boys_name in boys_list:
						if boys_name in online_list:
							try:
								queue = sqs.get_queue_by_name(QueueName=str(boys_name))
							except:
								continue
							response = queue.send_message(MessageBody="ResetCaseTimer", DelaySeconds=1)
							print_function('BOYS FIRE - RESET TIMER FOR ' + str(boys_name))

					random_timer = random.randrange(1443, 1563)  # 24 - 26 hours
					write_file("env/fireinspection_house_timer.txt", str(datetime.datetime.utcnow() + datetime.timedelta(minutes=random_timer)))

					thread_remove_from_queue(running_thread, waiting_thread_list)

		# if busniess profile records and in that city then check timer & fire inspection
		# if fires count current city > 0 then report fire
	return


def get_online_list_city(lock_webdriver, running_thread):
	# CLEAR SAVED NAMES
	online_player_list_currentcity = []

	# GETS FULL LIST OF NAMES
	while True:
		online_player_list_raw = element_get_attribute(lock_webdriver, "ID", "whosonlinecell", "innerHTML")
		if '|' in online_player_list_raw:
			break

	is_local_list_only = True
	if '*' in online_player_list_raw:
		is_local_list_only = False

	online_player_list_raw_split = online_player_list_raw.split("|")
	for player_raw in online_player_list_raw_split:
		if ':Alive:player:' in player_raw:
			if is_local_list_only or ('*' in player_raw):
				player_name = regex_match_between('>', '<', player_raw)
				online_player_list_currentcity.append(player_name)
	return online_player_list_currentcity

def misc_thread(lock_webdriver, running_thread, waiting_thread_list, aggtarget_person_list_manager, aggtarget_business_list_manager):
	# GET INITIAL TIMERS

	'''
	player_database = get_from_database('Player', None)
	item_count = (len(player_database['Items']) - 1)
	while item_count >= 0:
		try:
			player_alive_status = player_database['Items'][item_count]['AliveStatus']
		except:
			player_alive_status == ""

		if str(player_alive_status) == "Alive":
			try:
				name = player_database['Items'][item_count]['PlayerName']
				hours = player_database['Items'][item_count]['Hours']

				if (int(hours) >= 500):
					print(name, '\t', hours)
			except:
				pass

		item_count -= 1


	print('done')
	while True:
		time.sleep(30)
	'''


	'''
	known_deaths_list = read_s3('roastbusters', 'PromoRecords/ElJugador.txt')
	print(known_deaths_list)
	while True:
		time.sleep(30)
	'''


	try:
		response = get_from_database('Timers', 'NextTimer, LockedUntil', "Key('Timer').eq('CityList')")
	except:
		print("citylist timers not found - using now")
	try:	
		citylist_locked_until = datetime.datetime.strptime(response['Items'][0]['LockedUntil'], '%Y-%m-%d %H:%M:%S.%f')
	except: 
		citylist_locked_until = (datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
	try:
		next_citylist_timer = datetime.datetime.strptime(response['Items'][0]['NextTimer'], '%Y-%m-%d %H:%M:%S.%f')
	except:
		next_citylist_timer = (datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
	print_function("CITY LIST - GET INITIAL TIMER " + str(next_citylist_timer) + " / " + str(citylist_locked_until), "GREEN")

	try:
		response = get_from_database('Timers', 'NextTimer, LockedUntil', "Key('Timer').eq('Obituaries')")
	except:
		print("obituaries timers not found - using now")
	try:
		obituaries_locked_until = datetime.datetime.strptime(response['Items'][0]['LockedUntil'], '%Y-%m-%d %H:%M:%S.%f')
	except:
		obituaries_locked_until = (datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
	try:
		next_obituaries_timer = datetime.datetime.strptime(response['Items'][0]['NextTimer'], '%Y-%m-%d %H:%M:%S.%f')
	except:
		next_obituaries_timer = (datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
	print_function("OBITUARIES - GET INITIAL TIMER " + str(next_obituaries_timer) + " / " + str(obituaries_locked_until), "GREEN")

	try:
		response = get_from_database('Timers', 'NextTimer, LockedUntil', "Key('Timer').eq('OnlineHours')")
	except:
		print("online hoursnot found - using now")
	try:
		onlinehours_locked_until = datetime.datetime.strptime(response['Items'][0]['LockedUntil'], '%Y-%m-%d %H:%M:%S.%f')
	except:
		onlinehours_locked_until = (datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
	try:
		next_onlinehours_timer = datetime.datetime.strptime(response['Items'][0]['NextTimer'], '%Y-%m-%d %H:%M:%S.%f')
	except:
		next_onlinehours_timer = (datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
	print_function("ONLINE HOURS - GET INITIAL TIMER " + str(next_onlinehours_timer) + " / " + str(onlinehours_locked_until), "GREEN")


	try:
		running_thread[1] = datetime.datetime.utcnow()

		# GET BOYS LISTS
		globals()['Boys_Launder_List'] = []
		globals()['All_Boys_List'] = []
		for city in globals()['cities_list']:
			globals()['Boys_Fire_' + str(city)] = []
			globals()['Boys_Hospital_' + str(city)] = []
		globals()['Boys_Engineer'] = []

		response = get_from_database('Boys', 'PlayerName, Career, HomeCity')
		print_function('response: ' + str(response))
		for item in response['Items']:
			boys_name = item['PlayerName']
			boys_city = item['HomeCity']
			boys_career = item['Career']
			# print_function('Boys: ' + str(boys_name) + " " + str(boys_city) + " " + str(boys_career))

			globals()['All_Boys_List'].append(boys_name)

			if 'Bank' in str(boys_career):
				globals()['Boys_Launder_List'].append(boys_name)
			elif 'Hospital' in str(boys_career):
				globals()['Boys_Hospital_' + str(boys_city)].append(boys_name)
			elif 'Engineering' in str(boys_career):
				globals()['Boys_Engineer'].append(boys_name)
			elif 'Fire' in str(boys_career):
				globals()['Boys_Fire_' + str(boys_city)].append(boys_name)

		last_click_timer = None
		judge_boys_list = None
		globals()['resting_page'] = 'None'

		# NAME CHANGE / NEW CHARACTER CHECK
		variables_list = running_thread[4]
		character_name = None

		# GET DETAILS FOR DATABASE UPDATE
		for item in running_thread[4]:
			if 'CharacterName:' in item:
				character_name = regex_match_between('CharacterName:', None, item)

		your_character_name = None
		your_character_name = None
		rank = None
		occupation = None
		your_clean_money = None
		dirty_money = None
		current_city = None
		home_city = None
		next_line = None
		globals()['timers'].set_online_list_timer()

		while True:
			while True:
				if 'In-Jail' in str(running_thread[4]):
					print_function("IN JAIL", "RED")
					while 'In-Jail' in str(running_thread[4]):
						time.sleep(30)
					print_function("OUT OF JAIL", "RED")

				try:
					print_function("RIGHT BAR 1")
					right_bar_details = element_get_attribute(lock_webdriver, 'XPATH',
															  "/html/body[@id='body']/div[@id='wrapper']/div[@id='nav_right']",
															  'innerHTML')
					break
				except:
					print_function("MISC - GET RIGHT BAR FAILED", "RED")
					time.sleep(1)
					pass
			right_bar_line = right_bar_details.splitlines()

			desired_money_on_hand = int(config['Misc']['DesiredMoneyOnHand'])
			for line in right_bar_line:
				print("misc - right bar line:" + str(line))

				if str(line) == "":
					continue
				elif 'Name </div>' in str(line):
					print("misc - rightbar - next: yourname")
					next_line = 'YourName'
					continue
				elif 'Rank' in str(line):
					if 'Next Rank:' in str(line):
						print("misc - rightbar - next rank - pass")
						pass
					else:
						next_line = 'Rank'
						print("misc - rightbar - next: rank")
						continue
				elif 'Occupation </div>' in str(line):
					next_line = 'Occupation'
					print("misc - rightbar - next: occupation")
					continue
				elif 'Dirty money' in str(line):
					print("misc - rightbar - next: dirtymoney")
					next_line = 'DirtyMoney'
					continue
				elif 'Location' in str(line):
					print("misc - rightbar - next: currentcity")
					next_line = 'CurrentCity'
					continue
				elif 'Home City' in str(line):
					print("misc - rightbar - next: homecity")
					next_line = 'HomeCity'
					continue

				if (next_line == 'YourName') and ('userprofile.asp' in str(line)):
					your_character_name = regex_match_between('username\=', '">', line)
					print("misc - rightbar - yourname: " + str(your_character_name))
					next_line = None
				elif (next_line == 'Rank') and ('display' in str(line)):
					rank = regex_match_between('>', '<', line)
					print("misc - rightbar - rank: " + str(rank))
					next_line = None
				elif (next_line == 'Occupation') and ('display' in str(line)):
					occupation = regex_match_between('>', '<', line)
					print("misc - rightbar - occupation: " + str(occupation))
					next_line = None
				elif ('Clean money' in str(line)):
					your_clean_money = regex_match_between('value="', '"', line)
					your_clean_money = re.sub('[^0-9]', "", your_clean_money)
					print("misc - rightbar - your_clean_money: " + str(your_clean_money))
				elif (next_line == 'DirtyMoney') and ('$' in str(line)):
					dirty_money = regex_match_between('>', '<', line)
					dirty_money = re.sub('[^0-9]', "", dirty_money)
					print("misc - rightbar - dirty_money: " + str(dirty_money))
					next_line = None
				elif (next_line == 'CurrentCity') and ('display' in str(line)):
					current_city = regex_match_between('>', '<', line)
					current_city = current_city.replace(' ', '')
					print("misc - rightbar - current_city: " + str(current_city))
					next_line = None
				elif (next_line == 'HomeCity') and ('display' in str(line)):
					home_city = regex_match_between('>', '<', line)
					home_city = home_city.replace(' ', '')
					print("misc - rightbar - home_city: " + str(home_city))
					next_line = None

			if ( (your_character_name is None) or (rank is None) or (occupation is None) or (your_clean_money is None) or (dirty_money is None) or (current_city is None) or (home_city is None) ):
				if 'Jail Rank' in right_bar_details:
					pass
				else:
					print_function("MISC THREAD - FAILED TO GET RIGHT BAR VARIABLES", "RED")
					print("name: " + str(your_character_name))
					print("rank: " + str(rank))
					print("clean: " + str(your_clean_money))
					print("dirty: " + str(dirty_money))
					print("current_city: " + str(current_city))
					print("home_city: " + str(home_city))
					print("occupation: " + str(occupation))
					exit()
			else:
				break


		import multiprocessing
		print_function("MISC THREAD STARTED - CURRENT / HOME CITY " + str(current_city) + ' / ' + str(home_city) + ' | PID: ' + str(multiprocessing.current_process().pid), "GREEN")


		if ('Bank' in occupation) or ('Loan' in occupation):
			career = "Bank"
		elif ('Surgeon' in occupation) or ('Hospital' in occupation):
			career = "Hospital"
		elif ('Mechanic' in occupation) or ('Technician' in occupation) or ('Engineer' in occupation):
			career = "Engineering"
		elif ('Mortician' in occupation) or ('Undertaker' in occupation) or ('Funeral' in occupation):
			career = "Funeral"
		elif ('Fire' in occupation):
			career = "Fire"
		elif ('Lawyer' in occupation):
			career = "Lawyer"
		elif ('Judge' in occupation):
			career = "Judge"
		elif ('Inspector' in rank) or ('Supervisor' in rank) or ('Superintendent' in rank) or ('Commissioner-General' in rank):
			career = "Customs"
		elif ('Police Officer' in occupation):
			career = "Police"
		elif ('Gangster' in occupation):
			career = "Gangster"
		else:
			career = "None"

		import socket
		update_database('Boys', 'PlayerName', your_character_name, {"Career": career, "HomeCity": home_city, "Version": str(globals()['timers'].__dict__['bot_version']), "LastLogin": str(datetime.datetime.utcnow()), "Comp": str(socket.gethostname())})

		if character_name is None:
			variables_list = running_thread[4]
			variables_list.append("CharacterName:" + str(your_character_name))
			running_thread[4] = variables_list
			write_file("env/variables.txt", running_thread[4])
		else:
			your_character_name = str(your_character_name)
			if character_name == your_character_name:
				pass
			else:
				variables_list = running_thread[4]
				for item in running_thread[4]:
					if 'CharacterName:' in item:
						try:
							variables_list.remove(item)
						except:
							pass
				variables_list.append("CharacterName:" + str(your_character_name))
				running_thread[4] = variables_list
				write_file("env/variables.txt", running_thread[4])
				discord_message(config['Auth']['discord_id'] + str(your_character_name) + " NEW CHARACTER OR NAME CHANGE - RESTART THE SCRIPT IF CHANGE / RUN CLEANUP SCRIPT IF NEW")
				sys.exit("NEW CHARACTER NAME - RESTART THE SCRIPT IF THIS IS JUST A NAME CHANGE. OTHERWISE RUN RESET SCRIPT IF A NEW CHARACTER")
				return

		# suicide_killswitch(lock_webdriver, running_thread, waiting_thread_list)
		# middle_drugs(lock_webdriver, running_thread, waiting_thread_list)
		# profile_check(lock_webdriver, running_thread, waiting_thread_list)
		# profile check set timer whenever open. manually do a check daily

		print_function("MISC THREAD - LOOP STARTED", "GREEN")
		while True:
			# ONLY GET DETAILS IF THE PAGE HAS REFRESHED SINCE LAST TIME
			if last_click_timer != running_thread[1]:
				right_bar_details = running_thread[2]
				if right_bar_details == '':

					while True:
						try:
							print_function("RIGHT BAR 2")
							running_thread[2] = element_get_attribute(lock_webdriver, 'XPATH',
																	  "/html/body[@id='body']/div[@id='wrapper']/div[@id='nav_right']",
																	  'innerHTML')
							break
						except:
							pass

					right_bar_details = running_thread[2]
				right_bar_line = right_bar_details.splitlines()

				if 'Jail Rank' in right_bar_details:
					if 'In-Jail' in str(running_thread[4]):
						pass
					else:
						variables_list = running_thread[4]
						variables_list.append('In-Jail')
						running_thread[4] = variables_list
						print_function('UPDATED VARIABLES FOR IN-JAIL: ' + str(running_thread[4]))
						write_file("env/variables.txt", running_thread[4])
						waiting_thread_list.append('9zterminate-everything')
						print_function('9zterminate-everything THREAD QUEUED AS IN OR OUT OF JAIL - QUEUED VIA MISC THREAD ' + str(waiting_thread_list), "GREEN")
				else:
					# NOT IN JAIL
					if 'In-Jail' in str(running_thread[4]):
						variables_list = running_thread[4]
						try:
							variables_list.remove('In-Jail')
						except:
							pass
						running_thread[4] = variables_list
						print_function('UPDATED VARIABLES FOR NOT IN-JAIL: ' + str(running_thread[4]))
						write_file("env/variables.txt", running_thread[4])

				if 'In-Jail' in str(running_thread[4]):
					pass
				else:
					your_character_name = regex_match_between('username\=', '">', right_bar_line[4])
					rank = regex_match_between('>', '<', right_bar_line[7])
					occupation = regex_match_between('>', '<', right_bar_line[11])
					desired_money_on_hand = int(config['Misc']['DesiredMoneyOnHand'])
					your_clean_money = regex_match_between('value="', '"', right_bar_line[15])
					your_clean_money = re.sub('[^0-9]', "", your_clean_money)
					dirty_money = regex_match_between('>', '<', right_bar_line[18])
					dirty_money = re.sub('[^0-9]', "", dirty_money)
					current_city = None
					current_city = regex_match_between('>', '<', right_bar_line[21])
					current_city = current_city.replace(' ', '')
					home_city = None
					home_city = regex_match_between('>', '<', right_bar_line[23])
					home_city = home_city.replace(' ', '')
					# rank_percent = regex_match_between('title="', '"', right_bar_line[36])
					warmode_check = right_bar_line[9]
					if 'display_red' in warmode_check:
						warmode_on = True
					else:
						warmode_on = False

					# GET ONLINE LIST FOR BOYS WORK
					online_list_city = get_online_list_city(lock_webdriver, running_thread)

					# BLACKLIST AGG BIZ IF OWNED BY TOP LEGIT
					if 'Chief Engineer' in occupation:
						if not 'Construction' in config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city]:
							config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] = config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] + ' Construction'
					elif 'Bank Manager' in occupation:
						if not 'Bank' in config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city]:
							config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] = config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] + ' Bank'
					elif 'Hospital Director' in occupation:
						if not 'Hospital' in config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city]:
							config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] = config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] + ' Hospital'
					elif 'Funeral Director' in occupation:
						if not 'Funeral' in config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city]:
							config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] = config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] + ' Funeral'
					elif 'Fire Chief' in occupation:
						if not 'Fire' in config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city]:
							config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] = config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] + ' Fire'
					elif 'Commissioner-General' in rank:
						if not 'Airport' in config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city]:
							config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] = config['ArmedRobbery']['ArmedRobbery_Blacklist_' + home_city] + ' Airport'


					if 'SellItem' in str(waiting_thread_list):
						for thread in waiting_thread_list:
							if 'SellItem' in thread:
								profile_check(lock_webdriver, running_thread, waiting_thread_list, str(thread))

					# BOYS WORK - change these to run at start, when travel and on timer
					boys_work_fire(lock_webdriver, running_thread, waiting_thread_list, globals()['Boys_Fire_' + str(current_city)], online_list_city, your_character_name, current_city, home_city)

					boys_work_hospital(lock_webdriver, running_thread, waiting_thread_list, globals()['Boys_Hospital_' + str(current_city)], online_list_city, your_character_name)

					# WITHDRAW IF CASH ON HAND BELOW DESIRED
					withdraw_money_misc(lock_webdriver, running_thread, waiting_thread_list, desired_money_on_hand,
										your_clean_money)

					# RESTING PAGE TIMER
					globals()['timers'].__dict__['resting_page_timer'] = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)

				# STILL CHECKED IF IN JAIL?
				# MESSAGES & JOURNAL ONLY CHECKED AFTER PAGE REFRESH
				check_messages(lock_webdriver, running_thread, waiting_thread_list, occupation)
				check_journal(lock_webdriver, running_thread, waiting_thread_list, aggtarget_person_list_manager, aggtarget_business_list_manager, globals()['All_Boys_List'])

				last_click_timer = running_thread[1]

			if 'In-Jail' in str(running_thread[4]):
				pass
			else:
				# SEND MESSAGE
				if 'SendMessage' in str(waiting_thread_list):
					for thread in waiting_thread_list:
						if 'SendMessage' in thread:
							send_message(lock_webdriver, running_thread, waiting_thread_list, str(thread))

				# RESET TIMER IF REMOTE CONTROL
				if 'ResetCaseTimer' in str(waiting_thread_list):
					globals()['timers'].__dict__['case_timer'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=get_timer(lock_webdriver, 'Case', running_thread))
					globals()['timers'].__dict__['career_timer'] = datetime.datetime.utcnow()
					print_function("CASE TIMER RESET", "BLUE")
					for thread in waiting_thread_list:
						if 'ResetCaseTimer' in thread:
							try:
								waiting_thread_list.remove(thread)
							except:
								pass
				if 'ResetLaunderTimer' in str(waiting_thread_list):
					globals()['timers'].__dict__['launder_timer'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=get_timer(lock_webdriver, 'Launder', running_thread))
					print_function("LAUNDER TIMER RESET", "BLUE")
					for thread in waiting_thread_list:
						if 'ResetLaunderTimer' in thread:
							try:
								waiting_thread_list.remove(thread)
							except:
								pass
				if 'ResetTravelTimer' in str(waiting_thread_list):
					globals()['timers'].__dict__['travel_timer'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=get_timer(lock_webdriver, 'Travel', running_thread))
					print_function("TRAVEL TIMER RESET", "BLUE")
					for thread in waiting_thread_list:
						if 'ResetTravelTimer' in thread:
							try:
								waiting_thread_list.remove(thread)
							except:
								pass

				# EVENT TIMER
				if ( ('Halloween' in str(config['Misc']['Event'])) or ('Christmas' in str(config['Misc']['Event'])) or ('Easter' in str(config['Misc']['Event'])) ):
					if globals()['timers'].__dict__['event_timer'] is None:
						globals()['timers'].__dict__['event_timer'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=get_timer(lock_webdriver, 'Event', running_thread))

					time_difference = datetime.datetime.utcnow() - globals()['timers'].__dict__['event_timer']
					if not '-' in str(time_difference):
						event_halloween(lock_webdriver, running_thread, waiting_thread_list, str(config['Misc']['Event']))

				# ONLINE HOURS
				#if online_time_record(lock_webdriver, running_thread, waiting_thread_list, next_onlinehours_timer, onlinehours_locked_until):
					# ONLINE HOURS WAS UPDATED - RECHECK TIMERS
					#response = get_from_database('Timers', 'NextTimer, LockedUntil', "Key('Timer').eq('OnlineHours')")
					#onlinehours_locked_until = datetime.datetime.strptime(response['Items'][0]['LockedUntil'], '%Y-%m-%d %H:%M:%S.%f')
					#next_onlinehours_timer = datetime.datetime.strptime(response['Items'][0]['NextTimer'], '%Y-%m-%d %H:%M:%S.%f')
					#print_function("ONLINE HOURS - GET TIMER AFTER ONLINE HOURS" + str(next_onlinehours_timer) + " / " + str(onlinehours_locked_until), "GREEN")


				# OBITUARIES
				if obituaries(lock_webdriver, running_thread, waiting_thread_list, next_obituaries_timer, obituaries_locked_until):
					# OBITUARIES WAS UPDATED - RECHECK TIMERS
					obituaries_response = get_from_database('Timers', 'Obituaries, NextTimer, LockedUntil')
					obituaries_locked_until = datetime.datetime.strptime(obituaries_response['Items'][0]['LockedUntil'], '%Y-%m-%d %H:%M:%S.%f')
					next_obituaries_timer = datetime.datetime.strptime(obituaries_response['Items'][0]['NextTimer'], '%Y-%m-%d %H:%M:%S.%f')
					print_function("OBITUARIES - GET TIMER AFTER OBITS", str(next_obituaries_timer) + " / " + str(obituaries_locked_until))


				# CITY LIST RECORD
				if city_list_record(lock_webdriver, running_thread, waiting_thread_list, next_citylist_timer, citylist_locked_until, character_name):
					# CITYLIST WAS UPDATED - RECHECK TIMERS
					citylist_response = get_from_database('Timers', 'CityList, NextTimer, LockedUntil')
					citylist_locked_until = datetime.datetime.strptime(citylist_response['Items'][0]['LockedUntil'], '%Y-%m-%d %H:%M:%S.%f')
					next_citylist_timer = datetime.datetime.strptime(citylist_response['Items'][0]['NextTimer'], '%Y-%m-%d %H:%M:%S.%f')
					print_function("CITY LIST - GET TIMER AFTER CITYLIST", str(next_citylist_timer) + " / " + str(citylist_locked_until))



				update_unlocked_aggs(lock_webdriver, running_thread, waiting_thread_list)

				# GYM
				if 'Gym' in globals()['private_businesses_' + current_city]:
					gym(lock_webdriver, running_thread, waiting_thread_list)

				# RESTOCK CHECKS
				weapon_shop(lock_webdriver, running_thread, waiting_thread_list, current_city)
				bionic_shop(lock_webdriver, running_thread, waiting_thread_list, current_city)

				# BLACKMARKET
				if (config.getboolean('Blackmarket-Travel', 'Blackmarket_Gangster_Exp')) and not (config.getboolean('Blackmarket-Travel', 'TradeBlackmarket')):
					if warmode_on:
						pass
					else:
						blackmarket_gangster_exp(lock_webdriver, running_thread, waiting_thread_list, dirty_money, current_city)

				# CAREERS - TRAFFIC TIMER
				if ( ('Mortician' in occupation) or ('Undertaker' in occupation) or ('Funeral' in occupation) ):
					if ('9zSendDrugs' in str(waiting_thread_list)):
						for thread in waiting_thread_list:
							if '9zSendDrugs' in thread:
								thread_split = thread.split('//')
								smuggle_name = thread_split[1]
								mortician_smuggle(lock_webdriver, running_thread, waiting_thread_list, your_character_name, smuggle_name)
								try:
									waiting_thread_list.remove(thread)
								except:
									pass
						waiting_thread_list.sort()

				# CAREERS - CASE TIMER
				if globals()['timers'].__dict__['case_timer'] is None:
					globals()['timers'].__dict__['case_timer'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=get_timer(lock_webdriver, 'Case', running_thread))

				time_difference = datetime.datetime.utcnow() - globals()['timers'].__dict__['case_timer']
				if not '-' in str(time_difference):
					# CASE TIMER READY
					if 'Lawyer' in occupation:
						lawyer(lock_webdriver, running_thread, waiting_thread_list, current_city)
					elif ('Mechanic' in occupation) or ('Technician' in occupation) or ('Engineer' in occupation):
						mechanic(lock_webdriver, running_thread, waiting_thread_list, your_character_name, current_city, aggtarget_person_list_manager)
					elif ('Fire' in occupation):
						globals()['resting_page'] = 'Fire'
						fire_inspection(lock_webdriver, running_thread, waiting_thread_list, your_character_name)
						
					if ( (home_city == current_city) and (current_city != None) ):
						# HOME CITY STUFF
						if ('Police' in occupation):
							police_case(lock_webdriver, running_thread, waiting_thread_list, home_city, character_name)
						elif ('Bank' in occupation) or ('Loan' in occupation):
							bank_career(lock_webdriver, running_thread, waiting_thread_list, home_city)
						elif ('Nurse' in occupation) or ('Doctor' in occupation) or ('Surgeon' in occupation) or ('Hospital Director' in occupation):
							globals()['resting_page'] = 'Hospital'
							hospital(lock_webdriver, running_thread, waiting_thread_list, your_character_name)
						elif ('Judge' in occupation):
							if judge_boys_list is None:
								judge_boys_list = ""
								response = get_from_database('Boys', None)
								for item in response['Items']:
									boys_name = item['PlayerName']
									judge_boys_list = judge_boys_list + boys_name + " "
							else:
								pass
							import multiprocessing
							print_function("JUDGE CITY - CURRENT / HOME " + str(current_city) + ' / ' + str(home_city) + ' | PID: ' + str(multiprocessing.current_process().pid), "GREEN")
							judge(lock_webdriver, running_thread, waiting_thread_list, your_character_name, judge_boys_list)
						elif ('Mortician' in occupation) or ('Undertaker' in occupation) or ('Funeral' in occupation):
							if 'Assistant' in occupation:
								pass
							else:
								mortician_autopsy(lock_webdriver, running_thread, waiting_thread_list)
						elif ('Customs' in occupation):
							customs_blindeye(lock_webdriver, running_thread, waiting_thread_list, your_character_name)


				# NO TIMERS NEEDED
				if ( (home_city == current_city) and (current_city != None) ):
					# HOME CITY STUFF
					if 'Police' in occupation:
						police_911(lock_webdriver, running_thread, waiting_thread_list, home_city, character_name, globals()['All_Boys_List'])

					elif 'Mayor' in occupation:
						mayor_buy(lock_webdriver, running_thread, waiting_thread_list)
					if config['Drugs']['ConsumeCoke']:
						consume_drugs(lock_webdriver, waiting_thread_list, running_thread)
				else:
					# OUTSIDE HOME CITY STUFF
					launder(lock_webdriver, running_thread, waiting_thread_list, dirty_money, globals()['Boys_Launder_List'])


				# CASINO
				if 'Casino' in globals()['private_businesses_' + current_city]:
					casino(lock_webdriver, running_thread, waiting_thread_list)


				# BLACKMARKET & TRAVEL
				# DO BLACKMARKET CALCULATIONS

				# WHAT IF WE MOVE TO A CITY, HAVENT BOUGHT YET AND CANT TRAVEL. IT WOULD LOSE BUY SETTINGS AND SIT ON A PILE OF DIRTY
				# stuff is updated all over the bot once we travel. track last travel the same as last click.
				# variable for blackmarket status
				# avoid closed cities

				# BLACKMARKET & TRAVEL

				# NO CAR CHECK
				if ( ('Vehicle:NONE' in str(running_thread[4])) or ('profile-vehicle:NONE' in str(running_thread[4])) or ("BrokenDownAwaitingRepair" in str(running_thread[4])) ):
					pass
				else:
					if config.getboolean('Blackmarket-Travel', 'TradeBlackmarket'):
						if warmode_on:
							pass
						else:
							if 'BlackMarket' in str(running_thread[3]):
								# need aggpro
								# sell need car repair

								if globals()['timers'].__dict__['blackmarket_timer'] is None:
									globals()['timers'].__dict__['blackmarket_timer'] = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
								time_difference = datetime.datetime.utcnow() - globals()['timers'].__dict__['blackmarket_timer']
								if not '-' in str(time_difference):
									bm_buy_city = None
									bm_sell_city = None
									bm_travel_city = None
									bm_item = None
									bm_status = None
									for item in running_thread[4]:
										if ('blackmarket-buy' in str(item)):
											bm_buy_city = regex_match_between('blackmarket-buy:', None, item)
										elif ('blackmarket-sell' in str(item)):
											bm_sell_city = regex_match_between('blackmarket-sell:', None, item)
										elif ('blackmarket-travel' in str(item)):
											bm_travel_city = regex_match_between('blackmarket-travel:', None, item)
										elif ('blackmarket-item' in str(item)):
											bm_item = regex_match_between('blackmarket-item:', None, item)
										elif ('blackmarket-status' in str(item)):
											bm_status = regex_match_between('blackmarket-status:', None, item)

									# CHECK TRAVEL TIMER
									travel_ready = False
									if globals()['timers'].__dict__['travel_timer'] is None:
										globals()['timers'].__dict__['travel_timer'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=get_timer(lock_webdriver, 'Travel', running_thread))
									time_difference = datetime.datetime.utcnow() - globals()['timers'].__dict__['travel_timer']
									if not '-' in str(time_difference):
										travel_ready = True

									# CHECK TRAFFIC TIMER
									traffic_ready = False
									if globals()['timers'].__dict__['traffic_timer'] is None:
										globals()['timers'].__dict__['traffic_timer'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=get_timer(lock_webdriver, 'Trafficking', running_thread))
									time_difference = datetime.datetime.utcnow() - globals()['timers'].__dict__['traffic_timer']
									if not '-' in str(time_difference):
										traffic_ready = True

									# CHECK CURRENT CITY VARIABLE
									current_city_changed = False
									if 'blackmarket-currentcitysaved' in str(running_thread[4]):
										variables_list = running_thread[4]
										for item in running_thread[4]:
											if 'blackmarket-currentcitysaved:' in str(item):
												current_city_saved = regex_match_between('currentcitysaved:', None, item)
												if str(current_city_saved) != str(current_city):
													current_city_changed = True
									else:
										current_city_changed = True

									# CHECK VEHICLE STATUS
									vehicle_status = None
									for item in running_thread[4]:
										if ('Vehicle:' in str(item)):
											vehicle_status = regex_match_between('Vehicle:', None, item)

									# GET VEHICLE STATUS
									if vehicle_status is None:
										print_function('vehicle status 1 - queued')
										thread_add_to_queue(running_thread, waiting_thread_list, priority_thread_career)
										print_function('vehicle status 1 - running')
										vehicle_get_status(lock_webdriver, running_thread, waiting_thread_list)
										for item in running_thread[4]:
											if ('Vehicle:' in str(item)):
												vehicle_status = regex_match_between('Vehicle:', None, item)
										print_function('vehicle status 1 - finished')
										thread_remove_from_queue(running_thread, waiting_thread_list)

									# GET INITIAL STATUS
									if ((current_city_changed) and (bm_status == 'sold')) or (bm_status is None) or (bm_status == 'UNKNOWN'):
										blackmarket_get_status(lock_webdriver, running_thread, waiting_thread_list,
															   current_city, home_city, dirty_money, bm_buy_city, bm_sell_city)
										bm_buy_city = None
										bm_sell_city = None
										bm_travel_city = None
										bm_item = None
										bm_status = None
										for item in running_thread[4]:
											if ('blackmarket-buy' in str(item)):
												bm_buy_city = regex_match_between('blackmarket-buy:', None, item)
											elif ('blackmarket-sell' in str(item)):
												bm_sell_city = regex_match_between('blackmarket-sell:', None, item)
											elif ('blackmarket-travel' in str(item)):
												bm_travel_city = regex_match_between('blackmarket-travel:', None, item)
											elif ('blackmarket-item' in str(item)):
												bm_item = regex_match_between('blackmarket-item:', None, item)
											elif ('blackmarket-status' in str(item)):
												bm_status = regex_match_between('blackmarket-status:', None, item)

										print_function('BM STATUS: - BUY:' + str(bm_buy_city) + ' SELL:' + str(bm_sell_city) + ' TRAVEL:' +
											  str(bm_travel_city) + ' ITEM:' + str(bm_item) + ' STATUS:' + bm_status)

									# CALCULATE ROUTE
									if ((travel_ready) or (current_city_changed)) and (bm_status == 'sold'):
										blackmarket_calculation(lock_webdriver, running_thread, waiting_thread_list, current_city, home_city, dirty_money)
										# RECHECK VARIABLES AS THEY MAY HAVE CHANGED DURING CALCULATION
										bm_buy_city = None
										bm_sell_city = None
										bm_travel_city = None
										bm_item = None
										bm_status = None
										for item in running_thread[4]:
											if ('blackmarket-buy' in str(item)):
												bm_buy_city = regex_match_between('blackmarket-buy:', None, item)
											elif ('blackmarket-sell' in str(item)):
												bm_sell_city = regex_match_between('blackmarket-sell:', None, item)
											elif ('blackmarket-travel' in str(item)):
												bm_travel_city = regex_match_between('blackmarket-travel:', None, item)
											elif ('blackmarket-item' in str(item)):
												bm_item = regex_match_between('blackmarket-item:', None, item)
											elif ('blackmarket-status' in str(item)):
												bm_status = regex_match_between('blackmarket-status:', None, item)

										# UPDATE CURRENTCITY SAVED
										variables_list = running_thread[4]
										for item in running_thread[4]:
											if 'blackmarket-currentcitysaved:' in str(item):
												try:
													variables_list.remove(item)
												except:
													pass
										variables_list.append('blackmarket-currentcitysaved:' + str(current_city))
										running_thread[4] = variables_list
										print_function('UPDATED VARIABLES AS AFTER CALC ROUTE: ' + str(running_thread[4]))
										write_file("env/variables.txt", running_thread[4])
										print_function('BM CALC - BUY:' + str(bm_buy_city) + ' SELL:' + str(bm_sell_city) + ' TRAVEL:' + str(bm_travel_city) + ' ITEM:' + str(bm_item) + ' STATUS:' + str(bm_status))

									# BUY
									if (traffic_ready) and (bm_buy_city == current_city) and ('buying' in str(bm_status)):
										blackmarket_buy(lock_webdriver, running_thread, waiting_thread_list, current_city, home_city, dirty_money, bm_item, bm_sell_city)
										continue

									# SELL
									if ('selling' in str(bm_status)) and (traffic_ready) and (((bm_sell_city == current_city) and (travel_ready)) or (bm_sell_city != current_city)) :
										# GET AGGPRO FOR SELLING
										if config.getboolean('Blackmarket-Travel', 'NeedAggproToSell'):
											aggpro_seconds = int(get_aggpro_seconds(lock_webdriver))
											if int(aggpro_seconds) > 0:
												aggpro_mins = math.floor(int(aggpro_seconds) / 60)
											else:
												aggpro_mins = 0
										else:
											aggpro_mins = 12

										if int(aggpro_mins) >= 12:
											# CHECK VEHICLE STATUS
											if 'BrokenDownAwaitingRepair' in str(vehicle_status):
												pass
											elif 'WaitingRepair' in str(vehicle_status):
												# CANCEL REPAIR THEN SELL
												if globals()['timers'].__dict__['repair_timer'] is None:
													globals()['timers'].__dict__['repair_timer'] = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
												time_difference = datetime.datetime.utcnow() - globals()['timers'].__dict__['repair_timer']
												if not '-' in str(time_difference):
													vehicle_cancel_repair(lock_webdriver, running_thread, waiting_thread_list)
											elif 'Repaired' in str(vehicle_status):
												blackmarket_sell(lock_webdriver, running_thread, waiting_thread_list, current_city, home_city, dirty_money)
										else:
											time.sleep(10)
										continue

									# TRAVEL
									if (travel_ready) and (bm_travel_city != None) and ((bm_status == 'sold') or (bm_status == 'bought')):
										print_function('TRAVEL - BUY:' + str(bm_buy_city) + ' SELL:' + str(bm_sell_city) + ' TRAVEL:' + str(bm_travel_city) + ' ITEM:' + str(bm_item) + ' STATUS:' + str(bm_status))

										# CHECK VEHICLE STATUS
										if 'BrokenDownAwaitingRepair' in str(vehicle_status):
											pass
										elif 'WaitingRepair' in str(vehicle_status):
											# CANCEL REPAIR THEN SELL
											if globals()['timers'].__dict__['repair_timer'] is None:
												globals()['timers'].__dict__[
													'repair_timer'] = datetime.datetime.utcnow() - datetime.timedelta(
													minutes=30)
											time_difference = datetime.datetime.utcnow() - globals()['timers'].__dict__['repair_timer']
											if not '-' in str(time_difference):
												vehicle_cancel_repair(lock_webdriver, running_thread, waiting_thread_list)
										elif 'Repaired' in str(vehicle_status):
											print_function("TRAVEL TO " + str(bm_travel_city), "GREEN")
											if blackmarket_travel(lock_webdriver, running_thread, waiting_thread_list, bm_travel_city, current_city):

												variables_list = running_thread[4]
												for item in running_thread[4]:
													if ('Vehicle:' in item):
														try:
															variables_list.remove(item)
														except:
															pass
												running_thread[4] = variables_list
												print_function('MISC - TRAVELLED - REMOVED VEHICLE STATUS')
												write_file("env/variables.txt", running_thread[4])

												while True:
													try:
														print_function("RIGHT BAR 3")
														right_bar_details = element_get_attribute(lock_webdriver, 'XPATH',
																								  "/html/body[@id='body']/div[@id='wrapper']/div[@id='nav_right']",
																								  'innerHTML')
														break
													except:
														print_function("MISC - GET RIGHT BAR FAILED", "RED")
														time.sleep(1)
														pass
												right_bar_line = right_bar_details.splitlines()

												your_character_name = regex_match_between('username\=', '">', right_bar_line[4])
												rank = regex_match_between('>', '<', right_bar_line[7])
												if ('<' in str(right_bar_line[11])) and '>' in str(right_bar_line[11]):
													occupation = regex_match_between('>', '<', right_bar_line[11])
												desired_money_on_hand = int(config['Misc']['DesiredMoneyOnHand'])
												your_clean_money = regex_match_between('value="', '"', right_bar_line[15])
												your_clean_money = re.sub('[^0-9]', "", your_clean_money)
												dirty_money = regex_match_between('>', '<', right_bar_line[18])
												dirty_money = re.sub('[^0-9]', "", dirty_money)
												current_city = None
												current_city = regex_match_between('>', '<', right_bar_line[21])
												current_city = current_city.replace(' ', '')
												home_city = None
												home_city = regex_match_between('>', '<', right_bar_line[23])
												home_city = home_city.replace(' ', '')
												print_function("AFTER TRAVEL RESET VARIABLES - CITIES HOME/CURRENT: " + str(home_city) + ' / ' + str(current_city))

												'''
												if (config.getboolean('Misc', 'TravelForCasino')):
													if (gym_ready) or (casino_ready):
														waiting_thread_list.append('9zTravelToHomecity:')
														write_file("env/waiting_thread_list.txt", str(waiting_thread_list))
												'''

												vehicle_get_status(lock_webdriver, running_thread, waiting_thread_list)
												continue
					else:
						# NOT TRADING BLACKMARKET
						variables_list = running_thread[4]
						for item in running_thread[4]:
							if 'blackmarket' in str(item):
								try:
									variables_list.remove(item)
								except:
									pass
						running_thread[4] = variables_list
						write_file("env/variables.txt", running_thread[4])

						# NO BLACKMARKET - TRAVEL FOR GYM / CASINO
						# NOT BLACKMARKET - CHECK TRAVEL TIMER
						travel_ready = False
						if globals()['timers'].__dict__['travel_timer'] is None:
							globals()['timers'].__dict__['travel_timer'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=get_timer(lock_webdriver, 'Travel', running_thread))
						time_difference = datetime.datetime.utcnow() - globals()['timers'].__dict__['travel_timer']
						if not '-' in str(time_difference):
							travel_ready = True


						# NOT BLACKMARKET - CHECK GYM
						gym_ready = False
						if (config.getboolean('Misc', 'TravelForGym')):
							gym_timer = read_file("env/gym_timer.txt")
							try:
								gym_timer = datetime.datetime.strptime(gym_timer, '%Y-%m-%d %H:%M:%S')
							except:
								gym_timer = datetime.datetime.strptime(gym_timer, '%Y-%m-%d %H:%M:%S.%f')
							time_difference = datetime.datetime.utcnow() - gym_timer
							if not '-' in str(time_difference):
								gym_ready = True

						# NOT BLACKMARKET - CHECK CASINO
						casino_ready = False
						if (config.getboolean('Misc', 'TravelForCasino')):
							casino_timer = read_file("env/casino_timer.txt")
							try:
								casino_timer = datetime.datetime.strptime(casino_timer, '%Y-%m-%d %H:%M:%S')
							except:
								casino_timer = datetime.datetime.strptime(casino_timer, '%Y-%m-%d %H:%M:%S.%f')
							time_difference = datetime.datetime.utcnow() - casino_timer
							if not '-' in str(time_difference):
								casino_ready = True

						bm_travel_city = None
						if (travel_ready):
							if (gym_ready):
								for city in globals()['cities_list']:
									if city == current_city:
										pass
									elif 'Gym' in globals()['private_businesses_' + city]:
										if (config.getboolean('Blackmarket-Travel', 'AvoidCitiesWithCases')):
											city_short = globals()[city].city_short_string
											cases_in_city = os.listdir('cases/' + str(city_short))
											cases_in_city = len(cases_in_city)
											if (int(cases_in_city) > 0):
												break
											city_short = globals()[current_city].city_short_string
											cases_in_city = os.listdir('cases/' + str(city_short))
											cases_in_city = len(cases_in_city)
											if (int(cases_in_city) > 0):
												break

										bm_travel_city = city
										break
							elif (casino_ready):
								for city in globals()['cities_list']:
									if city == current_city:
										pass
									elif 'Casino' in globals()['private_businesses_' + city]:
										if (config.getboolean('Blackmarket-Travel', 'AvoidCitiesWithCases')):
											city_short = globals()[city].city_short_string
											cases_in_city = os.listdir('cases/' + str(city_short))
											cases_in_city = len(cases_in_city)
											if (int(cases_in_city) > 0):
												break
											city_short = globals()[current_city].city_short_string
											cases_in_city = os.listdir('cases/' + str(city_short))
											cases_in_city = len(cases_in_city)
											if (int(cases_in_city) > 0):
												break

										bm_travel_city = city
										break
							elif ('TravelToHomecity' in str(waiting_thread_list) ):
								city = home_city
								print_function("TRAVEL TO HOMECITY " + str(city))
								if city == current_city:
									for item in waiting_thread_list:
										if 'TravelToHomecity' in str(item):
											try:
												waiting_thread_list.remove(item)
												print_function('MISC - REMOVED TRAVEL TO HOMECITY AS ALREADY THERE', "GREEN")
												break
											except:
												print_function('MISC - REMOVED TRAVEL TO HOMECITY AS ALREADY THERE - FAILED', "RED")
												pass
								else:
									print_function("TRAVELLING TO HOMECITY " + str(city))
									no_cases_homecity_travel = False
									if (config.getboolean('Blackmarket-Travel', 'AvoidCitiesWithCases')):
										print_function("TRAVELLING TO HOMECITY " + str(city) + " SKIP AS CASES")
										city_short = globals()[city].city_short_string
										cases_in_city = os.listdir('cases/' + str(city_short))
										cases_in_city = len(cases_in_city)
										if (int(cases_in_city) > 0):
											no_cases_homecity_travel = True
										city_short = globals()[current_city].city_short_string
										cases_in_city = os.listdir('cases/' + str(city_short))
										cases_in_city = len(cases_in_city)
										if (int(cases_in_city) > 0):
											no_cases_homecity_travel = True

									if no_cases_homecity_travel:
										pass
									else:
										bm_travel_city = city
										print_function("TRAVEL TO HOMECITY - SET bm_travel_city: " + str(bm_travel_city) )

						if bm_travel_city is None:
							pass
						else:
							# TRAVEL TIME

							# CHECK VEHICLE STATUS
							vehicle_status = None
							for item in running_thread[4]:
								if ('Vehicle:' in str(item)):
									vehicle_status = regex_match_between('Vehicle:', None, item)

							# GET VEHICLE STATUS
							if vehicle_status is None:
								print_function('vehicle status 2 - queued')
								thread_add_to_queue(running_thread, waiting_thread_list, priority_thread_career)
								print_function('vehicle status 2 - running')
								vehicle_get_status(lock_webdriver, running_thread, waiting_thread_list)
								for item in running_thread[4]:
									if ('Vehicle:' in str(item)):
										vehicle_status = regex_match_between('Vehicle:', None, item)
								print_function('vehicle status 2 - finished')
								thread_remove_from_queue(running_thread, waiting_thread_list)

							# TRAVEL IF VEHICLE READY
							if 'BrokenDownAwaitingRepair' in str(vehicle_status):
								pass
							elif 'WaitingRepair' in str(vehicle_status):
								# CANCEL REPAIR THEN SELL
								if globals()['timers'].__dict__['repair_timer'] is None:
									globals()['timers'].__dict__['repair_timer'] = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
								time_difference = datetime.datetime.utcnow() - globals()['timers'].__dict__['repair_timer']
								if not '-' in str(time_difference):
									vehicle_cancel_repair(lock_webdriver, running_thread, waiting_thread_list)
							elif 'Repaired' in str(vehicle_status):
								try:
									if blackmarket_travel(lock_webdriver, running_thread, waiting_thread_list, bm_travel_city, current_city):

										variables_list = running_thread[4]
										for item in running_thread[4]:
											if ('Vehicle:' in item):
												try:
													variables_list.remove(item)
												except:
													pass
										running_thread[4] = variables_list
										print_function('MISC - TRAVELLED - REMOVED VEHICLE STATUS')
										write_file("env/variables.txt", running_thread[4])

										while True:
											try:
												print_function("RIGHT BAR 4")
												right_bar_details = element_get_attribute(lock_webdriver, 'XPATH',
																						  "/html/body[@id='body']/div[@id='wrapper']/div[@id='nav_right']",
																						  'innerHTML')
												break
											except:
												print_function("MISC - GET RIGHT BAR FAILED", "RED")
												time.sleep(1)
												pass
										right_bar_line = right_bar_details.splitlines()

										your_character_name = regex_match_between('username\=', '">', right_bar_line[4])
										rank = regex_match_between('>', '<', right_bar_line[7])
										if ('<' in str(right_bar_line[11])) and '>' in str(right_bar_line[11]):
											occupation = regex_match_between('>', '<', right_bar_line[11])
										desired_money_on_hand = int(config['Misc']['DesiredMoneyOnHand'])
										your_clean_money = regex_match_between('value="', '"', right_bar_line[15])
										your_clean_money = re.sub('[^0-9]', "", your_clean_money)
										dirty_money = regex_match_between('>', '<', right_bar_line[18])
										dirty_money = re.sub('[^0-9]', "", dirty_money)
										current_city = None
										current_city = regex_match_between('>', '<', right_bar_line[21])
										current_city = current_city.replace(' ', '')
										home_city = None
										home_city = regex_match_between('>', '<', right_bar_line[23])
										home_city = home_city.replace(' ', '')
										print_function("AFTER TRAVEL RESET VARIABLES - CITIES HOME/CURRENT: " + str(home_city) + ' / ' + str(current_city))

										if (config.getboolean('Misc', 'TravelForCasino')):
											if (gym_ready) or (casino_ready):
												if 'TravelToHomecity' in str(waiting_thread_list):
													pass
												else:
													waiting_thread_list.append('9zTravelToHomecity:')
													write_file("env/waiting_thread_list.txt", str(waiting_thread_list))

										vehicle_get_status(lock_webdriver, running_thread, waiting_thread_list)
										continue
								except Exception as e:
									if ('EOF' in str(e)):
										pass
									else:
										raise Exception(e)

				# BOYS MECHANIC - THIS IS AFTER TRAVEL SO IT DOESN'T INFINITE LOOP OF CANCEL REPAIR TO TRAVEL, THEN PUT BACK IN FOR BOYS REPAIR
				if not 'Vehicle:FullyRepaired' in str(running_thread[4]):
					boys_work_mechanic(lock_webdriver, running_thread, waiting_thread_list, globals()['Boys_Engineer'], online_list_city, your_character_name)


				# CHANGE RESTING PAGE
				if '999None' in str(running_thread[0]):
					if globals()['timers'].__dict__['case_timer'] is None:
						globals()['timers'].__dict__['case_timer'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=get_timer(lock_webdriver, 'Case', running_thread))
					else:
						time_difference = datetime.datetime.utcnow() - globals()['timers'].__dict__['case_timer']
						if not '-' in str(time_difference):
							case_ready = True
						else:
							case_ready = False

					if globals()['resting_page'] == 'None':
						pass
					elif (globals()['resting_page'] == 'Fire') and (config.getboolean('Career-Fire', 'Do_Cases') and (case_ready)):
						url_check = get_url(lock_webdriver)
						if 'firestation.asp' in url_check:
							pass
						else:
							if globals()['timers'].__dict__['resting_page_timer'] is None:
								globals()['timers'].__dict__['resting_page_timer'] = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
							time_difference_resting = datetime.datetime.utcnow() - globals()['timers'].__dict__['resting_page_timer']
							if globals()['timers'].__dict__['career_timer'] is None:
								globals()['timers'].__dict__['career_timer'] = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
							time_difference_career = datetime.datetime.utcnow() - globals()['timers'].__dict__['career_timer']
							if (not '-' in str(time_difference_resting)) and (not '-' in str(time_difference_career)):
								open_city(lock_webdriver, running_thread)
								element_click(lock_webdriver, "XPATH", ".//*[@class='fire_station']", running_thread)
					elif (globals()['resting_page'] == 'Hospital') and (config.getboolean('Career-Hospital', 'Do_Cases') and (case_ready)):
						url_check = get_url(lock_webdriver)
						if 'hospital.asp' in url_check:
							pass
						else:
							if globals()['timers'].__dict__['resting_page_timer'] is None:
								globals()['timers'].__dict__['resting_page_timer'] = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
							time_difference_resting = datetime.datetime.utcnow() - globals()['timers'].__dict__['resting_page_timer']
							if globals()['timers'].__dict__['career_timer'] is None:
								globals()['timers'].__dict__['career_timer'] = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
							time_difference_career = datetime.datetime.utcnow() - globals()['timers'].__dict__['career_timer']
							if (not '-' in str(time_difference_resting)) and (not '-' in str(time_difference_career)):
								open_city(lock_webdriver, running_thread)

								if element_found(lock_webdriver, "XPATH", ".//*[@class='maintenance']/a[@class='business hospital']"):
									# HOSPITAL TORCHED
									random_timer = random.randrange(20, 30)
									globals()['timers'].__dict__['resting_page_timer'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=random_timer)
								else:
									element_click(lock_webdriver, "XPATH", ".//*[@class='business hospital']", running_thread)

									# HOSPITAL TORCHED
									if element_found(lock_webdriver, "ID", "fail"):
										results = element_get_attribute(lock_webdriver, "ID", "fail", "innerHTML")
										if 'under going repairs' in results:
											print_function('hospital torched')
											random_timer = random.randrange(20, 30)
											globals()['timers'].__dict__['resting_page_timer'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=random_timer)
											globals()['timers'].__dict__['career_timer'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=random_timer)
										else:
											print_function('changed resting page to hospital')

				profile_timer = read_file("env/profile_timer.txt")
				profile_timer = datetime.datetime.strptime(profile_timer, '%Y-%m-%d %H:%M:%S.%f')
				time_difference = datetime.datetime.utcnow() - profile_timer
				if not '-' in str(time_difference):
					profile_check(lock_webdriver, running_thread, waiting_thread_list, None)
			time.sleep(1)
	except:
		from code_modules.function import PrintException
		PrintException()
