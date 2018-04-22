'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Original Author: Minh Ho
Edited by: Joshua Siao
Re-implementation of FCFS and implementation of RR, SRTF and SJF scheduling schemes.

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
from copy import deepcopy

input_file = 'input.txt'

class Process:
    last_burst_prediction = 5
    new_burst_prediction = 0
    last_scheduled_time = 0
    last_burst_time = 0
    waiting_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.remaining_work = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def putToGlobalList(global_list, process):
    for p in global_list:
        if p.id == process.id:
            p.waiting_time += process.waiting_time
            p.last_burst_time = process.burst_time
            return global_list
    Exception()

#Returns task_list
def RR_enqueuework(incoming_tasks, curr_cycle, task_schedule, global_list):
    for p in incoming_tasks:
        if p.arrive_time == curr_cycle and p.remaining_work > 0:
            task_schedule.append(p)
            print('  pid %d has arrived.'%(p.id))
            #Append to the global list if never found before.
            for pp in global_list:
                if pp.id == p.id:
                    return task_schedule #Do nothing but return the task_list.
            global_list.append(deepcopy(p))
    return task_schedule

def SRTF_enqueuework(process_list, curr_cycle, task_list, global_list):
    return RR_enqueuework(process_list, curr_cycle, task_list, global_list)

def SJF_enqueuework(process_list, curr_cycle, task_list, global_list):
    return RR_enqueuework(process_list, curr_cycle, task_list, global_list)

def haswork(process_list):
    for p in process_list:
        if p.remaining_work > 0:
            return True
    return False

#Put the process with the shortest remaining time at the head of the list.
def SRTF_findwork(task_schedule):
    shortest_proc = task_schedule[0]
    for p in task_schedule:
        if(p.remaining_work < shortest_proc.remaining_work):
            shortest_proc = p
    task_schedule.remove(shortest_proc)
    task_schedule.insert(0, shortest_proc)
    return task_schedule

def SJF_findwork(task_schedule, alpha, global_list):
    #Predict the burst in every process
    for p in task_schedule:
        #Find the corresponding pid in global_list and get the last burst time.
        for pp in global_list:
            if p.id == pp.id:
                p.last_burst_time = pp.last_burst_time
        #The formula
        p.new_burst_prediction = alpha * p.last_burst_time + (1.0 - alpha) * p.last_burst_prediction
    #Find the shortest process by looking for the lowest predicted burst
    shortest_proc = task_schedule[0]
    for p in task_schedule:
        if(p.new_burst_prediction < shortest_proc.new_burst_prediction):
            shortest_proc = p
    shortest_proc.last_burst_prediction = shortest_proc.new_burst_prediction
    task_schedule.remove(shortest_proc)
    task_schedule.insert(0, shortest_proc)
    return task_schedule


def FCFS_scheduling(process_list):
    p_list = deepcopy(process_list) #Copy of process_list
    curr_cycle = 0                  #Current 'clock cycle'
    global_list = []                #List of all tasks ever scheduled
    task_list = []                  #Queue of tasks that have arrived have and not yet completed their work.
    schedule = []                   #The output schedule for printing.
    last_task = process_list[0]

    #Check for work
    while(haswork(p_list)):
        print('Cycle %d'%(curr_cycle))
        #Enqueue tasks that have arrived.
        task_list = RR_enqueuework(p_list, curr_cycle, task_list, global_list)
        #If there is nothing to do, go to the next cycle.
        if len(task_list) == 0:
            curr_cycle += 1
            continue
        #Get the task at the head of the list.
        p = task_list[0]
        if p != last_task:
            schedule.append((curr_cycle, p.id));
        last_task = p
        print('Executing pid %d'%(p.id))
        p.remaining_work -= 1
        #For all other tasks in the list, add waiting time.
        for i in range(1, len(task_list)):
            task_list[i].waiting_time += 1
        
        #If the task finished its work, remove it and reset the quantum.
        if p.remaining_work == 0:
            print('  pid %d has finished and is removed.'%(p.id))
            task_list.remove(p)
            global_list = putToGlobalList(global_list, p);
        curr_cycle += 1

    total_waiting_time = 0.0
    for t in global_list:
        total_waiting_time += t.waiting_time;
    avg_waiting_time = total_waiting_time / len(global_list)

    return (schedule, avg_waiting_time)

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    p_list = deepcopy(process_list) #Copy of process_list
    curr_cycle = 0                  #Current 'clock cycle'
    curr_quantum = time_quantum     #The time quantum left in the current cycle.
    global_list = []                #List of all tasks ever scheduled
    task_list = []                  #Queue of tasks that have arrived have and not yet completed their work.
    schedule = []                   #The output schedule for printing.
    last_task = process_list[0]

    #Check for work
    while(haswork(p_list)):
        print('Cycle %d'%(curr_cycle))
        #Enqueue tasks that have arrived.
        task_list = RR_enqueuework(p_list, curr_cycle, task_list, global_list)
        #If there is nothing to do, go to the next cycle.
        if len(task_list) == 0:
            curr_cycle += 1
            curr_quantum = time_quantum
            continue;
        #Get the task at the head of the list.
        p = task_list[0]
        if p != last_task:
            schedule.append((curr_cycle, p.id));
        last_task = p
        print('Executing pid %d'%(p.id))
        p.remaining_work -= 1
        curr_quantum -= 1
        #For all other tasks in the list, add waiting time.
        for i in range(1, len(task_list)):
            task_list[i].waiting_time += 1
        #If the task finished its work, remove it and reset the quantum.
        if p.remaining_work == 0:
            print('  pid %d has finished and is removed.'%(p.id))
            task_list.remove(p)
            global_list = putToGlobalList(global_list, p);
            curr_quantum = time_quantum
        #If the quantum is finished, but the work is not completed, push it to the back.
        elif curr_quantum == 0:
            print('  pid %d has exhausted its quantum and is pushed to the back.'%(p.id))
            task_list.remove(p)
            task_list.append(p)
            curr_quantum = time_quantum
        curr_cycle += 1

    total_waiting_time = 0.0
    for t in global_list:
        total_waiting_time += t.waiting_time;
    avg_waiting_time = total_waiting_time / len(global_list)

    return (schedule, avg_waiting_time)

