import asyncio
import os
import subprocess
import webbrowser
import psutil
from nicegui import ui

NUBOTS_DIR = os.path.expanduser('~/nubots')
NUSIGHT_DIR = os.path.expanduser('~/nubots/nusight2')
NUSIGHT_PORT = 9090
SSH_USER = 'nubots'
REFRESH_TIME = 1.0
DEFAULT_INTERFACE = 'wlp166s0' # made for the framework 13, suck shit if that's not yours :P

ROBOTS = [
    {'name': 'n1', 'friendly_name': 'Kevin', 'ip': '10.0.1.1'},
    {'name': 'n2', 'friendly_name': 'Billie', 'ip': '10.0.1.2'},
    {'name': 'n3', 'friendly_name': 'Sarah', 'ip': '10.0.1.3'},
    {'name': 'n4', 'friendly_name': 'Frankie', 'ip': '10.0.1.4'},
]

# gotta have dark mode
ui.dark_mode().toggle()
ui.page_title("NUStatus")

with ui.row().style('width: 100%; align-items: center;'):
    ui.label('NUStatus').classes('text-4xl font-bold').style('margin-left: 20px; font-family: Helvetica Neue; font-weight: bold; flex: 1;')
    ui.image('NUbots_Banner.svg').style('width: 200px; flex-shrink: 0;')
    ui.element('div').style('flex: 1;')

with ui.row().classes('items-center gap-4'):
    ui.label('Select Network Interface:').classes('text-lg')
    interfaces = list(psutil.net_if_addrs().keys())
    ui.select(interfaces, value=DEFAULT_INTERFACE if DEFAULT_INTERFACE in interfaces else interfaces[0] if interfaces else None, label='Network Interface').style('width: 300px;')

ui.separator()

async def is_online(ip: str) -> bool:
    proc = await asyncio.create_subprocess_exec(
        'ping', '-c', '1', '-W', '1', ip,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()
    return proc.returncode == 0

def open_ssh(ip: str) -> None:
    subprocess.Popen(['gnome-terminal', '--', 'sshpass', '-p', ' ', 'ssh', f'{SSH_USER}@{ip}'])

def install(robot: str, with_config: bool) -> None:
    if with_config:
        subprocess.Popen(['gnome-terminal', '--', './b', 'install', '-co', robot], cwd=NUBOTS_DIR)
    else:
        subprocess.Popen(['gnome-terminal', '--', './b', 'install', robot], cwd=NUBOTS_DIR)

nusight_proc: subprocess.Popen | None = None

def start_nusight(ip: str) -> None:
    global nusight_proc
    if nusight_proc is None or nusight_proc.poll() is not None:
        nusight_proc = subprocess.Popen(['gnome-terminal', '--', './b', 'yarn', 'prod', '--address', ip], cwd=NUBOTS_DIR)
    ui.timer(1.5, lambda: webbrowser.open(f'http://localhost:{NUSIGHT_PORT}'), once=True)

for robot in ROBOTS:
    with ui.row().classes('items-center gap-4 py-2'):
        led = ui.icon('circle', size='sm').classes('text-red-500').style('filter: drop-shadow(0 0 6px currentColor)')
        ui.label(robot['friendly_name']).classes('text-lg font-mono w-24')
        ui.label(robot['name']).classes('text-sm text-gray-500 font-mono w-24')
        ui.label(robot['ip']).classes('font-mono text-gray-400 w-32')
        ui.button('SSH', on_click=lambda ip=robot['ip']: open_ssh(ip)).props('color=primary')
        ui.button('NUsight', on_click=lambda ip=robot['ip']: start_nusight(ip)).props('color=positive')
        ui.button('Install', on_click=lambda robot=robot['name']: install(robot, with_config=False)).props('color=secondary')
        ui.button('Install (with config)', on_click=lambda robot=robot['name']: install(robot, with_config=True)).props('color=secondary').style('font-weight: bold;')

        async def refresh_led(l=led, ip=robot['ip']) -> None:
            online = await is_online(ip)
            if online:
                l.classes(remove='text-red-500', add='text-green-500')
            else:
                l.classes(remove='text-green-500', add='text-red-500')

        ui.timer(REFRESH_TIME, refresh_led)

ui.run(favicon='Ball_Black.png')
