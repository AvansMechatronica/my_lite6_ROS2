#!/usr/bin/env python3

import threading
import tkinter as tk
from tkinter import ttk

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from xarm_msgs.srv import Call
from xarm_msgs.srv import SetInt16


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
	1: 'In motion (reported state)',
	2: 'Sleeping (reported state)',
	3: 'Pause state',
	4: 'Stop state',
	6: 'Deceleration stop state',
}


def mode_to_text(value: int) -> str:
	return MODE_TEXT.get(value, f'Unknown mode ({value})')


def state_to_text(value: int) -> str:
	return STATE_TEXT.get(value, f'Unknown state ({value})')


class UFControlNode(Node):
	def __init__(self, set_status):
		super().__init__('uf_control')
		self._set_status = set_status
		self._clean_error_client = self.create_client(Call, '/xarm/clean_error')
		self._clean_warn_client = self.create_client(Call, '/xarm/clean_warn')
		self._set_mode_client = self.create_client(SetInt16, '/xarm/set_mode')
		self._set_state_client = self.create_client(SetInt16, '/xarm/set_state')

	def call_clean_error(self):
		self._call_service(self._clean_error_client, '/xarm/clean_error')

	def call_clean_warn(self):
		self._call_service(self._clean_warn_client, '/xarm/clean_warn')

	def call_set_mode(self, value: int):
		self._call_set_int16_service(self._set_mode_client, '/xarm/set_mode', value, mode_to_text(value))

	def call_set_state(self, value: int):
		self._call_set_int16_service(self._set_state_client, '/xarm/set_state', value, state_to_text(value))

	def _call_service(self, client, service_name: str):
		if not client.wait_for_service(timeout_sec=0.3):
			self._set_status(f'Service unavailable: {service_name}')
			return

		request = Call.Request()
		future = client.call_async(request)
		self._set_status(f'Calling {service_name} ...')

		def _done(fut):
			try:
				response = fut.result()
				if response is None:
					self._set_status(f'{service_name} failed: empty response')
					return
				if response.ret == 0:
					self._set_status(f'{service_name} OK (ret=0)')
				else:
					self._set_status(f'{service_name} returned ret={response.ret}, message={response.message}')
			except Exception as exc:
				self._set_status(f'{service_name} failed: {exc}')

		future.add_done_callback(_done)

	def _call_set_int16_service(self, client, service_name: str, value: int, value_text: str):
		if not client.wait_for_service(timeout_sec=0.3):
			self._set_status(f'Service unavailable: {service_name}')
			return

		request = SetInt16.Request()
		request.data = int(value)
		future = client.call_async(request)
		self._set_status(f'Calling {service_name} with data={value} ({value_text}) ...')

		def _done(fut):
			try:
				response = fut.result()
				if response is None:
					self._set_status(f'{service_name} failed: empty response')
					return
				if response.ret == 0:
					self._set_status(f'{service_name} OK (ret=0, data={value}, {value_text})')
				else:
					self._set_status(f'{service_name} returned ret={response.ret}, message={response.message}')
			except Exception as exc:
				self._set_status(f'{service_name} failed: {exc}')

		future.add_done_callback(_done)


