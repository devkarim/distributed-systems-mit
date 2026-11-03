package lock

import (
	"time"

	"6.5840/kvsrv1/rpc"
	"6.5840/kvtest1"
)

type Lock struct {
	// IKVClerk is a go interface for k/v clerks: the interface hides
	// the specific Clerk type of ck but promises that ck supports
	// Put and Get.  The tester passes the clerk in when calling
	// MakeLock().
	ck       kvtest.IKVClerk
	lockname string
	clientId string
}

const sleepTime = time.Millisecond * 100

// The tester calls MakeLock() and passes in a k/v clerk; your code can
// perform a Put or Get by calling lk.ck.Put() or lk.ck.Get().
//
// This interface supports multiple locks by means of the
// lockname argument; locks with different names should be
// independent.
func MakeLock(ck kvtest.IKVClerk, lockname string) *Lock {
	lk := &Lock{ck: ck, lockname: lockname, clientId: kvtest.RandValue(8)}
	return lk
}

func (lk *Lock) Acquire() {
	for {
		value, version, _ := lk.ck.Get(lk.lockname)
		// already acquired by me
		if value == lk.clientId {
			return
		}
		// acquired by someone else
		if value != "" {
			time.Sleep(sleepTime)
			continue
		}
		// free (missing or empty): try to claim
		if lk.ck.Put(lk.lockname, lk.clientId, version) == rpc.OK {
			return
		}
		time.Sleep(sleepTime)
	}
}

func (lk *Lock) Release() {
	for {
		value, version, err := lk.ck.Get(lk.lockname)
		if err != rpc.OK || value != lk.clientId {
			return
		}
		if lk.ck.Put(lk.lockname, "", version) == rpc.OK {
			return
		}
		time.Sleep(sleepTime)
	}
}
