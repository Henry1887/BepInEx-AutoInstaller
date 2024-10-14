"""
Copyright (c) 2024, Henry
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. 
"""

import os
import win32file
import sys
import requests
import zipfile
import shutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import threading

if not os.path.isdir('scripts'):
    os.mkdir('scripts')
scripts = [script for script in os.listdir(
    'scripts') if script.endswith('.script')]


class Worker(QObject):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def log(self, msg: str):
        self.log_signal.emit(msg)


worker = Worker()


def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


def unzip(file: str):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall()


def interpreter(code: list):
    skip = 0
    for line in code:
        if skip > 0:
            skip -= 1
            print(f"skipped {line}")
            continue
        line = line.split('=')
        if line[0] == 'download' and len(line) == 3:
            download_url(line[1], line[2])
        elif line[0] == 'unzip' and len(line) == 2 and os.path.isfile(line[1]):
            unzip(line[1])
        elif line[0] == 'delete' and len(line) == 2:
            if os.path.isdir(line[1]):
                shutil.rmtree(line[1], ignore_errors=True)
            elif os.path.isfile(line[1]):
                os.remove(line[1])
        elif line[0] == 'move' and len(line) == 3:
            shutil.move(line[1], line[2])
        elif line[0] == 'copy' and len(line) == 3 and os.path.isdir(line[1]) and os.path.isdir(line[2]):
            shutil.copy(line[1], line[2])
        elif line[0] == 'rename' and len(line) == 3 and os.path.isfile(line[1]):
            if not os.path.isfile(line[2]):
                os.rename(line[1], line[2])
            else:
                raise Exception(f"Error: Cannot Rename {line[1]} to {
                                line[2]} as the target file name already exists.")
        elif line[0] == 'create' and len(line) == 2:
            if not os.path.isdir(line[1]):
                os.mkdir(line[1])
            else:
                print(f"Warning: {line[1]} already exists.")
        elif line[0] == 'skipiffileexists' and len(line) == 3:
            if os.path.isfile(line[1]):
                skip += int(line[2])
        elif line[0] == 'skipifdirectoryexists' and len(line) == 3:
            if os.path.isdir(line[1]):
                skip += int(line[2])
        elif line[0] == 'skipiffilenotexists' and len(line) == 3:
            if not os.path.isfile(line[1]):
                skip += int(line[2])
        elif line[0] == 'skipifdirectorynotexists' and len(line) == 3:
            if not os.path.isdir(line[1]):
                skip += int(line[2])
        elif line[0] == 'log' and len(line) == 2:
            print(f'Script Log: {line[1]}')
            worker.log(line[1])
        else:
            worker.log(f'Error: Invalid line: {line}')
            raise Exception(f'Error: Invalid line: {line}')
    print('Done!')


class Game:
    def __init__(self, executable):
        if not os.path.isfile(executable):
            raise Exception(
                'Error: Game Class could not be initialized: Executable does not exist.')
        self.executable = executable
        self.path = os.path.dirname(self.executable)
        exec_name = os.path.splitext(os.path.basename(self.executable))[0]
        self.data_path = os.path.join(self.path, f'{exec_name}_Data')
        if not os.path.isdir(self.data_path):
            raise Exception(
                'Error: Game Class could not be initialized: Game is not a Unity Game.')
        self.mono = not os.path.isfile(
            os.path.join(self.path, 'GameAssembly.dll'))
        self.bit64 = win32file.GetBinaryType(
            self.executable) != win32file.SCS_32BIT_BINARY
        with open(os.path.join(self.data_path, 'app.info'), 'r', encoding="utf-8") as f:
            lines = f.readlines()
            self.developer = lines[0].replace('\n', '')
            self.name = lines[1].replace('\n', '')

    def get_arch_str(self) -> str:
        match (self.bit64, self.mono):
            case [True, True]:
                return 'x64 Mono'
            case [True, False]:
                return 'x64 IL2CPP'
            case [False, True]:
                return 'x86 Mono'
            case [False, False]:
                return 'x86 IL2CPP'

    def __str__(self):
        return self.name


