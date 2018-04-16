'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum):
	#some protection from negative value
	if(time_quantum < 0):
		time_quantum = 2
	schedule = []
	current_time = 0
	waiting_time = 0
	completed_process = 0
	total_process = len(process_list)
	while completed_process < total_process:
		#print("Completed %d current_time %d" %(completed_process, current_time))
		for process in process_list:
			timeUpdated = 0
			#print("current_process id %d\n" %process.id) 
			if((current_time >= process.arrive_time) and (process.burst_time > 0)):
				#print("current_time %d\n" %current_time)
				if(process.burst_time > 0):
					schedule.append((current_time, process.id))
					process.burst_time = process.burst_time - time_quantum
				if(process.burst_time == 0):
					completed_process = completed_process + 1
					waiting_time = waiting_time + current_time - process.arrive_time
					current_time = current_time + time_quantum
					timeUpdated = 1
				elif(process.burst_time < 0):
					completed_process = completed_process + 1
					waiting_time = waiting_time + current_time - process.arrive_time
					current_time = current_time + process.burst_time + time_quantum
					timeUpdated = 1
				else:
					current_time = current_time + time_quantum
					timeUpdated = 1
			elif(current_time < process.arrive_time):
				#print("no more process, trying to loop back")
				if(timeUpdated == 0):
					#print("no process run, time need to update\n");
					current_time = process.arrive_time	 
				break

	average_waiting_time = waiting_time/float(len(process_list))	    
    
	return schedule, average_waiting_time

#Input: process_list
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def SRTF_scheduling(process_list):
	schedule = []
	current_time = 0
	waiting_time = 0
	completed_process = 0
	total_process = len(process_list)
					
	while completed_process < total_process:
		min_burst_time = -1
		process_location = 0
		for position, process in enumerate(process_list):
			if((current_time >= process.arrive_time) and (process.burst_time > 0)):
				if(min_burst_time < 0):
					min_burst_time = process.burst_time
					process_location = position
				elif(process.burst_time < min_burst_time):
					min_burst_time = process.burst_time
					process_location = position
		
		#get the minimum time, so this is the process to be run
		process_list[process_location].burst_time = process_list[process_location].burst_time - 1
		
		schedule.append((current_time, process_list[process_location].id))
		
		#if complete the process, then can get the waiting time for it
		if(process_list[process_location].burst_time == 0):
			waiting_time = waiting_time + current_time - process_list[process_location].arrive_time	
			completed_process = completed_process + 1
				
		current_time = current_time + 1

	#create a new schedule
	schedule_len = len(schedule)
	newschedule = []
	newschedule.append((schedule[0]))
	i = 1
	while i < schedule_len: 
#		print(i)
		for j in xrange(i, schedule_len):
			#if not same, then only add into new schedule
			if(schedule[i][1] != schedule[j][1]):
				newschedule.append((schedule[j]))
				i = j
				break
			elif(j == schedule_len-1):
				i = j+1
				break
												
	average_waiting_time = waiting_time/float(len(process_list))	    
    
	return newschedule, average_waiting_time

# time prediction function
# last_actual is the burst_time of the process, ie the real time used
# last_prediction is the guess of the process
def time_prediction(last_actual_list, last_prediction_list, pid, alpha):
	prediction = 0
	last_actual = 0
	last_prediction = 0
	
	#get the last_actual
	for i in last_actual_list:
		if(i[0] == pid):
			last_actual = i[1]		
			break
	
	#get the last_prediction
	for i in last_prediction_list:
		if(i[0] == pid):
			last_prediction = i[1]		
			break
	
	if(last_prediction == 0):
		prediction = 5 #init guess
	else:
		one_minus_alpha = 1 - alpha
		prediction = (alpha * last_actual) + (one_minus_alpha * last_prediction) 	
	return prediction

