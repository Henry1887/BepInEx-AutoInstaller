"""
Copyright (c) 2023, Henry1887
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. 
"""

import sys
import zipfile
import os
import shutil
import win32file
import requests
from rich.console import Console

console = Console()
il2cpp = False
arch = ""

try:
    game_exe = sys.argv[1]
except Exception:
    files = os.listdir()
    games_in_cur_dir = [
        file
        for file in files
        if file.endswith(".exe") and os.path.exists(file.replace(".exe", "") + "_Data")
    ]
    if len(games_in_cur_dir) == 1:
        game_exe = os.path.join(os.getcwd(), games_in_cur_dir[0])
    elif len(games_in_cur_dir) > 1:
        console.print("Multiple games found in this directory!",
                      style="red on black")
        console.print("Automatic Detection is not possible.",
                      style="red on black")
        input("Press Enter to continue...")
        sys.exit(0)
    else:
        console.print("You have to specify the games exe file.",
                    style="red on black")
        input("Press Enter to continue...")
        sys.exit(0)
if not os.path.isfile(game_exe):
    console.print("Game not found!", style="red on black")
    input("Press Enter to continue...")
    sys.exit(0)


def get_bepinexIL2CPP64() -> str:
    return "https://builds.bepinex.dev/projects/bepinex_be/577/BepInEx_UnityIL2CPP_x64_ec79ad0_6.0.0-be.577.zip"

def get_bepinexxIL2CPP86() -> str:
    return "https://builds.bepinex.dev/projects/bepinex_be/577/BepInEx_UnityIL2CPP_x86_ec79ad0_6.0.0-be.577.zip"

def get_bepinex64() -> str:
    return "https://github.com/BepInEx/BepInEx/releases/download/v5.4.21/BepInEx_x64_5.4.21.0.zip"

def get_bepinex86() -> str:
    return "https://github.com/BepInEx/BepInEx/releases/download/v5.4.21/BepInEx_x86_5.4.21.0.zip"

def get_bepinex6IL2CPP64() -> str:
    return "https://github.com/BepInEx/BepInEx/releases/download/v6.0.0-pre.1/BepInEx_UnityIL2CPP_x64_6.0.0-pre.1.zip"

def get_bepinex6IL2CPP86() -> str:
    return "https://github.com/BepInEx/BepInEx/releases/download/v6.0.0-pre.1/BepInEx_UnityIL2CPP_x86_6.0.0-pre.1.zip"

def get_bepinex664() -> str:
    return "https://github.com/BepInEx/BepInEx/releases/download/v6.0.0-pre.1/BepInEx_UnityMono_x64_6.0.0-pre.1.zip"

def get_bepinex686() -> str:
    return "https://github.com/BepInEx/BepInEx/releases/download/v6.0.0-pre.1/BepInEx_UnityMono_x86_6.0.0-pre.1.zip"

def get_bepinexBEBuild64() -> str:
    return "https://builds.bepinex.dev/projects/bepinex_be/668/BepInEx-Unity.Mono-win-x64-6.0.0-be.668%2B46e297f.zip"

def get_bepinexBEBuild86() -> str:
    return "https://builds.bepinex.dev/projects/bepinex_be/668/BepInEx-Unity.Mono-win-x86-6.0.0-be.668%2B46e297f.zip"

def get_bepinexBEBuildIL2CPP64() -> str:
    return "https://builds.bepinex.dev/projects/bepinex_be/668/BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.668%2B46e297f.zip"

def get_bepinexBEBuildIL2CPP86() -> str:
    return "https://builds.bepinex.dev/projects/bepinex_be/668/BepInEx-Unity.IL2CPP-win-x86-6.0.0-be.668%2B46e297f.zip"

def determine_arch() -> str:
    il2cpp = bool(os.path.isfile("GameAssembly.dll"))
    bit64 = False
    if os.path.isfile("UnityCrashHandler64.exe"):
        bit64 = True
    elif not os.path.isfile("UnityCrashHandler32.exe"):
        bit64 = win32file.GetBinaryType(game_exe) != win32file.SCS_32BIT_BINARY
    if not il2cpp and not bit64:
        return "mono_86"
    elif not il2cpp:
        return "mono_64"
    elif not bit64:
        return "il2cpp_86"
    else:
        return "il2cpp_64"


