#!/usr/bin/env python3

import threading
import tkinter as tk
from typing import Dict

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from xarm_msgs.msg import RobotMsg


CONTROLLER_WARN_TEXT = {
	0: 'No warning',
	11: 'UXBUX queue is full',
	12: 'Parameter error',
	13: 'Instruction does not exist',
	14: 'Command has no solution',
	15: 'Modbus command queue full',
}


CONTROLLER_ERROR_TEXT = {
	0: 'No error',
	1: 'Emergency stop button pressed',
	2: 'Control box emergency IO triggered',
	3: 'Three-state switch emergency stop pressed',
	10: 'Servo motor error',
	11: 'Servo motor 1 error',
	12: 'Servo motor 2 error',
	13: 'Servo motor 3 error',
	14: 'Servo motor 4 error',
	15: 'Servo motor 5 error',
	16: 'Servo motor 6 error',
	17: 'Servo motor 7 error',
	18: 'Force torque sensor communication error',
	19: 'End module communication error',
	21: 'Kinematic error',
	22: 'Self-collision error',
	23: 'Joint angle exceeds limit',
	24: 'Speed exceeds limit',
	25: 'Planning error',
	26: 'Linux RT error',
	27: 'Command reply error',
	28: 'End module communication error',
	29: 'Other controller error',
	30: 'Feedback speed exceeds limit',
	31: 'Collision caused abnormal current',
	32: 'Three-point circle calculation error',
	33: 'Controller GPIO error',
	34: 'Recording timeout',
	35: 'Safety boundary limit',
	36: 'Delay command count exceeds limit',
	37: 'Abnormal movement in manual mode',
	38: 'Abnormal joint angle',
	39: 'Master/slave power board communication error',
	40: 'No IK available',
	50: 'Force torque sensor read error',
	51: 'Force torque sensor set mode error',
	52: 'Force torque sensor set zero error',
	53: 'Force torque sensor overload/out of limit',
	110: 'Robot arm base board communication error',
	111: 'Control box external 485 communication error',
}


MODE_TEXT = {
	0: 'Position control mode',
	1: 'Servo motion mode',
	2: 'Joint teaching mode',
	3: 'Cartesian teaching mode (invalid)',
	4: 'Joint velocity control mode',
	5: 'Cartesian velocity control mode',
	6: 'Joint online trajectory planning mode',
	7: 'Cartesian online trajectory planning mode',
}


STATE_TEXT = {
	0: 'Motion state (run)',
	1: 'In motion',
	2: 'Sleeping',
	3: 'Suspended/Pause',
	4: 'Stopping',
	6: 'Deceleration stop',
}


def warn_code_to_text(code: int) -> str:
	return CONTROLLER_WARN_TEXT.get(code, f'Unknown warning code ({code})')


def error_code_to_text(code: int) -> str:
	return CONTROLLER_ERROR_TEXT.get(code, f'Unknown error code ({code})')


def mode_to_text(code: int) -> str:
	return MODE_TEXT.get(code, f'Unknown mode ({code})')


def state_to_text(code: int) -> str:
	return STATE_TEXT.get(code, f'Unknown state ({code})')


class UFMonitorNode(Node):
	def __init__(self, on_robot_state):
		super().__init__('uf_monitor')
		self._on_robot_state = on_robot_state
		self.create_subscription(
			RobotMsg,
			'/xarm/robot_states',
			self._robot_state_callback,
			10,
		)

	def _robot_state_callback(self, msg: RobotMsg):
		self._on_robot_state({
			'state': msg.state,
			'state_text': state_to_text(msg.state),
			'mode': msg.mode,
			'mode_text': mode_to_text(msg.mode),
			'cmdnum': msg.cmdnum,
			'mt_brake': msg.mt_brake,
			'mt_able': msg.mt_able,
			'err': msg.err,
			'warn': msg.warn,
			'err_text': error_code_to_text(msg.err),
			'warn_text': warn_code_to_text(msg.warn),
		})


class UFMonitorGUI:
	def __init__(self):
		self.root = tk.Tk()
		self.root.title('UF Robot State Monitor')
		self.root.geometry('450x140')
		self.root.resizable(False, False)

		self._value_vars: Dict[str, tk.StringVar] = {}
		keys = ('state_text', 'mode_text', 'err_text', 'warn_text')

		for row, key in enumerate(keys):
			tk.Label(self.root, text=f'{key}:', anchor='w', width=10, font=('Arial', 12, 'bold')).grid(
				row=row,
				column=0,
				padx=(12, 4),
				pady=4,
				sticky='w',
			)
			value_var = tk.StringVar(value='-')
			self._value_vars[key] = value_var
			tk.Label(self.root, textvariable=value_var, anchor='w', width=70, font=('Arial', 12)).grid(
				row=row,
				column=1,
				padx=(4, 12),
				pady=4,
				sticky='w',
			)

	def set_values(self, values: Dict[str, int]):
		for key, value in values.items():
			if key in self._value_vars:
				self._value_vars[key].set(str(value))


def main(args=None):
	rclpy.init(args=args)

	latest_values = {
		'state_text': '-',
		'mode_text': '-',
		'err_text': '-',
		'warn_text': '-',
	}
	lock = threading.Lock()

	def on_robot_state(values):
		with lock:
			latest_values.update(values)

	node = UFMonitorNode(on_robot_state)
	executor = SingleThreadedExecutor()
	executor.add_node(node)
	stop_event = threading.Event()

	def spin_ros():
		while rclpy.ok() and not stop_event.is_set():
			executor.spin_once(timeout_sec=0.1)

	spin_thread = threading.Thread(target=spin_ros, daemon=True)
	spin_thread.start()

	gui = UFMonitorGUI()

	def refresh():
		with lock:
			gui.set_values(dict(latest_values))
		if not stop_event.is_set():
			gui.root.after(100, refresh)

	def on_close():
		stop_event.set()
		spin_thread.join(timeout=1.0)
		executor.shutdown()
		node.destroy_node()
		if rclpy.ok():
			rclpy.shutdown()
		gui.root.destroy()

	gui.root.protocol('WM_DELETE_WINDOW', on_close)
	refresh()
	gui.root.mainloop()


if __name__ == '__main__':
	main()
