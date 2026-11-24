from collections import deque
import random
import time

# 0 = ทางเดิน, 1 = กำแพง, 2 = จุดเริ่ม, 3 = เส้นชัย, 4 = กุญแจ, 5 = ประตูล็อก
LEVELS = [
    [
        [2, 0, 1, 4, 1, 0, 0],
        [1, 0, 1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 5, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 3],
    ],
    [
        [2, 0, 0, 1, 4, 0, 0, 1, 0],
        [1, 1, 0, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0],
        [1, 1, 0, 1, 0, 1, 1, 5, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 3],
    ],
    [
        [2, 0, 1, 0, 0, 0, 1, 4, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 5],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    ],
]

DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}


def generate_random_maze(size: int = 9) -> list[list[int]]:
    """สุ่มสร้างเขาวงกตขนาดคี่ (ขั้นต่ำ 7) พร้อมกุญแจ (4) และประตูล็อก (5) ที่เล่นผ่านได้จริง"""
    size = max(7, size if size % 2 == 1 else size + 1)
    grid = [[1 for _ in range(size)] for _ in range(size)]

    def carve(r: int, c: int):
        grid[r][c] = 0
        dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 1:
                grid[r + dr // 2][c + dc // 2] = 0
                carve(nr, nc)

    carve(0, 0)

    start = (0, 0)
    goal = (size - 1, size - 1)
    grid[start[0]][start[1]] = 2
    grid[goal[0]][goal[1]] = 3

    for r, c in [(0, 1), (1, 0), (size - 1, size - 2), (size - 2, size - 1)]:
        if grid[r][c] == 1:
            grid[r][c] = 0

    queue = deque([(start, [start])])
    visited = {start}
    main_path = []

    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == goal:
            main_path = path
            break
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] != 1 and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))

    door_pos = None
    if len(main_path) >= 5:
        door_idx = len(main_path) - 2
        dr, dc = main_path[door_idx]
        if (dr, dc) not in (start, goal):
            grid[dr][dc] = 5
            door_pos = (dr, dc)

    reachable_before_door = []
    q2 = deque([start])
    vis2 = {start}
    while q2:
        r, c = q2.popleft()
        if (r, c) not in (start, goal) and (r, c) != door_pos and grid[r][c] == 0:
            reachable_before_door.append((r, c))
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < size
                and 0 <= nc < size
                and (nr, nc) != door_pos
                and grid[nr][nc] != 1
                and (nr, nc) not in vis2
            ):
                vis2.add((nr, nc))
                q2.append((nr, nc))

    if reachable_before_door:
        reachable_before_door.sort(key=lambda p: abs(p[0] - start[0]) + abs(p[1] - start[1]), reverse=True)
        kr, kc = reachable_before_door[0]
        grid[kr][kc] = 4

    return grid


