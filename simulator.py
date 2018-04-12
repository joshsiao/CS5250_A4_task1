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
from copy import deepcopy

input_file = 'input.txt'

class Process:
    last_burst_prediction = 5
    last_scheduled_time = 0
    remaining_work = 0
    waiting_time = 0
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

def RR_init(process_list):
    for p in process_list:
        p.remaining_work = p.burst_time

def SRTF_init(process_list):
    RR_init(process_list)

def SJF_init(process_list):
    RR_init(process_list)

def RR_enqueuework(process_list, curr_cycle, task_list):
    for p in process_list:
        if p.arrive_time == curr_cycle and p.remaining_work > 0:
            task_list.append(p)
            print('Enqueued pid %d'%(p.id))
    return task_list

def SRTF_enqueuework(process_list, curr_cycle, task_list):
    return RR_enqueuework(process_list, curr_cycle, task_list)

def SJF_enqueuework(process_list, curr_cycle, task_list):
    return RR_enqueuework(process_list, curr_cycle, task_list)

def RR_haswork(process_list):
    for p in process_list:
        if p.remaining_work > 0:
            return True
    return False

def SRTF_haswork(process_list):
    return RR_haswork(process_list)

def SJF_haswork(process_list):
    return RR_haswork(process_list)

def SRTF_findwork(process_list):
    shortest_proc = process_list[0]
    for p in process_list:
        if(p.remaining_work < shortest_proc.remaining_work):
            shortest_proc = p
    process_list.remove(shortest_proc)
    process_list.insert(0, shortest_proc)
    return process_list

def SJF_findwork(process_list, alpha):
    #Predict the burst in every process
    for p in process_list:
        new_prediction = alpha * p.burst_time + (1 - alpha) * p.last_burst_prediction
        p.last_burst_prediction = new_prediction
    #Find the shortest process by looking for the lowest predicted burst
    shortest_proc = process_list[0]
    for p in process_list:
        if(p.last_burst_prediction < shortest_proc.last_burst_prediction):
            shortest_proc = p
    process_list.remove(shortest_proc)
    process_list.insert(0, shortest_proc)
    return process_list

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    p_list = deepcopy(process_list)
    RR_init(p_list)
    curr_cycle = 0
    curr_quantum = time_quantum
    task_list = []
    finished_tasks = []
    schedule = []
    last_task = process_list[0]

    #Check for work
    while(RR_haswork(p_list)):
        print('Cycle %d'%(curr_cycle))
        #Enqueue tasks that have arrived.
        task_list = RR_enqueuework(p_list, curr_cycle, task_list)
        #If there is nothing to do, go to the next cycle.
        if task_list.count == 0:
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
            print('  PID %d has finished and is removed.'%(p.id))
            task_list.remove(p)
            finished_tasks.append(p)
            curr_quantum = time_quantum
        #If the quantum is finished, but the work is not completed, push it to the back.
        elif curr_quantum == 0:
            print('  PID %d has exhausted its quantum and is pushed to the back.'%(p.id))
            task_list.remove(p)
            task_list.append(p)
            curr_quantum = time_quantum
        curr_cycle += 1

    total_waiting_time = 0.0
    for t in finished_tasks:
        total_waiting_time += t.waiting_time;
    avg_waiting_time = total_waiting_time / len(finished_tasks)

    return (schedule, avg_waiting_time)

def SRTF_scheduling(process_list):
    p_list = deepcopy(process_list)
    SRTF_init(p_list)
    curr_cycle = 0
    task_list = []
    finished_tasks = []
    schedule = []
    last_task = process_list[0]

    #Check for work
    while(SRTF_haswork(p_list)):
        print('Cycle %d'%(curr_cycle))
        #Enqueue tasks that have arrived.
        task_list = SRTF_enqueuework(p_list, curr_cycle, task_list)
        #If there is nothing to do, go to the next cycle.
        if task_list.count == 0:
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
            print('  PID %d has finished and is removed.'%(p.id))
            task_list.remove(p)
            finished_tasks.append(p)
        curr_cycle += 1

    total_waiting_time = 0.0
    for t in finished_tasks:
        total_waiting_time += t.waiting_time;
    avg_waiting_time = total_waiting_time / len(finished_tasks)

    return (schedule, avg_waiting_time)


def SJF_scheduling(process_list, alpha):
    p_list = deepcopy(process_list)
    SJF_init(p_list)
    curr_cycle = 0
    task_list = []
    finished_tasks = []
    schedule = []
    last_task = process_list[0]
    last_prediction = 5
    find_new_task = True

    #Check for work
    while(SJF_haswork(p_list)):
        print('Cycle %d'%(curr_cycle))
        #Enqueue tasks that have arrived.
        task_list = SJF_enqueuework(p_list, curr_cycle, task_list)
        #If there is nothing to do, go to the next cycle.
        if task_list.count == 0:
            curr_cycle += 1
            continue;
        #Find the task with the shortest job
        if find_new_task == True:
            task_list = SJF_findwork(task_list, alpha)
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
            print('  PID %d has finished and is removed.'%(p.id))
            task_list.remove(p)
            finished_tasks.append(p)
            find_new_task = True
        curr_cycle += 1

    total_waiting_time = 0.0
    for t in finished_tasks:
        total_waiting_time += t.waiting_time;
    avg_waiting_time = total_waiting_time / len(finished_tasks)

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

if __name__ == '__main__':
    main(sys.argv[1:])