''' written by Richard Pattis @rpattis.uci.edu

used for testing by Klint Segarra
'''

import time


class Stopwatch:
    """
    Models a stopwatch, tracking wallclock time.
    Stopwatches can be started (run forwards and backwards), stopped, and read.
    """
    def __init__(self, running_now=False, running_forward=True, elapsed_prior=0, last_start_time=0):
        """
        Instantiate like Stopwatch()
        Stopwatch instance is stopped with 0 elapsed wallclock time.
        """
        self._running_now     = running_now
        self._running_forward = running_forward
        self._elapsed_prior   = elapsed_prior
        self._last_start_time =  (time.clock() if running_now else last_start_time)


    def reset(self):
        """
        Stopwatch is now stopped with 0 elapsed wallclock time.
        """
        self._running_now     = False
        self._running_forward = True
        self._elapsed_prior   = 0
        self._last_start_time = 0


    def start(self):
        """
        Stopwatch is now running forwards, accumulating wallclock time.
        """
        if self._running_now: 
            if self._running_forward:
                return
            else:                             # running backward
                self._update()                # update, then start running forward
        self._last_start_time = time.clock()
        self._running_now     = True
        self._running_forward = True


    def start_backwards(self):
        """
        Stopwatch is now running backwards, [un]accumulating wallclock time.
        """
        if self._running_now: 
            if not self._running_forward:
                return
            else:                             # running forward
                self._update()                # update, then start running backward
        self._last_start_time = time.clock()
        self._running_now     = True
        self._running_forward = False


    def stop(self):
        """
        Stopwatch is now stopped: not accumulating wallclock time.
        """
        if not self._running_now:
            return
        self._running_now = False
        self._update()

        
    def read(self):
        """
        Returns the elapsed wallclock time in seconds as a float.
        Works when the Stopwatch is running and when it is stopped.
        """
        if self._running_now:
            self._update()
        return self._elapsed_prior


    def __str__(self):
        """
        Returns a string representation for a Stopwatch, such that
        s2 = eval(str(s1)) copies the state of s1 at the time of the call
        """
        return "Stopwatch("+ \
               str(self._running_now)     + ","  +   \
               str(self._running_forward) + ","  +   \
               str(self._elapsed_prior)   + ","  +   \
               str(self._last_start_time) + ")"

    
    def status(self):
        """
        Returns the status of the Stopwatch: a tuple
        (running?, forward?, elapsed) :  (bool, bool, float)
        """
        return (self._running_now, self._running_forward, self.read())

    
    def _update(self):
        """
        Accumulates time from last start time; now becomes last start time
        """
        self._elapsed_prior  += (1 if self._running_forward else -1) * (time.clock() - self._last_start_time)
        self._last_start_time  = time.clock()



        
if __name__ == "__main__": 
    import prompt
    print("Begin testing Stopwatch") 
    commandPrompt = \
"""\nTesting Stopwatch:
Commands                Queries        Other
  > - start               ? - read       . - exec(...)
  s - stop                : - status     q - quit
  < - start_backwards     _ - __str__
  r - reset\nCommand"""                            
    s = Stopwatch()
    while True:
        action = prompt.for_char(commandPrompt, legal=">s<r?:_.q")
        try:
            if   action == ">": s.start()
            elif action == "s": s.stop()
            elif action == "<": s.start_backwards()
            elif action == "r": s.reset()
            elif action == "?": print("  Elapsed =", s.read(), "seconds")
            elif action == ":": print("  Status =", s.status())
            elif action == "_": print("  __str__ =", str(s))
            elif action == ".": exec(prompt.for_string("  Enter command to exec (instance=s)"))
            elif action == "q": break
            else: print("  Unknown command")
        except AssertionError as report:
            print("  AssertionError exception caught:", report)
        except Exception as report:
            import traceback
            traceback.print_exc()
    print("\nFinished testing Stopwatch")
