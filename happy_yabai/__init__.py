import typer
import subprocess

def main(name: str):
    name = "yabai -m query --windows"
    subprocess.run(name, shell=True)

def run():
    typer.run(main)

if __name__ == "__main__":
    typer.run(main)