class Script:
    def __init__(self, script_path):
        if not os.path.isfile(script_path):
            raise Exception(
                'Error: Script Class could not be initialized: Script does not exist.')
        self.il2cpp_case = {'64': [], '32': []}
        self.mono_case = {'64': [], '32': []}
        self.name = os.path.splitext(os.path.basename(script_path))[0]
        self.dependancys = {'IL2CPP': [], 'MONO': []}
        with open(script_path, 'r') as f:
            lines = f.readlines()
            caseil2cpp = False
            case64 = False
            both = True
            both2 = True
            for line in lines:
                if line.startswith('#') or line.replace('\n', '') == '':
                    continue
                elif line.startswith('IL2CPP'):
                    caseil2cpp = True
                    if '64' in line:
                        case64 = True
                        both = False
                        both2 = False
                    elif '32' in line:
                        case64 = False
                        both = False
                        both2 = False
                    else:
                        both = True
                        both2 = False
                        case64 = False
                elif line.startswith('MONO'):
                    caseil2cpp = False
                    if '64' in line:
                        case64 = True
                        both = False
                        both2 = False
                    elif '32' in line:
                        case64 = False
                        both = False
                        both2 = False
                    else:
                        both = True
                        both2 = False
                        case64 = False
                elif line.startswith('GLOBAL'):
                    both2 = True
                    both = False
                    case64 = False
                    caseil2cpp = False
                elif line.startswith('DEPENDENCY'):
                    if line.startswith('DEPENDENCYIL2CPP'):
                        dependancy = line.split('=')[1]
                        self.dependancys['IL2CPP'].append(
                            dependancy.replace('\n', ''))
                    elif line.startswith('DEPENDENCYMONO'):
                        dependancy = line.split('=')[1]
                        self.dependancys['MONO'].append(
                            dependancy.replace('\n', ''))
                else:
                    if both2:
                        self.il2cpp_case['64'].append(line.replace('\n', ''))
                        self.il2cpp_case['32'].append(line.replace('\n', ''))
                        self.mono_case['64'].append(line.replace('\n', ''))
                        self.mono_case['32'].append(line.replace('\n', ''))
                    elif caseil2cpp:
                        if both:
                            self.il2cpp_case['64'].append(
                                line.replace('\n', ''))
                            self.il2cpp_case['32'].append(
                                line.replace('\n', ''))
                        elif case64:
                            self.il2cpp_case['64'].append(
                                line.replace('\n', ''))
                        else:
                            self.il2cpp_case['32'].append(
                                line.replace('\n', ''))
                    else:
                        if both:
                            self.mono_case['64'].append(line.replace('\n', ''))
                            self.mono_case['32'].append(line.replace('\n', ''))
                        elif case64:
                            self.mono_case['64'].append(
                                line.replace('\n', ''))
                        else:
                            self.mono_case['32'].append(
                                line.replace('\n', ''))
        self.il2cpp = len(self.il2cpp_case['64']) > 0 or len(
            self.il2cpp_case['32']) > 0
        self.mono = len(self.mono_case['64']) > 0 or len(
            self.mono_case['32']) > 0
        self.il2cpp64 = len(self.il2cpp_case['64']) > 0
        self.mono64 = len(self.mono_case['64']) > 0
        self.il2cpp32 = len(self.il2cpp_case['32']) > 0
        self.mono32 = len(self.mono_case['32']) > 0

    def __str__(self):
        return f'{self.name}, IL2CPP: {self.il2cpp}, MONO: {self.mono}'

    def is_compatible_with(self, game: Game):
        return (game.mono and game.bit64 and self.mono64) or (game.mono and not game.bit64 and self.mono32) or (not game.mono and game.bit64 and self.il2cpp64) or (not game.mono and not game.bit64 and self.il2cpp32)

    def install_dependencies_for(self, game: Game) -> bool:
        if game.mono:
            backend = "MONO"
        else:
            backend = "IL2CPP"
        try:
            if len(self.dependancys[backend]) > 0:
                for dependancy in self.dependancys[backend]:
                    if dependancy not in scripts:
                        worker.log(f'Error: Dependency not found \'{
                                   dependancy}\'')
                        raise Exception(
                            'Error: Script Dependency could not be found')
                    script = Script(os.path.join('scripts', dependancy))
                    script.run(game)
            return True
        except Exception as e:
            worker.log('Something went wrong while running a dependency')
            worker.log(str(e))
            print('Something went wrong while running a dependency')
            print(e)
        return False

    def run(self, game: Game):
        installButton.setEnabled(False)
        org = os.getcwd()
        try:
            if not self.is_compatible_with(game):
                worker.log('Error: Script is not compatible with the game.')
                raise Exception(
                    'Error: Script is not compatible with the game.')
            dependencies_installed = self.install_dependencies_for(game)
            os.chdir(game.path)
            if dependencies_installed:
                match (game.mono, game.bit64):
                    case [True, True]:
                        interpreter(self.mono_case['64'])
                    case [True, False]:
                        interpreter(self.mono_case['32'])
                    case [False, True]:
                        interpreter(self.il2cpp_case['64'])
                    case [False, False]:
                        interpreter(self.il2cpp_case['32'])
        except Exception as e:
            worker.log(str(e))
            print(e)
        os.chdir(org)
        installButton.setEnabled(True)


