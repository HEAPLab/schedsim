# CSV File description
Each line of the CSV file represents an event and it is composed of 6 fields:
`timestamp,task,job,processor,type_of_event,extra_data`
where:
 - **timestamp** [integer or float]: the elapsed time since the epoch of measurements (usually 0). 
                                     This can be measured in different time units (e.g. seconds,
                                     milliseconds, clock cycles, etc.). This may not be unique in
                                     the file, multiple events may happen at the same time.
 - **task** [integer]: the task id. If the event refers to a processor-only event, this value is 0.
 - **job** [integer]: the job id. If the event refers to a processor-only event, this value is 0.
 - **processor** [integer]: the processor id where the event happened. If the event is not
                            processor-related, this value is 0.
 - **type_of_event** [enum/char]: the identificator for the event (see later)
 - **extra_data** [integer]: additional data depending on the event type, this value is 0 if not
                             used.

#### Events
Possible events for tasks/jobs:
 - `A`: activation of a job (processor-independent)
 - `D`: deadline of a job (processor-independent)
 - `W`: theoretical worst-case finish time for the job (`A` + WCET) (it may differ depending on the
        processor)
 - `S`: actual start of a job
 - `F`: actual finish of a job

Possible processor-only events:
 - `+`: processor goes online
 - `-`: processor goes offline
 - `F`: frequency change (`extra_data` contains the new frequency in MHz)

#### Example
```
 0,1,1,0,A,0  # t=0 Task 1 Job 1 activates
 0,2,1,0,A,0  # t=0 Task 2 Job 1 activates
 0,1,1,1,S,0  # t=0 Task 1 Job 1 starts on processor 1
 0,2,1,2,S,0  # t=0 Task 2 Job 1 starts on processor 2
 3,2,1,2,F,0  # t=3 Task 2 Job 1 finishes
 5,2,1,0,D,0  # t=5 Task 2 Job 1 deadline
 5,2,2,0,A,0  # t=5 Task 2 Job 2 activates
 5,2,2,2,S,0  # t=5 Task 2 Job 2 starts on processor 2
 8,1,1,1,F,0  # t=8 Task 1 Job 1 finishes
 9,2,2,2,F,0  # t=9 Task 2 Job 2 finishes
 10,2,2,0,D,0  # t=10 Task 2 Job 2 deadline
 15,1,1,0,D,0  # t=15 Task 1 Job 1 deadline
```
 
