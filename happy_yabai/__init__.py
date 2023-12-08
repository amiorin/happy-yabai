import typer
import json
import subprocess
import os

app = typer.Typer(name="happy-yabai", add_completion=False, no_args_is_help=True)
events_app = typer.Typer()
app.add_typer(events_app, name="events", no_args_is_help=True)

cmds_app = typer.Typer()
app.add_typer(cmds_app, name="cmds", no_args_is_help=True)

@cmds_app.command("cycle-layout")
def cycle_layout():
    yabai = Yabai()
    layout = yabai.yabai_run_with_json("""yabai -m query --spaces --display | jq 'map(select(."is-visible"))[0].type'""")
    if layout == "stack":
        yabai.yabai_run("yabai -m space --layout bsp")
    else:
        yabai.yabai_run("yabai -m space --layout stack")

@cmds_app.command("cycle-win-and-stack")
def cycle_win_and_stack():
    yabai = Yabai()
    layout = yabai.yabai_run_with_json("""yabai -m query --spaces --display | jq 'map(select(."is-visible"))[0].type'""")
    if layout == "stack":
        yabai.yabai_run("yabai -m window --focus stack.next || yabai -m window --focus stack.first")
    else:
        yabai.yabai_run("yabai -m window --focus next || yabai -m window --focus first")


@cmds_app.command("move-or-prev")
def move_or_prev(space: int):
    yabai = Yabai()
    current_space = yabai.yabai_run_with_json("""yabai -m query --windows | jq 'map(select(."has-focus"))[0].space'""")
    current_win = yabai.yabai_run_with_json("""yabai -m query --windows | jq 'map(select(."has-focus"))[].id'""")
    if space != current_space:
        yabai.yabai_run(f"yabai -m window --space {space}")
        yabai.yabai_run(f"yabai -m window {current_win} --focus")
        print("move window", space, current_space)
    else:
        yabai.yabai_run("yabai -m window --focus stack.prev || yabai -m window --focus stack.last || true")
        print("cycle backwards", space, current_space)

@cmds_app.command("swap-spaces")
def swap_spaces(display1, display2):
    yabai = Yabai()

@cmds_app.command("swap-windows")
def swap_windows(display1, display2):
    yabai = Yabai()
    display = yabai.yabai_run_with_json("""yabai -m query --windows | jq 'map(select(."has-focus"))[0].display'""")
    win1 = yabai.yabai_run_with_json("""yabai -m query --windows --display 1 | jq 'map(select(."is-visible"))[0].id'""")
    win2 = yabai.yabai_run_with_json("""yabai -m query --windows --display 2 | jq 'map(select(."is-visible"))[0].id'""")
    yabai.yabai_run(f"""yabai -m window {win1} --display {display2}""")
    yabai.yabai_run(f"""yabai -m window {win2} --display {display1}""")
    if display == display1:
        yabai.yabai_run(f"""yabai -m window {win2} --focus""")
        yabai.yabai_run(f"""yabai -m window {win1} --focus""")
    else:
        yabai.yabai_run(f"""yabai -m window {win1} --focus""")
        yabai.yabai_run(f"""yabai -m window {win2} --focus""")

@events_app.command("window-destroyed")
def window_destroyed():
    yabai = Yabai()
    yabai.yabai_run("yabai -m space --destroy")
    yabai.yabai_run("yabai -m window --focus recent")

@events_app.command("window-created")
def window_created():
    yabai = Yabai()
    win_id = int(os.environ["YABAI_WINDOW_ID"])
    yabai.move_window_to_new_space(win_id)

@events_app.command("space-moved")
def space_moved():
    yabai = Yabai()
    yabai.destroy_empty_spaces()

@events_app.command("fix-left-padding")
def fix_left_padding(pixels):
    yabai = Yabai()
    yabai.fix_left_padding(pixels)

class Yabai:
    def __init__(self):
        self.refresh()
    
    def refresh(self):
        self.windows = self.yabai_run_with_json("yabai -m query --windows")
        self.spaces = self.yabai_run_with_json("yabai -m query --spaces")
        self.displays = self.yabai_run_with_json("yabai -m query --displays")

    def create_space(self) -> int:
        self.yabai_run(f"yabai -m display --focus {self.main_display}")
        self.yabai_run("yabai -m space --create")
        return len(self.yabai_run_with_json(f"yabai -m query --spaces --display {self.main_display}"))
        
    def fix_left_padding(self, pixels):
        for s in self.spaces:
            if len(s["windows"]) > 1:
                self.yabai_run(f"yabai -m config --space {s['index']} left_padding {pixels}")
            else:
                self.yabai_run(f"yabai -m config --space {s['index']} left_padding 0")

    def destroy_empty_spaces(self):
        empty_spaces = []
        for s in self.spaces:
            if len(s["windows"]) == 0:
                empty_spaces.append(s["index"])
        empty_spaces.sort(reverse=True)
        for n in empty_spaces:
            print(f"destroying space {n}")
            self.yabai_run(f"yabai -m space --destroy {n}")

    def current_space_has_no_window(self):
        return False

    def move_window_to_new_space(self, win_id: int):
        space_id = self.create_space()
        self.yabai_run(f"yabai -m window {win_id} --space {space_id}")
        self.yabai_run(f"yabai -m window {win_id} --focus")

    @property
    def main_display(self):
        if len(self.displays) > 1:
            return 2
        else:
            return 1

    def yabai_run_with_json(self, cmd: str) -> json:
        output = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
        return json.loads(output.stdout)

    def yabai_run(self, cmd: str):
        subprocess.run(cmd, check=True, shell=True)

def run():
    app()