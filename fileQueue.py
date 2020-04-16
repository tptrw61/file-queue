import os

class FileQueue:
    def __init__(self, fileobj=None):
        self.__file = None
        self.__filename = None
        self.__size = 0
        self.__pos = None
        self.__tell = None
        self.__currentVal = None
        self.__bookmarks = dict()
        if fileobj == None:
            i = 0
            while os.path.exists(f".t{i:03}.fq"):
                i += 1
                self.__filename = f".t{i:03}.fq"
                self.__file = open(self.__filename, 'r+')
        elif type(fileobj) == str:
            self.__filename = fileobj
            self.__file = open(fileobj, 'r+')
            #check file size then decide how to count lines
            self.__file.seek(0)
            while True:
                if len(self.__file.readline()) == 0:
                    break
                self.__size += 1
            self.__file.seek(0)
        if self.__size > 0:
            self.__bookmarks['start'] = (0, 0)
            self.__bookmarks[0] = (0, 0)

    def filename(self):
        return self.__filename
    def size(self):
        return self.__size
    def pos(self):
        return self.__pos
    def val(self):
        return self.__currentVal
    def bookmark(self, key):
        if self.__pos == None:
            return False
        self.__bookmarks[key] = (self.__tell, self.__pos)
        return True
    def gotoBookmark(self, key):
        if not key in self.__bookmarks.keys():
            return False
        tpl = self.__bookmarks[key]
        self.__file.seek(tpl[0])
        self.__pos = tpl[1] - 1 #it gets incremented in next
        self.next()
        return True
    
    def next(self):
        if self.__size == 0:
            return None
        elif self.__pos == None:
            self.__pos = 0
            self.__bookmarks['start'] = (0, 0)
            self.__bookmarks[0] = (0, 0)
        elif self.__pos + 1 == self.__size:
            return None
        else:
            self.__pos += 1
        self.__tell = self.__file.tell()
        self.__currentVal = self.__file.readline().replace('\n', '')
        return self.__currentVal

    def add(self, val):
        s = str(val).replace('\n','\\n')
        tell = self.__file.tell()
        self.__file.seek(0, 2)
        self.__file.write(f"{s}\n")
        self.__file.seek(tell)
        self.__size += 1
        self.__file.flush()

    def close(self):
        if self.__pos == None or self.__pos == 0:
            self.__file.close()
            return
        current = self.__file.tell()
        self.__file.seek(0)
        self.__file.write(self.__currentVal)
        write = self.__file.tell()
        self.__file.seek(current)
        s = self.next()
        while not s == None:
            current = self.__file.tell()
            self.__file.seek(write)
            self.__file.write(self.__currentVal)
            write = self.__file.tell()
            self.__file.seek(current)
            s = self.next()
        self.__file.seek(0)
        self.__file.truncate(write)
        self.__file.flush()
        self.__file.close()
