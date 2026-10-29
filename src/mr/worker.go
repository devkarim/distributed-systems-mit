package mr

import (
	"encoding/json"
	"errors"
	"fmt"
	"hash/fnv"
	"io"
	"log"
	"net/rpc"
	"os"
	"path/filepath"
	"sort"
	"time"
)

// Map functions return a slice of KeyValue.
type KeyValue struct {
	Key   string
	Value string
}

// use ihash(key) % NReduce to choose the reduce
// task number for each KeyValue emitted by Map.
func ihash(key string) int {
	h := fnv.New32a()
	h.Write([]byte(key))
	return int(h.Sum32() & 0x7fffffff)
}

var coordSockName string // socket for coordinator

// main/mrworker.go calls this function.
func Worker(sockname string, mapf func(string, string) []KeyValue,
	reducef func(string, []string) string) {

	coordSockName = sockname

	ok, reply := CallInitWorker()
	if !ok {
		DPrintf("init worker not ok: %v, exiting...\n", reply)
		return
	}

	workerId := reply.Id

	for {
		ok, reply := CallRequestTask()

		if !ok {
			DPrintf("[%v] Task: not ok: %v, exiting...\n", workerId, reply)
			return
		}

		found := reply.Found
		done := reply.Done

		if done {
			DPrintf("[%v] Worker: all done, exiting...\n", workerId)
			return
		}

		task := reply.Task

		if !found {
			time.Sleep(2 * time.Second)
			continue
		}

		DPrintf("[%v] Task %v: taking task %v\n", workerId, task.Id, task)

		switch task.Type {
		case MAP:
			doMap(task, reply.NReduce, mapf)
		case REDUCE:
			doReduce(task, reducef)
		default:
			DPrintf("[%v] Task %v: received unknown task %v\n", workerId, task.Id, task.Type)
			return
		}

		if ok, _ := CallFinishTask(task.Id); !ok {
			DPrintf("[%v] FinishTask failed for %v\n", workerId, task.Id)
		}
	}
}

func doMap(task *Task, nReduce int, mapf func(string, string) []KeyValue) {
	filename := task.InputFile

	file, err := os.Open(filename)
	if err != nil {
		log.Fatalf("cannot open %v", filename)
	}
	content, err := io.ReadAll(file)
	if err != nil {
		log.Fatalf("cannot read %v", filename)
	}
	file.Close()
	kva := mapf(filename, string(content))

	kvaPerReduce := make([][]KeyValue, nReduce)

	for _, kv := range kva {
		reduceId := ihash(kv.Key) % nReduce
		kvaPerReduce[reduceId] = append(kvaPerReduce[reduceId], kv)
	}

	// write to mr-mapId-reduceId.json
	for reduceId, kva := range kvaPerReduce {
		filename = fmt.Sprintf("mr-%v-%v.json", task.Id, reduceId)
		dir := filepath.Dir(filename)

		tmpFile, err := os.CreateTemp(dir, fmt.Sprintf("%v.tmp", filename))
		if err != nil {
			log.Fatalf("cannot open temp %v: %v", filename, err)
		}
		tmpName := tmpFile.Name()

		err = json.NewEncoder(tmpFile).Encode(kva)
		if err != nil {
			log.Fatalf("couldn't encode to file %v: %v", tmpName, err)
		}

		if err = tmpFile.Sync(); err != nil {
			log.Fatalf("couldn't sync file %v: %v", tmpName, err)
		}

		if err = tmpFile.Close(); err != nil {
			log.Fatalf("couldn't close file %v: %v", tmpName, err)
		}

		// only rename if the file does not exist, maybe another worker has already done this task
		if _, err := os.Stat(filename); errors.Is(err, os.ErrNotExist) {
			err = os.Rename(tmpName, filename)
			if err != nil {
				os.Remove(tmpName)
			}
		} else {
			os.Remove(tmpName)
		}
	}
}

func doReduce(task *Task, reducef func(string, []string) string) {
	pattern := fmt.Sprintf("mr-*-%v.json", task.Id)
	files, err := filepath.Glob(pattern)
	if err != nil {
		log.Fatalf("couldn't glob %v: %v", pattern, err)
	}

	intermediate := []KeyValue{}

	for _, filename := range files {
		file, err := os.Open(filename)
		if err != nil {
			log.Fatalf("couldn't open file %v: %v", filename, err)
		}

		kva := []KeyValue{}
		dec := json.NewDecoder(file)
		for {
			var kv []KeyValue
			if err = dec.Decode(&kv); err != nil {
				break
			}
			kva = append(kva, kv...)
		}

		intermediate = append(intermediate, kva...)
		file.Close()
	}

	sort.Slice(intermediate, func(i, j int) bool {
		return intermediate[i].Key < intermediate[j].Key
	})

	oname := fmt.Sprintf("mr-out-%v", task.Id)
	ofile, err := os.Create(oname)
	if err != nil {
		log.Fatalf("couldn't create file %v: %v", oname, err)
	}

	defer ofile.Close()

	i := 0
	for i < len(intermediate) {
		j := i + 1
		for j < len(intermediate) && intermediate[j].Key == intermediate[i].Key {
			j++
		}
		values := []string{}
		for k := i; k < j; k++ {
			values = append(values, intermediate[k].Value)
		}
		output := reducef(intermediate[i].Key, values)

		// this is the correct format for each line of Reduce output.
		fmt.Fprintf(ofile, "%v %v\n", intermediate[i].Key, output)

		i = j
	}
}

func CallInitWorker() (bool, InitWorkerReply) {
	args := InitWorkerArgs{}

	reply := InitWorkerReply{}

	ok := call("Coordinator.InitWorker", &args, &reply)

	return ok, reply
}

func CallRequestTask() (bool, RequestTaskReply) {
	args := RequestTaskArgs{}

	reply := RequestTaskReply{}

	ok := call("Coordinator.RequestTask", &args, &reply)

	return ok, reply
}

func CallFinishTask(id int) (bool, FinishTaskReply) {
	args := FinishTaskArgs{
		Id: id,
	}

	reply := FinishTaskReply{}

	ok := call("Coordinator.FinishTask", &args, &reply)

	return ok, reply
}

// send an RPC request to the coordinator, wait for the response.
// usually returns true.
// returns false if something goes wrong.
func call(rpcname string, args interface{}, reply interface{}) bool {
	// c, err := rpc.DialHTTP("tcp", "127.0.0.1"+":1234")
	c, err := rpc.DialHTTP("unix", coordSockName)
	if err != nil {
		log.Fatal("dialing:", err)
	}
	defer c.Close()

	if err := c.Call(rpcname, args, reply); err == nil {
		return true
	}
	log.Printf("%d: call failed err %v", os.Getpid(), err)
	return false
}
