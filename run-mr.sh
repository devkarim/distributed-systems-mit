cd src/main

# Debug logs on by default for manual runs; unset or MR_DEBUG= to silence.
export MR_DEBUG="${MR_DEBUG:-1}"

# macOS 27+ dyld rejects Go plugins with mismatched chained-fixup seg_count.
# -w strips DWARF so the segment count stays consistent.
if [ "$(uname -s)" = "Darwin" ]; then
	go build -buildmode=plugin -ldflags=-w -o wc.so ../mrapps/wc.go
else
	go build -buildmode=plugin -o wc.so ../mrapps/wc.go
fi

rm -f mr-out* mr-*-*.json mr-*-*.json.tmp*
go run mrcoordinator.go sock123 pg-*.txt