if __name__ == '__main__':
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle('BepInEx AutoInstaller V2')

    window.setStyleSheet("""
        QWidget {
            color: #FFFFFF;
            background-color: #282A36;
            font-family: Arial, sans-serif;
            font-size: 12pt;
        }
        QPushButton {
            background-color: #6272A4;
            border: 1px solid #44475A;
            border-radius: 10px;
            padding: 10px;
            color: #F8F8F2;
        }
        QPushButton:hover {
            background-color: #50FA7B;
        }
        QLabel {
            color: #F8F8F2;
        }
        QComboBox {
            background-color: #44475A;
            color: #F8F8F2;
            padding: 5px;
            border-radius: 5px;
        }
        QLineEdit {
            background-color: #44475A;
            color: #F8F8F2;
            border: 1px solid #6272A4;
            padding: 5px;
            border-radius: 5px;
        }
    """)

    layout = QVBoxLayout()
    gameLabel = QLabel('<h2>GAME_NAME</h2>', parent=window)
    gameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

    archLabel = QLabel('<h3>GAME_ARCH</h3>', parent=window)
    archLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

    layout.addSpacing(10)

    gameFile = QFileDialog(parent=window)
    gameFile.setFileMode(QFileDialog.FileMode.ExistingFile)
    gameFile.setNameFilter('*.exe')
    gameFile.setWindowTitle("Select Game's Executable")

    scriptComboBox = QComboBox(parent=window)
    scriptComboBox.addItems(scripts)

    installButton = QPushButton('Install', parent=window)
    installButton.clicked.connect(lambda: threading.Thread(target=lambda: Script(
        os.path.join('scripts', scriptComboBox.currentText())).run(game)).start())

    currentStatus = QLabel('<h4>Status:</h4>', parent=window)
    consoleBox = QTextEdit(parent=window)
    consoleBox.setReadOnly(True)
    consoleBox.setStyleSheet('background-color: #282A36; color: #50FA7B;')

    clearButton = QPushButton('Clear', parent=window)
    clearButton.clicked.connect(lambda: consoleBox.setText(''))

    worker.log_signal.connect(lambda msg: consoleBox.append(msg))

    layout.addWidget(gameLabel)
    layout.addWidget(archLabel)
    layout.addWidget(scriptComboBox)
    layout.addWidget(installButton)
    layout.addWidget(currentStatus)
    layout.addWidget(consoleBox)
    layout.addWidget(clearButton)

    window.setLayout(layout)
    window.setMinimumWidth(350)
    window.setMinimumHeight(400)
    window.show()

    gameFile.exec()
    if len(gameFile.selectedFiles()) == 0:
        sys.exit(0)
    game = Game(gameFile.selectedFiles()[0])
    gameLabel.setText(f'<h2>{str(game)}</h2>')
    archLabel.setText(f'<h3>{game.get_arch_str()}</h3>')

    sys.exit(app.exec())
