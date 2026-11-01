package kvsrv

import (
	"log"
	"sync"

	"6.5840/kvsrv1/rpc"
	"6.5840/labrpc"
	"6.5840/tester1"
)

const Debug = false

func DPrintf(format string, a ...interface{}) (n int, err error) {
	if Debug {
		log.Printf(format, a...)
	}
	return
}

type Record struct {
	Value   string
	Version rpc.Tversion
}

type KVMap map[string]Record

type KVServer struct {
	mu    sync.Mutex
	store KVMap
}

func MakeKVServer() *KVServer {
	kv := &KVServer{
		store: make(map[string]Record),
	}

	return kv
}

// Get returns the value and version for args.Key, if args.Key
// exists. Otherwise, Get returns ErrNoKey.
func (kv *KVServer) Get(args *rpc.GetArgs, reply *rpc.GetReply) {
	kv.mu.Lock()
	defer kv.mu.Unlock()

	record, exists := kv.store[args.Key]
	if !exists {
		reply.Err = rpc.ErrNoKey
		return
	}

	reply.Value = record.Value
	reply.Version = record.Version
	reply.Err = rpc.OK
}

// Update the value for a key if args.Version matches the version of
// the key on the server. If versions don't match, return ErrVersion.
// If the key doesn't exist, Put installs the value if the
// args.Version is 0, and returns ErrNoKey otherwise.
func (kv *KVServer) Put(args *rpc.PutArgs, reply *rpc.PutReply) {
	kv.mu.Lock()
	defer kv.mu.Unlock()

	record, exists := kv.store[args.Key]
	if !exists && args.Version != 0 {
		reply.Err = rpc.ErrNoKey
		return
	}

	if !exists {
		record = Record{Value: args.Value, Version: args.Version}
	}

	if record.Version != args.Version {
		reply.Err = rpc.ErrVersion
		return
	}

	record.Value = args.Value
	record.Version += 1

	kv.store[args.Key] = record
	reply.Err = rpc.OK
}

// You can ignore all arguments; they are for replicated KVservers
func StartKVServer(tc *tester.TesterClnt, ends []*labrpc.ClientEnd, gid tester.Tgid, srv int, persister *tester.Persister) []any {
	kv := MakeKVServer()
	return []any{kv}
}
