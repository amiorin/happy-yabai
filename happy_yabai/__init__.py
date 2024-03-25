from typing import Any
import typer
import json
import subprocess
import os

app = typer.Typer(name="happy-yabai", add_completion=False, no_args_is_help=True)
events_app = typer.Typer()
app.add_typer(events_app, name="events", no_args_is_help=True)

cmds_app = typer.Typer()
app.add_typer(cmds_app, name="cmds", no_args_is_help=True)

def yabai_run_capture_json(cmd: str) -> Any:
    #print(cmd)
    output = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    return json.loads(output.stdout)

def yabai_run(cmd: str):
    #print(cmd)
    subprocess.run(cmd, check=True, shell=True)

@cmds_app.command("cycle-layout")
def cycle_layout():
    layout = yabai_run_capture_json("""yabai -m query --spaces --display | jq 'map(select(."is-visible"))[0].type'""")
    if layout == "stack":
        yabai_run("yabai -m space --layout bsp")
    else:
        yabai_run("yabai -m space --layout stack")

@cmds_app.command("swap")
def swap():
    current_win = yabai_run_capture_json("""yabai -m query --windows | jq 'map(select(."has-focus"))[].id'""")
    space_is_visible_no_focus = yabai_run_capture_json("""yabai -m query --spaces | jq 'map(select(."has-focus" | not)) | map(select(."is-visible")).[].index'""")
    if space_is_visible_no_focus:
        yabai_run(f"yabai -m window {current_win} --space {space_is_visible_no_focus}")
        yabai_run(f"yabai -m window {current_win} --focus")

@cmds_app.command("move-or-prev")
def move_or_prev(space: int):
    current_space = yabai_run_capture_json("""yabai -m query --windows | jq 'map(select(."has-focus"))[0].space'""")
    current_win = yabai_run_capture_json("""yabai -m query --windows | jq 'map(select(."has-focus"))[].id'""")
    if space != current_space:
        yabai_run(f"yabai -m window {current_win} --space {space}")
        yabai_run(f"yabai -m window {current_win} --focus")
    else:
        layout = yabai_run_capture_json("""yabai -m query --spaces --display | jq 'map(select(."is-visible"))[0].type'""")
        if layout == "stack":
            yabai_run("yabai -m window --focus stack.prev || yabai -m window --focus stack.last || true")
        else:
            yabai_run("yabai -m window --focus prev || yabai -m window --focus last || true")


@cmds_app.command("move-or-next")
def move_or_next(space: int):
    current_space = yabai_run_capture_json("""yabai -m query --windows | jq 'map(select(."has-focus"))[0].space'""")
    layout = yabai_run_capture_json("""yabai -m query --spaces --display | jq 'map(select(."is-visible"))[0].type'""")
    if space != current_space:
        yabai_run(f"yabai -m space --focus {space}")
    else:
        if layout == "stack":
            yabai_run("yabai -m window --focus stack.next || yabai -m window --focus stack.first || true")
        else:
            yabai_run("yabai -m window --focus next || yabai -m window --focus first || true")


def run():
    app()