#Input: process_list, alpha (Positive value)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def SJF_scheduling(process_list, alpha):
	#some protection from negative alpha
	if(alpha < 0):
		alpha = -alpha
	#generate the process list, assuming the process id can be anything but we just want every unique id
	processActualRunTime = []
	processPredictedRunTime = []
	
	output = set()
	for process in process_list:
		output.add(process.id)
	
	for pid in output:
			t = (pid, 0)
			processActualRunTime.append(list(t))		#actual time need to be updated
			processPredictedRunTime.append(list(t))	#later will predict the time to 5 if at first is 0, meaning init time	
	
	schedule = []
	current_time = 0
	waiting_time = 0
	completed_process = 0
	total_process = len(process_list)
	
	#location in the process_list
	process_location = 0		

	while completed_process < total_process:
		min_prediction_time = 0
		min_position = 0
		process_cleared = 0
		for position, process in enumerate(process_list):
			if((current_time >= process.arrive_time) and (process.burst_time > 0)):
				#check who has the minimum job time	
				prediction = time_prediction(processActualRunTime, processPredictedRunTime, process.id, alpha)
				if(min_prediction_time == 0):
					#print("1. current time %d, prediction %d, process.id %d, position %d, process_list[position].id %d\n" %(current_time, prediction, process.id, position, process_list[position].id))
					min_prediction_time = prediction
					min_position = position
				elif(min_prediction_time > prediction):
					#print("2. current time %d, prediction %d, process.id %d, position %d, process_list[position].id %d\n" %(current_time, prediction, process.id, position, process_list[position].id))
					min_prediction_time = prediction
					min_position = position
				process_cleared = 1
			elif(current_time < process.arrive_time):
				#print("3. current time %d, prediction %d, process.id %d, position %d, process_list[position].id %d, arrive_time %d\n" %(current_time, prediction, process.id, position, process_list[position].id, process.arrive_time))
				#print("no process to run, break\n")
				break;

		if(process_cleared == 1):
			#we have the least time process, run it till completed
			schedule.append((current_time, process_list[min_position].id))
	
			#update the prediction to latest prediction
			for i in processPredictedRunTime:
				#print("i[0] %d and process_list[min_position].id %d" %(i[0], process_list[min_position].id))
				if(i[0] == process_list[min_position].id):
					#print("position is %d\n" %i[0])
					i[1] = min_prediction_time
					break
			#print(processPredictedRunTime)
				
			#update the actual time to burst time used
			for i in processActualRunTime:
				if(i[0] == process_list[min_position].id):
					i[1] = process_list[min_position].burst_time
					break
			#print(processActualRunTime)

			#make burst time to zero since completed it/ non preemptive
			completed_process = completed_process + 1
			waiting_time = waiting_time + current_time - process_list[min_position].arrive_time
			current_time = current_time + process_list[min_position].burst_time
			process_list[min_position].burst_time = 0
		else:
			#print("No process run, so move to the next arriving time\n");
			for proces in process_list:
				if(process.arrive_time > current_time):
					current_time = process.arrive_time 
					break
		
	average_waiting_time = waiting_time/float(len(process_list))	    
    
	return schedule, average_waiting_time

def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def T1():
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    
    process_list = read_input()
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 100)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    
    process_list = read_input()
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    
    process_list = read_input()
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

def T2():
	rr_average = []
	sjf_average = []
	
	for i in xrange(1,100):
		my_quantum =  i
		process_list = read_input()
		RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list, time_quantum = my_quantum)
		rr_average.append((my_quantum, RR_avg_waiting_time))
	
	print("RR_schedule\n")
	minimum_rr = 0.0
	quantum_rr = 0
	for s in rr_average:
		print("time quantum: %d, average_waiting_time: %f\n" %(s[0], s[1]))
		if(minimum_rr == 0):
			minimum_rr = s[1]
			quantum_rr = s[0]
		elif(minimum_rr > s[1]):
			minimum_rr = s[1]
			quantum_rr = s[0]
			
	print("Minimum average waiting time for RR: %f, at time quantum: %d\n" %(minimum_rr, quantum_rr)) 

	for i in xrange(0,11):
		my_alpha =  i/10.0
		process_list = read_input()
		SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = my_alpha)
		sjf_average.append((my_alpha, SJF_avg_waiting_time))
	
	print("SJF_schedule\n")
	minimum_sjf = 0.0
	alpha_sjf = 0.0
	for s in sjf_average:
		print("alpha: %.1f, average_waiting_time: %f\n" %(s[0], s[1]))
		if(minimum_sjf == 0):
			minimum_sjf = s[1]
			alpha_sjf = s[0]
		elif(minimum_sjf > s[1]):
			minimum_sjf = s[1]
			alpha_sjf = s[0]

	print("Minimum average waiting time for SJF: %f, at alpha: %.1f\n" %(minimum_sjf, alpha_sjf)) 

def main(argv):
	T1()
#	T2()

if __name__ == '__main__':
    main(sys.argv[1:])