def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


def download_universaldemosaic():
    if os.path.isfile("BepInEx/plugins/DumbRendererDemosaic.dll") or os.path.isfile("BepInEx/plugins/DumbRendererDemosaicIl2Cpp.dll"):
        console.print("DumbRendererDemosaic is already installed!",
                      style="yellow on black")
        return
    arch = determine_arch()
    os.mkdir("Bepinex/plugins")
    if arch in ["mono_64", "mono_86"]:
        install_universaldemosaic_9(
            "https://github.com/ManlyMarco/UniversalUnityDemosaics/releases/download/v1.5/UniversalUnityDemosaics_BepInEx5_v1.5.zip",
            "DumbRendererDemosaic.dll",
        )
        os.system("del DumbTypeDemosaic.dll")
        os.system("del MaterialReplaceDemosaic.dll")
        os.system("del CubismModelDemosaic.dll")
        os.system("del CombinedMeshDemosaic.dll")
    elif arch in ["il2cpp_64", "il2cpp_86"]:
        install_universaldemosaic_9(
            "https://github.com/ManlyMarco/UniversalUnityDemosaics/releases/download/v1.5/UniversalUnityDemosaics_BepInEx6_IL2CPP_v1.5.zip",
            "DumbRendererDemosaicIl2Cpp.dll",
        )
    else:
        sys.exit("Something went wrong&&&")
    console.print("UniversalDemosaic installed!", style="green on black")

def install_universaldemosaic_9(arg0, arg1):
    download_url(arg0, "UniversalDemosaic.zip")
    unzip("UniversalDemosaic.zip")
    os.system("del UniversalDemosaic.zip")
    shutil.move(arg1, "BepInEx/plugins")
    os.system("del LICENSE")
    os.system("del README.md")