class MazeGame:
    def __init__(self, level_index: int = 0):
        self.custom_grid: list[list[int]] | None = None
        self.is_random = False
        self.started = False
        self.reset(level_index, keep_started=False)

    def reset(
        self,
        level_index: int | None = None,
        custom_grid: list[list[int]] | None = None,
        keep_started: bool = True,
    ):
        if level_index is not None:
            self.level_index = max(0, min(level_index, len(LEVELS) - 1))

        if custom_grid is not None:
            self.custom_grid = [row[:] for row in custom_grid]
            self.is_random = True
            self.grid = [row[:] for row in self.custom_grid]
        elif self.is_random and self.custom_grid is not None and level_index is None:
            self.grid = [row[:] for row in self.custom_grid]
        else:
            self.custom_grid = None
            self.is_random = False
            self.grid = [row[:] for row in LEVELS[self.level_index]]

        self.rows = len(self.grid)
        self.cols = len(self.grid[0])

        start_pos = (0, 0)
        goal_pos = (self.rows - 1, self.cols - 1)

        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == 2:
                    start_pos = (r, c)
                elif self.grid[r][c] == 3:
                    goal_pos = (r, c)

        self.player = {"row": start_pos[0], "col": start_pos[1]}
        self.goal = {"row": goal_pos[0], "col": goal_pos[1]}
        self.steps = 0
        self.has_key = False
        self.won = False
        self.started = keep_started
        self.start_time = time.monotonic()
        self.final_elapsed: int | None = None
        self.last_status = "พร้อมออกเดินทาง! เก็บกุญแจเพื่อเปิดประตูล็อกแล้วมุ่งสู่เส้นชัย"

    def start_game(self, level_index: int | None = None, random_size: int | None = None):
        if random_size is not None:
            new_grid = generate_random_maze(size=random_size)
            self.reset(level_index=level_index, custom_grid=new_grid, keep_started=True)
            self.last_status = f"เริ่มภารกิจเขาวงกตสุ่มขนาด {self.rows}×{self.cols}! ตามหากุญแจเพื่อไขประตู"
        else:
            self.reset(
                level_index=level_index if level_index is not None else self.level_index,
                custom_grid=None,
                keep_started=True,
            )
            self.last_status = f"เริ่มภารกิจด่าน {self.level_index + 1}! เก็บกุญแจเพื่อเปิดประตูล็อก"

    def generate_new_random(self, size: int = 9):
        new_grid = generate_random_maze(size=size)
        self.reset(custom_grid=new_grid, keep_started=True)
        self.last_status = f"สร้างเขาวงกตสุ่มขนาด {self.rows}×{self.cols} สำเร็จ! ตามหากุญแจเพื่อไขประตู"

    def get_elapsed_seconds(self) -> int:
        if not self.started:
            return 0
        if self.won and self.final_elapsed is not None:
            return self.final_elapsed
        return max(0, int(time.monotonic() - self.start_time))

    def calculate_score(self) -> int:
        elapsed = self.get_elapsed_seconds()
        difficulty_mult = self.level_index + 2 if self.is_random else self.level_index + 1
        base_score = 1000 * difficulty_mult
        step_penalty = self.steps * 15
        time_penalty = elapsed * 10
        win_bonus = 400 if self.won else 0
        return max(50, base_score - step_penalty - time_penalty + win_bonus)

    def move(self, direction: str) -> dict:
        if not self.started:
            return {
                "valid": False,
                "message": "กรุณากด 'เริ่มเข้าสู่เขาวงกต' ที่หน้าเริ่มเกมก่อนครับ",
            }

        direction = direction.upper()
        if self.won:
            return {
                "valid": False,
                "message": "คุณถึงเส้นชัยแล้ว! บันทึกชื่อลง Leaderboard หรือเริ่มด่านใหม่ได้เลย",
            }

        if direction not in DIRECTIONS:
            return {
                "valid": False,
                "message": f"ทิศทางไม่ถูกต้อง: {direction}",
            }

        dr, dc = DIRECTIONS[direction]
        next_r = self.player["row"] + dr
        next_c = self.player["col"] + dc

        if not (0 <= next_r < self.rows and 0 <= next_c < self.cols):
            return {
                "valid": False,
                "message": "ชนขอบนอกสุดของตารางกริด เดินต่อไม่ได้!",
            }

        target_cell = self.grid[next_r][next_c]

        if target_cell == 1:
            return {
                "valid": False,
                "message": "ชนกำแพง! ลองมองหาช่องทางเดินอื่นดู",
            }

        if target_cell == 5:
            if not self.has_key:
                return {
                    "valid": False,
                    "message": "ประตูล็อกอยู่! คุณต้องเก็บกุญแจก่อนจึงจะเปิดประตูนี้ได้",
                }
            self.grid[next_r][next_c] = 0
            self.has_key = False
            self.player["row"] = next_r
            self.player["col"] = next_c
            self.steps += 1
            self.last_status = f"ไขประตูล็อกสำเร็จที่พิกัด ({next_r + 1}, {next_c + 1})!"
            return {"valid": True, "message": self.last_status}

        self.player["row"] = next_r
        self.player["col"] = next_c
        self.steps += 1

        if target_cell == 4:
            self.has_key = True
            self.grid[next_r][next_c] = 0
            self.last_status = f"เก็บกุญแจได้แล้วที่พิกัด ({next_r + 1}, {next_c + 1})! นำไปไขประตูล็อกได้เลย"
            return {"valid": True, "message": self.last_status}

        if (next_r, next_c) == (self.goal["row"], self.goal["col"]):
            self.won = True
            self.final_elapsed = self.get_elapsed_seconds()
            final_score = self.calculate_score()
            self.last_status = (
                f"ยินดีด้วย! ถึงเส้นชัยใน {self.steps} ก้าว • เวลา {self.final_elapsed} วิ • คะแนน {final_score}"
            )
            return {"valid": True, "message": self.last_status}

        self.last_status = f"เดินไปทาง {direction} สำเร็จ (พิกัดแถว {next_r + 1}, คอลัมน์ {next_c + 1})"
        return {"valid": True, "message": self.last_status}

    def _bfs(
        self,
        start: tuple[int, int],
        target: tuple[int, int],
        allow_locked_door: bool,
    ) -> list[tuple[int, int]]:
        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            (r, c), path = queue.popleft()
            if (r, c) == target:
                return path

            for dr, dc in DIRECTIONS.values():
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and (nr, nc) not in visited:
                    cell = self.grid[nr][nc]
                    if cell == 1:
                        continue
                    if cell == 5 and not allow_locked_door:
                        continue
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [(nr, nc)]))

        return []

    def shortest_path(self) -> list[list[int]]:
        start = (self.player["row"], self.player["col"])
        goal = (self.goal["row"], self.goal["col"])

        keys = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.grid[r][c] == 4
        ]

        if not self.has_key and keys:
            nearest_key_path = []
            for k_pos in keys:
                p_to_key = self._bfs(start, k_pos, allow_locked_door=False)
                k_to_goal = self._bfs(k_pos, goal, allow_locked_door=True)
                if p_to_key and k_to_goal:
                    combined = p_to_key + k_to_goal[1:]
                    if not nearest_key_path or len(combined) < len(nearest_key_path):
                        nearest_key_path = combined
            if nearest_key_path:
                return [[r, c] for r, c in nearest_key_path]

        path_to_goal = self._bfs(start, goal, allow_locked_door=self.has_key)
        return [[r, c] for r, c in path_to_goal]

    def to_dict(self, include_hint: bool = False) -> dict:
        data = {
            "started": self.started,
            "level": self.level_index + 1,
            "total_levels": len(LEVELS),
            "is_random": self.is_random,
            "rows": self.rows,
            "cols": self.cols,
            "grid": self.grid,
            "player": self.player,
            "goal": self.goal,
            "steps": self.steps,
            "has_key": self.has_key,
            "elapsed_seconds": self.get_elapsed_seconds(),
            "score": self.calculate_score(),
            "won": self.won,
            "status": self.last_status,
        }
        if include_hint:
            data["hint_path"] = self.shortest_path()
        return data