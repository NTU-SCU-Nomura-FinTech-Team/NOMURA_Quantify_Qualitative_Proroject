class Stack:
    def __init__(self):
        """
        To initialize a list to save processing job.
        """
        self.stack = ['main']

    def push(self, x):
        """
        To append job to list.
        """
        self.stack.append(x)

    def pop(self):
        """
        To remove latest job.
        """
        self.stack.pop(-1)

    def top(self):
        """
        To get the latest job.
        """
        if self.stack:
            return self.stack[-1]
        else:
            return False

    def get_stack(self):
        """
        To get the full list job.
        """
        return self.stack

    def is_empty(self):
        """
        To check whether is new job or a processing job.
        """
        result = False if self.stack else True
        return result

    def renew(self):
        """
        To reset job list.
        """
        self.stack = []