def download_bepinex6():
    if os.path.exists("BepInEx"):
        console.print("A Bepinex version is already installed!",
                      style="yellow on black")
        return
    if arch == "il2cpp_64":
        download_url(get_bepinex6IL2CPP64(), "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    elif arch == "il2cpp_86":
        download_url(get_bepinex6IL2CPP86(), "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    elif arch == "mono_64":
        download_url(get_bepinex664(), "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    elif arch == "mono_86":
        download_url(get_bepinex686(), "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    else:
        sys.exit("Something went wrong,,,")
    console.print("Bepinex 6 installed!", style="green on black")


def download_bepinex():
    if os.path.exists("BepInEx"):
        console.print("A Bepinex version is already installed!",
                      style="yellow on black")
        return
    if arch == "mono_64":
        download_url(get_bepinex64(), "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    elif arch == "mono_86":
        download_url(get_bepinex86(), "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    elif arch == "il2cpp_64":
        download_url(get_bepinexIL2CPP64(), "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    elif arch == "il2cpp_86":
        download_url(get_bepinexxIL2CPP86(), "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    else:
        sys.exit("Something went wrong!!!")
    console.print("Bepinex installed!", style="green on black")


def unzip(file: str):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall()


def download_autotranslator():
    if os.path.exists("BepInEx/plugins/XUnity.AutoTranslator"):
        console.print("AutoTranslator Plugin is already installed!",
                      style="yellow on black")
        return
    if arch in ["mono_64", "mono_86"]:
        install_autotranslator_7(
            "https://github.com/bbepis/XUnity.AutoTranslator/releases/download/v5.0.0/XUnity.AutoTranslator-BepInEx-5.0.0.zip"
        )
    elif arch in ["il2cpp_64", "il2cpp_86"]:
        install_autotranslator_7(
            "https://github.com/bbepis/XUnity.AutoTranslator/releases/download/v5.0.0/XUnity.AutoTranslator-BepInEx-IL2CPP-5.0.0.zip"
        )
    else:
        sys.exit("Something went wrong***")
    console.print("AutoTranslator Plugin installed!", style="green on black")

def install_autotranslator_7(arg0):
    download_url(arg0, "AutoTranslate.zip")
    unzip("AutoTranslate.zip")
    os.system("del AutoTranslate.zip")


def download_unityexplorer():
    if os.path.exists("BepInEx/plugins/sinai-dev-UnityExplorer"):
        console.print("UnityExplorer Plugin is already Installed!",
                      style="yellow on black")
        return
    try:
        if arch in ["mono_64", "mono_86"]:
            install_unityexplorer_8(
                "https://github.com/sinai-dev/UnityExplorer/releases/latest/download/UnityExplorer.BepInEx5.Mono.zip",
                "plugins/sinai-dev-UnityExplorer/",
                "plugins",
            )
        elif arch in ["il2cpp_64", "il2cpp_86"]:
            install_unityexplorer_8(
                "https://github.com/sinai-dev/UnityExplorer/releases/latest/download/UnityExplorer.BepInEx.Il2Cpp.zip",
                "UnityExplorer.BepInEx.IL2CPP/plugins/sinai-dev-UnityExplorer/",
                "UnityExplorer.BepInEx.IL2CPP",
            )
        else:
            sys.exit("Something went wrong///")
        console.print("UnityExplorer Plugin installed!",
                      style="green on black")
    except PermissionError:
        console.print("UnityExplorer Plugin installed!",
                      style="green on black")

def install_unityexplorer_8(arg0, arg1, arg2):
    download_url(arg0, "UnityExplorer.zip")
    unzip("UnityExplorer.zip")
    os.system("del UnityExplorer.zip")
    shutil.move(arg1, "BepInEx/plugins")
    if arg2 == "UnityExplorer.BepInEx.IL2CPP":
        os.rmdir("UnityExplorer.BepInEx.IL2CPP/plugins")
    os.rmdir(arg2)

def install_BEBuild6():
    if os.path.exists("BepInEx"):
        console.print("Bepinex is already installed!", style="yellow on black")
        return
    if arch == "mono_64":
        download_url(get_bepinexBEBuild64(), "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    elif arch == "mono_86":
        download_url(get_bepinexBEBuild86(), "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    elif arch == "il2cpp_64":
        download_url(get_bepinexBEBuildIL2CPP64(), "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    elif arch == "il2cpp_86":
        download_url(get_bepinexBEBuildIL2CPP86, "Bepinex.zip")
        unzip("Bepinex.zip")
        os.system("del Bepinex.zip")
    else:
        sys.exit("Something went wrong!!!")
    console.print("Bepinex 6 installed!", style="green on black")

def install_UnityExplorer6():
    if os.path.exists("BepInEx/plugins/sinai-dev-UnityExplorer"):
        console.print("UnityExplorer Plugin is already Installed!",
                      style="yellow on black")
        return
    if arch in ["mono_64", "mono_86"]:
        download_url("https://github.com/sinai-dev/UnityExplorer/releases/download/4.9.0/UnityExplorer.BepInEx6.Mono.zip", "UnityExplorer.zip")
        unzip("UnityExplorer.zip")
        os.system("del UnityExplorer.zip")
        shutil.move("plugins/sinai-dev-UnityExplorer", "BepInEx/plugins")
        os.rmdir("plugins")
    elif arch in ["il2cpp_64", "il2cpp_86"]:
        download_url("https://github.com/sinai-dev/UnityExplorer/releases/download/4.9.0/UnityExplorer.BepInEx.IL2CPP.zip", "UnityExplorer.zip")
        unzip("UnityExplorer.zip")
        os.system("del UnityExplorer.zip")
        shutil.move("UnityExplorer.BepInEx.IL2CPP/plugins/sinai-dev-UnityExplorer", "BepInEx/plugins")
        os.rmdir("UnityExplorer.BepInEx.IL2CPP/plugins")
        os.rmdir("UnityExplorer.BepInEx.IL2CPP")
    else:
        sys.exit("Something went wrong???")
    console.print("UnityExplorer Plugin installed!", style="green on black")

def install_TextureReplacer():
    if os.path.isfile("BepInEx/plugins/Texture_Replacer.dll") or os.path.isfile("BepInEx/plugins/Texture_Replacer_il2cpp.dll"):
        console.print("Texture Replacer Plugin is already Installed!",
                      style="yellow on black")
        return
    if arch in ["mono_64", "mono_86"]:
        download_url("https://attachments.f95zone.to/2023/01/2332348_Texture_Replacer_v1.0.4.1.zip", "Texture_Replacer.zip")
        unzip("Texture_Replacer.zip")
        os.system("del Texture_Replacer.zip")
        os.mkdir("BepInEx/plugins")
        shutil.move("Texture_Replacer.dll", "BepInEx/plugins")
        os.system("del Texture_Replacer_il2cpp.dll")
    elif arch in ["il2cpp_64", "il2cpp_86"]:
        download_url("https://attachments.f95zone.to/2023/01/2332348_Texture_Replacer_v1.0.4.1.zip", "Texture_Replacer.zip")
        unzip("Texture_Replacer.zip")
        os.system("del Texture_Replacer.zip")
        os.mkdir("BepInEx/plugins")
        shutil.move("Texture_Replacer_il2cpp.dll", "BepInEx/plugins")
        os.system("del Texture_Replacer.dll")
    else:
        sys.exit("Something went wrong???")
    console.print("Texture Replacer Plugin installed!", style="green on black")

def main():
    global arch
    console.rule("[bold blue]BepInEx Installer")
    print("")
    console.print(game_exe, style="yellow on black", justify="center")
    console.print("-----", justify="center", style="green on black")
    console.print(arch, style="yellow on black", justify="center")
    print("")
    console.print(
        "Choose what Plugins to include in this installation", justify="center")
    print("")
    console.print("1: Bepinex 5 & AutoTranslator",
                  justify="center", style="yellow on black")
    console.print("2: Bepinex 5 & UnityExplorer",
                  justify="center", style="yellow on black")
    console.print("3: Bepinex 5/6 & DumbRendererDemosaic",
                  justify="center", style="yellow on black")
    console.print("4: Bepinex 5/6 & Texture Replacer",
                    justify="center", style="yellow on black")
    console.print("5: Bepinex 6 & UnityExplorer",
                  justify="center", style="yellow on black")
    console.print("6: Only Bepinex 5", justify="center", style="yellow on black")
    console.print("7: Only Bepinex 6", justify="center",
                  style="yellow on black")
    console.print("8: Only Bepinex 6 Latest Bleeding Edge Build",
                  justify="center", style="yellow on black")
    a = int(input(""))
    os.system("cls")
    if a == 1:
        with console.status("Installing BepInEx 5..."):
            download_bepinex()
        with console.status("Installing AutoTranslator Plugin..."):
            download_autotranslator()
        console.print("Done!", style="green on black")
    elif a == 2:
        with console.status("Installing BepInEx 5..."):
            download_bepinex()
        with console.status("Installing UnityExplorer Plugin..."):
            download_unityexplorer()
        console.print("Done!", style="green on black")
    elif a == 3:
        if arch in ["mono_64", "mono_86"]:
            with console.status("Installing BepInEx 5..."):
                download_bepinex()
        else:
            with console.status("Installing Bepinex 6..."):
                download_bepinex6()
        with console.status("Installing DumbRendererDemosaic..."):
            download_universaldemosaic()
        console.print("Done!", style="green on black")
    elif a == 4:
        if arch in ["mono_64", "mono_86"]:
            with console.status("Installing BepInEx 5..."):
                download_bepinex()
        else:
            with console.status("Installing Bepinex 6..."):
                download_bepinex6()
        with console.status("Installing Texture Replacer Plugin..."):
            install_TextureReplacer()
        console.print("Done!", style="green on black")
    elif a == 5:
        with console.status("Installing Bepinex 6..."):
            download_bepinex6()
        with console.status("Installing UnityExplorer Plugin..."):
            install_UnityExplorer6()
        console.print("Done!", style="green on black")
    elif a == 6:
        with console.status("Installing BepInEx 5..."):
            download_bepinex()
        console.print("Done!", style="green on black")
    elif a == 7:
        with console.status("Installing BepiInEx 6..."):
            download_bepinex6()
        console.print("Done!", style="green on black")
    elif a == 8:
        with console.status("Installing Bepinex 6 Latest Bleeding Edge Build..."):
            install_BEBuild6()
        console.print("Done!", style="green on black")
    else:
        console.print("Invalid Input!", style="red on black")
    input("Press Enter to continue...")


if __name__ == "__main__":
    os.system("cls")
    arch = determine_arch()
    main()