class UFControlGUI:
	def __init__(self, on_clean_error, on_clean_warn, on_set_mode, on_set_state):
		self.root = tk.Tk()
		self.root.title('UF xArm Service Control')
		self.root.geometry('520x280')
		self.root.resizable(False, False)

		tk.Label(
			self.root,
			text='xArm API Services',
			font=('Arial', 14, 'bold'),
		).pack(pady=(10, 6))

		button_frame = tk.Frame(self.root)
		button_frame.pack(pady=8)

		tk.Button(
			button_frame,
			text='Clean Error',
			width=18,
			command=on_clean_error,
		).grid(row=0, column=0, padx=8)

		tk.Button(
			button_frame,
			text='Clean Warn',
			width=18,
			command=on_clean_warn,
		).grid(row=0, column=1, padx=8)

		mode_state_frame = tk.Frame(self.root)
		mode_state_frame.pack(pady=(6, 8), fill='x', padx=12)

		self._mode_options = self._build_options(MODE_TEXT)
		self._state_options = self._build_options(STATE_TEXT)

		tk.Label(mode_state_frame, text='Mode:', font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w')
		self._mode_var = tk.StringVar(value=self._mode_options[0])
		self._mode_combo = ttk.Combobox(
			mode_state_frame,
			textvariable=self._mode_var,
			values=self._mode_options,
			state='readonly',
			width=34,
		)
		self._mode_combo.grid(row=0, column=1, padx=(6, 10), sticky='w')
		tk.Button(
			mode_state_frame,
			text='Set Mode',
			width=14,
			command=lambda: self._try_call_selected(self._mode_var, 'mode', on_set_mode),
		).grid(row=0, column=2, sticky='w')

		tk.Label(mode_state_frame, text='State:', font=('Arial', 11, 'bold')).grid(row=1, column=0, pady=(8, 0), sticky='w')
		self._state_var = tk.StringVar(value=self._state_options[0])
		self._state_combo = ttk.Combobox(
			mode_state_frame,
			textvariable=self._state_var,
			values=self._state_options,
			state='readonly',
			width=34,
		)
		self._state_combo.grid(row=1, column=1, padx=(6, 10), pady=(8, 0), sticky='w')
		tk.Button(
			mode_state_frame,
			text='Set State',
			width=14,
			command=lambda: self._try_call_selected(self._state_var, 'state', on_set_state),
		).grid(row=1, column=2, pady=(8, 0), sticky='w')

		self._status_var = tk.StringVar(value='Ready')
		tk.Label(
			self.root,
			text='Status:',
			font=('Arial', 11, 'bold'),
		).pack(anchor='w', padx=12)
		tk.Label(
			self.root,
			textvariable=self._status_var,
			wraplength=400,
			justify='left',
			font=('Arial', 11),
		).pack(anchor='w', padx=12, pady=(2, 0))

	def set_status(self, text: str):
		self._status_var.set(text)

	def _build_options(self, data):
		return [f'{k} - {v}' for k, v in sorted(data.items(), key=lambda item: item[0])]

	def _parse_selected_value(self, selected: str):
		return int(selected.split(' - ', 1)[0])

	def _try_call_selected(self, value_var: tk.StringVar, label: str, callback):
		try:
			value = self._parse_selected_value(value_var.get().strip())
		except ValueError:
			self.set_status(f'Invalid {label}: select from pull-down')
			return
		callback(value)


def main(args=None):
	rclpy.init(args=args)

	status_lock = threading.Lock()
	status_text = {'value': 'Ready'}

	def set_status(text: str):
		with status_lock:
			status_text['value'] = text

	node = UFControlNode(set_status)
	executor = SingleThreadedExecutor()
	executor.add_node(node)
	stop_event = threading.Event()

	def spin_ros():
		while rclpy.ok() and not stop_event.is_set():
			executor.spin_once(timeout_sec=0.1)

	spin_thread = threading.Thread(target=spin_ros, daemon=True)
	spin_thread.start()

	gui = UFControlGUI(
		on_clean_error=node.call_clean_error,
		on_clean_warn=node.call_clean_warn,
		on_set_mode=node.call_set_mode,
		on_set_state=node.call_set_state,
	)

	def refresh_status():
		with status_lock:
			gui.set_status(status_text['value'])
		if not stop_event.is_set():
			gui.root.after(100, refresh_status)

	def on_close():
		stop_event.set()
		spin_thread.join(timeout=1.0)
		executor.shutdown()
		node.destroy_node()
		if rclpy.ok():
			rclpy.shutdown()
		gui.root.destroy()

	gui.root.protocol('WM_DELETE_WINDOW', on_close)
	refresh_status()
	gui.root.mainloop()


if __name__ == '__main__':
	main()
