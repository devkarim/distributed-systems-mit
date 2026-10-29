package mr

import (
	"fmt"
	"os"
)

var debugEnabled = os.Getenv("MR_DEBUG") != ""

// DPrintf prints only when MR_DEBUG is set (e.g. MR_DEBUG=1).
func DPrintf(format string, a ...interface{}) {
	if debugEnabled {
		fmt.Printf(format, a...)
	}
}
