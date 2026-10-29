package mr

//
// RPC definitions.
//
// remember to capitalize all names.
//

type TaskType string

const (
	MAP    TaskType = "MAP"
	REDUCE TaskType = "REDUCE"
)

type Phase string

const (
	MAP_PHASE    Phase = "MAP"
	REDUCE_PHASE Phase = "REDUCE"
	DONE_PHASE   Phase = "DONE"
)

type Task struct {
	Id        int
	Type      TaskType
	isRunning bool
	finished  bool
	InputFile string
	phase     Phase
}

type InitWorkerArgs struct {
}

type InitWorkerReply struct {
	Id int
}

type RequestTaskArgs struct {
}

type RequestTaskReply struct {
	Found   bool
	Done    bool
	Task    *Task
	NReduce int
}

type FinishTaskArgs struct {
	Id int
}

type FinishTaskReply struct {
}
