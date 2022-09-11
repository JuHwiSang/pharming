class DebugSave:
    idx: int = 0
    def __call__(self, data: bytes, msg: str = "") -> None:
        with open(f"./debug/{self.idx}_{msg}.log", "wb") as f:
            self.idx += 1
            f.write(data)
debug_save = DebugSave()