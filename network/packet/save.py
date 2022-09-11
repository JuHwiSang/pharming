import time

class Save:
    idx: int = 0
    def __call__(self, data: bytes, msg: str) -> None:
        filename = f"./result/{self.idx}_{int(time.time())}_{msg}({len(data)}).log"
        with open(filename, "wb") as f:
            self.idx += 1
            f.write(data)
        print("save:", filename)