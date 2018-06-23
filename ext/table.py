import sys
import time

import keyboard
from termcolor import cprint

class Table:
    def __init__(self, ctx, callback, *items, **options):
        self.ctx = ctx
        self.callback = callback
        self.items = list(items)
        self.options = {
            'padding': options.get('padding') or '   ',
            'max_num': 3
        }
        self.current_index = 0
        self.rows = 0
        self.maxlen = max([len(i) for i in items])
        self.full_len = self.maxlen + len(self.options['padding'])

        for n, i in enumerate(items):
            self.items[n] = i + ' ' * (self.maxlen - len(i)) + self.options['padding']
            self.items[n] = ' ' + self.items[n]
            if (n + 1) % self.options['max_num'] == 0 or n == len(items) - 1:
                self.items[n] += '\n'
                self.rows += 1

    def start(self):
        for n, i in enumerate(self.items):
            if n == 0:
                cprint(i, 'grey', 'on_white', end='')
            else:
                cprint(i, end='')
        self.move_cursor(x=-1, y=self.rows)
        self.wait_for_input()

    def move_cursor(self, **coords: int):
        y = coords.get('y')
        x = coords.get('x', '')
        if y:
            if abs(y) == y:
                y = '\033[{}A'.format(y)
            else:
                y = '\033[{}B'.format(abs(y))
            sys.stdout.write(y)
        if x:
            if abs(x) == x:
                x = '\033[{}C'.format(x)
            else:
                x = '\033[{}D'.format(abs(x))
            sys.stdout.write(x)
        sys.stdout.flush()

    def reload_text(self, index):
        if index == self.current_index:
            cprint(self.items[index], 'grey', 'on_white', end='')
        else:
            cprint(self.items[index], end='')

    def wait_for_input(self):
        time.sleep(1)
        keyboard.on_release_key('up', self.input_callback)
        keyboard.on_release_key('down', self.input_callback)
        keyboard.on_release_key('left', self.input_callback)
        keyboard.on_release_key('right', self.input_callback)
        keyboard.on_release_key('enter', self.input_callback)

    def input_callback(self, key):
        if key.name == 'right':
            self.current_index += 1
            self.reload_text(self.current_index - 1)
            self.reload_text(self.current_index)
            if (self.current_index + 1) % self.options['max_num'] == 0:
                self.move_cursor(x=self.full_len * (self.options['max_num'] - 1) + 2, y=1)
            else:
                self.move_cursor(x=-self.full_len - 1)

        if key.name == 'left':
            self.current_index -= 1
            self.reload_text(self.current_index + 1)
            if (self.current_index + 2) % self.options['max_num'] == 0:
                self.move_cursor(x=self.full_len * (self.options['max_num'] - 2) + 1, y=1)
            elif (self.current_index + 1) % self.options['max_num'] == 0:
                self.move_cursor(x=self.full_len + 1, y=1)
            else:
                self.move_cursor(x=-self.full_len * (self.options['max_num'] - 1) - 2)
            self.reload_text(self.current_index)
            if (self.current_index + 1) % self.options['max_num'] == 0:
                self.move_cursor(x=self.full_len * (self.options['max_num'] - 1) + 2, y=1)
            else:
                self.move_cursor(x=-self.full_len - 1)

        if key.name == 'enter':
            current_column = ((self.current_index + 1) % self.options['max_num'])
            current_row = ((self.current_index + 1) // self.options['max_num']) + 1
            self.move_cursor(x=-self.full_len * (current_column - 1) - 1, y=self.rows % current_row)
            for _ in range(self.rows):
                sys.stdout.write('\033[K')
                self.move_cursor(y=-1)
            self.move_cursor(x=-self.full_len * self.rows, y=self.rows)
            keyboard.unhook_all()

            self.ctx.bot.paused = False
            try:
                import msvcrt
                while msvcrt.kbhit():
                    msvcrt.getch()
            except ImportError:
                import termios  #for linux/unix
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
            self.callback(self.ctx, self.items[self.current_index].strip())
