import os
import itertools
import time
import curses
from copy import deepcopy as copy


def bold(msg):
	return u'\033[1m%s\033[0m' % msg

class System:
	def __init__(self):
		self.clean, self.count, self.average = 0, 0, 1
		self.state = {}
		self.meminfo()
		self.start = self.state['Dirty']
		self.max = copy(self.start)
		self.total = copy(self.start)

	def sync(self):
		os.system('sync')

	def update(self):
		self.meminfo()
		self.buffer = self.state['Dirty']
		self.wrback = self.state['Writeback']
		if self.buffer > self.max:
			self.max = self.buffer
		self.count += 1
		self.average += (self.buffer - self.average) / self.count
		new_clean = self.start - self.buffer
		if new_clean < self.clean:
			self.total += self.clean - new_clean
		self.clean = self.start - self.buffer
		self.cleaned = self.total - self.buffer

	def meminfo(self):
		with open('/proc/meminfo') as meminfo:
			for line in meminfo:
				k, v = line.replace('kB', '').replace(' ', '').split(':')
				self.state[k] = int(v)


class UI:
	def __init__(self):
		self.screen = curses.initscr()
		self.sys = System()
		self.sys.update()
		curses.noecho()
		curses.cbreak()

	def input_thread(L):
		raw_input()
		L.append(None)

	def close(self):
		curses.echo()
		curses.nocbreak()
		curses.endwin()

	def report_progress(self):
		width = self.screen.getmaxyx()[1] - 3
		try:
			#progress = (self.sys.average - self.sys.buffer) / self.sys.average
			buffer = self.sys.buffer / self.sys.max
		except ZeroDivisionError:
			buffer = 0
		#progress *= progress > 0
		#progress2 = self.sys.cleaned / self.sys.total
		#self.screen.addstr(0, 0, 'Initial buffer: {:{}} kB'.format(self.sys.start, 10))
		self.screen.addstr(1, 0, 'Current buffer: {:{}} kB'.format(self.sys.buffer, 10))
		self.screen.addstr(2, 0, 'Average buffer: {:{}} kB'.format(int(self.sys.average), 10))
		self.screen.addstr(3, 0, 'Max buffer:     {:{}} kB'.format(self.sys.max, 10))
		self.screen.addstr(5, 0, 'Writeback:      {:{}} kB'.format(self.sys.wrback, 10))
		self.screen.addstr(7, 0, 'Total buffered: {:{}} kB'.format(self.sys.total, 10))
		self.screen.addstr(8, 0, 'Total flushed:  {:{}} kB'.format(self.sys.cleaned, 10))
		#self.screen.addstr(11, 0, 'Progress: {:{}} % '.format(int(progress*100), 5))
		#self.screen.addstr(12, 0, '[{:{}}]'.format('#'*int(progress*width),width))
		if self.sys.buffer == self.sys.max:
			self.screen.addstr(11, 0, 'Buffer enlarging, please wait.%s'.format(int(buffer*100), 5) % (' '*(width-30)))
			self.screen.addstr(12, 0, '[%s]' % (' '*width))
		else:
			self.screen.addstr(11, 0, 'Buffer: {:{}} %% full %s'.format(int(buffer*100), 5) % (' '*(width-30)))
			self.screen.addstr(12, 0, '[%s>%s]' % ('-'*int(width-buffer*width), '#'*int(buffer*width)))
		#self.screen.addstr(14, 0, 'Overall Progress:       {:{}} %'.format(int(progress2*100), 3))
		#self.screen.addstr(15, 0, '[{:{}}]'.format('#'*int(progress2*width),width))
		self.screen.refresh()

	def loop(self):
		try:
			for i in itertools.count():
				self.sys.update()
				self.screen.clearok(i % 10 == 0)
				try:
					self.report_progress()
				except curses.error:
					self.screen.refresh()
				time.sleep(0.1)
		except KeyboardInterrupt:
			self.close()
		self.close()



if __name__ == '__main__':
	inst = UI()
	inst.loop()
	print('Total buffer flushed: ' + str(inst.sys.cleaned))
