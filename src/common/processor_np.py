from processor import processor
import numpy as np
from data_stream import *
import collections

class processor_np(processor):
    """
    base class for processors taking in numpy arrays
    """
    def __init__(self, istream_handle, buff_size, resid_size, observation_shape, dtype):
        super(processor_np, self).__init__()
        self.istream_handle = istream_handle
        self.istream = istream_handle.stream
        self.ostream = None
        self.buff_size = buff_size
        self.resid_size = resid_size
        self.observation_shape = observation_shape
        self.dtype = dtype
        return

    def work(self, buff, size, pos):
        pass
    
    def run(self):
        buff = np.zeros((self.buff_size,) + self.observation_shape, dtype = self.dtype)
        tail = self.resid_size
        queue = collections.deque()
        while self.istream_handle.pos < self.istream.total_samples or len(queue):
            if self.istream_handle.pos < self.istream.total_samples:
                pos, n, queue = self.istream_handle.read(self.buff_size - tail, queue)
                #print pos, n, self.buff_size - tail
            while tail < self.buff_size and len(queue):
                tmp = queue.popleft()
                if len(tmp) <= self.buff_size - tail:
                    buff[tail: tail + len(tmp)] = tmp
                    tail = tail + len(tmp)
                else:
                    buff[tail:] = tmp[:self.buff_size - tail]
                    queue.appendleft(tmp[self.buff_size - tail:])
                    tail = self.buff_size
            
            self.work(buff, tail, pos)
            buff[:self.resid_size] = buff[self.buff_size - self.resid_size:]
            tail = self.resid_size
        if self.ostream:
            self.ostream.finish_writing()
        print 'proc finish'