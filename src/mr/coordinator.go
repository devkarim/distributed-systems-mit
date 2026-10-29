package mr

import (
	"log"
	"net"
	"net/http"
	"net/rpc"
	"os"
	"sync"
	"time"
)

const TIMEOUT = 10 * time.Second

type Coordinator struct {
	nReduce      int
	tasks        []*Task
	mutex        sync.RWMutex
	phase        Phase
	numOfWorkers int
}

func (c *Coordinator) InitWorker(args *InitWorkerArgs, reply *InitWorkerReply) error {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	reply.Id = c.numOfWorkers
	c.numOfWorkers += 1

	return nil
}

func (c *Coordinator) RequestTask(args *RequestTaskArgs, reply *RequestTaskReply) error {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	found, task := c.getTask()

	if !found {
		reply.Found = false
		reply.Done = c.phase == DONE_PHASE
		return nil
	}

	reply.Found = true
	reply.Task = task
	reply.NReduce = c.nReduce

	task.isRunning = true

	time.AfterFunc(TIMEOUT, func() {
		c.mutex.Lock()
		defer c.mutex.Unlock()

		if !task.finished {
			task.isRunning = false
		}
	})

	return nil
}

func (c *Coordinator) FinishTask(args *FinishTaskArgs, reply *FinishTaskReply) error {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	if args.Id < 0 || args.Id >= len(c.tasks) {
		return nil
	}

	task := c.tasks[args.Id]

	if task.finished || task.phase != c.phase {
		return nil
	}

	task.isRunning = false
	task.finished = true

	DPrintf("Task %v: finished\n", task.Id)
	if !c.isPhaseRunning() {
		c.moveToNextPhase()
		DPrintf("Coordinator moving to next phase: %v\n", c.phase)
	}

	return nil
}

func (c *Coordinator) moveToNextPhase() {
	switch c.phase {
	case MAP_PHASE:
		c.phase = REDUCE_PHASE
		c.generateReduceTasks()
	case REDUCE_PHASE:
		c.phase = DONE_PHASE
	default:
		DPrintf("coordinator unknown move from: %v", c.phase)
	}
}

func (c *Coordinator) generateReduceTasks() {
	tasks := make([]*Task, c.nReduce)
	for i := range tasks {
		tasks[i] = &Task{
			Id:        i,
			Type:      REDUCE,
			isRunning: false,
			finished:  false,
			phase:     REDUCE_PHASE,
		}
	}
	c.tasks = tasks
}

func (c *Coordinator) getTask() (bool, *Task) {
	for _, t := range c.tasks {
		if !t.isRunning && !t.finished {
			return true, t
		}
	}
	return false, nil
}

func (c *Coordinator) isPhaseRunning() bool {
	for _, t := range c.tasks {
		if !t.finished {
			return true
		}
	}
	return false
}

// start a thread that listens for RPCs from worker.go
func (c *Coordinator) server(sockname string) {
	rpc.Register(c)
	rpc.HandleHTTP()
	os.Remove(sockname)
	l, e := net.Listen("unix", sockname)
	if e != nil {
		log.Fatalf("listen error %s: %v", sockname, e)
	}
	go http.Serve(l, nil)
}

// main/mrcoordinator.go calls Done() periodically to find out
// if the entire job has finished.
func (c *Coordinator) Done() bool {
	c.mutex.RLock()
	defer c.mutex.RUnlock()

	return c.phase == DONE_PHASE
}

// create a Coordinator.
// main/mrcoordinator.go calls this function.
// nReduce is the number of reduce tasks to use.
func MakeCoordinator(sockname string, files []string, nReduce int) *Coordinator {
	c := Coordinator{
		nReduce: nReduce,
		tasks:   make([]*Task, len(files), len(files)+nReduce),
		phase:   MAP_PHASE,
	}

	// generate map tasks for each file input
	for idx, filePath := range files {
		c.tasks[idx] = &Task{
			Id:        idx,
			Type:      MAP,
			isRunning: false,
			finished:  false,
			InputFile: filePath,
			phase:     MAP_PHASE,
		}
	}

	c.server(sockname)
	return &c
}