def SRTF_scheduling(process_list):
    p_list = deepcopy(process_list) #Copy of process_list
    curr_cycle = 0                  #Current 'clock cycle'
    global_list = []                #List of all tasks ever scheduled
    task_list = []                  #Queue of tasks that have arrived have and not yet completed their work.
    schedule = []                   #The output schedule for printing.
    last_task = process_list[0]     

    #Check for work
    while(haswork(p_list)):
        print('Cycle %d'%(curr_cycle))
        #Enqueue tasks that have arrived.
        task_list = SRTF_enqueuework(p_list, curr_cycle, task_list, global_list)
        #If there is nothing to do, go to the next cycle.
        if len(task_list) == 0:
            curr_cycle += 1
            continue;
        #Find the task with the shortest job
        task_list = SRTF_findwork(task_list)
        #Shortest job is now at the front.
        p = task_list[0]
        if p != last_task:
            schedule.append((curr_cycle, p.id));
        last_task = p
        print('Executing pid %d'%(p.id))
        p.remaining_work -= 1
        #For all other tasks in the list, add waiting time.
        for i in range(1, len(task_list)):
            task_list[i].waiting_time += 1
        #If the task finished its work, remove it.
        if p.remaining_work == 0:
            print('  pid %d has finished and is removed.'%(p.id))
            task_list.remove(p)
            global_list = putToGlobalList(global_list, p)
        curr_cycle += 1

    total_waiting_time = 0.0
    for t in global_list:
        total_waiting_time += t.waiting_time;
    avg_waiting_time = total_waiting_time / len(global_list)

    return (schedule, avg_waiting_time)


def SJF_scheduling(process_list, alpha):
    p_list = deepcopy(process_list) #Copy of process_list
    curr_cycle = 0                  #Current 'clock cycle'
    global_list = []                #List of all tasks ever scheduled
    task_list = []                  #Queue of tasks that have arrived have and not yet completed their work.
    schedule = []                   #The output schedule for printing.
    last_task = process_list[0]
    find_new_task = True

    #Check for work
    while(haswork(p_list)):
        print('Cycle %d'%(curr_cycle))
        #Enqueue tasks that have arrived.
        task_list = SJF_enqueuework(p_list, curr_cycle, task_list, global_list)
        #If there is nothing to do, go to the next cycle.
        if len(task_list) == 0:
            curr_cycle += 1
            continue;
        #Find the task with the shortest job
        if find_new_task == True:
            task_list = SJF_findwork(task_list, alpha, global_list)
            find_new_task = False
        #Shortest job is now at the front.
        p = task_list[0]
        if p != last_task:
            schedule.append((curr_cycle, p.id));
        last_task = p
        print('Executing pid %d'%(p.id))
        p.remaining_work -= 1
        #For all other tasks in the list, add waiting time.
        for i in range(1, len(task_list)):
            task_list[i].waiting_time += 1
        #If the task finished its work, remove it.
        if p.remaining_work == 0:
            print('  pid %d has finished and is removed.'%(p.id))
            task_list.remove(p)
            global_list = putToGlobalList(global_list, p)
            find_new_task = True
        curr_cycle += 1

    total_waiting_time = 0.0
    for t in global_list:
        total_waiting_time += t.waiting_time;
    avg_waiting_time = total_waiting_time / len(global_list)

    return (schedule, avg_waiting_time)


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


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

    #Finding optimal RR_time_quantum
    print('Finding Optimal RR Quantum')
    RR_result_list = []
    for tq in range(1, 13):
        RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = tq)
        RR_result_list.append((tq, RR_avg_waiting_time))
    #Finding optimal alpha
    print('Finding Optimal SJF alpha')
    SJF_result_list = []
    testalpha = 0.0
    for i in range (0, 11):
        SJF_schedule, SJF_avg_waiting_time = SJF_scheduling(process_list, testalpha)
        SJF_result_list.append((testalpha, SJF_avg_waiting_time))
        testalpha = testalpha + 0.1
    print('RR Quantum Test Results: time_quantum, avg_waiting_time')
    for r in RR_result_list:
        print(r)
    print('SJF alpha Test Results: alpha, avg_waiting_time')
    for r in SJF_result_list:
        print(r)
if __name__ == '__main__':
    main(sys.argv[1:])
