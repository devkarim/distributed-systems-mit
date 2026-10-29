cd src/main

# Debug logs on by default for manual runs; unset or MR_DEBUG= to silence.
export MR_DEBUG="${MR_DEBUG:-1}"

go run mrworker.go wc.so sock123
