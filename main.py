"""
Copyright (c) 2023, Henry1887
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. 
"""




import contextlib
import sys
import zipfile
import os
import shutil
import requests
import json
import win32file
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
        if file.endswith(".exe")
        and os.path.exists(file.replace(".exe", "") + "_Data")
    ]
    match len(games_in_cur_dir):
        case 0:
            console.print("Automatic Detection could not find any Game in the current Directory",
                    style="red on black")
            input("Press Enter to continue...")
            sys.exit(0)
        case 1:
            game_exe = os.path.join(os.getcwd(), games_in_cur_dir[0])
        case _:
            console.print("Multiple games found in this directory!",
                      style="red on black")
            console.print("Automatic Detection is not possible.",
                        style="red on black")
            input("Press Enter to continue...")
            sys.exit(0)
if not os.path.isfile(game_exe):
    console.print("Game not found!", style="red on black")
    input("Press Enter to continue...")
    sys.exit(0)

links = {
        "BEPINEXIL2CPP64": "https://builds.bepinex.dev/projects/bepinex_be/577/BepInEx_UnityIL2CPP_x64_ec79ad0_6.0.0-be.577.zip",
        "BEPINEXIL2CPP86": "https://builds.bepinex.dev/projects/bepinex_be/577/BepInEx_UnityIL2CPP_x86_ec79ad0_6.0.0-be.577.zip",
        "BEPINEX64": "https://github.com/BepInEx/BepInEx/releases/download/v5.4.21/BepInEx_x64_5.4.21.0.zip",
        "BEPINEX86": "https://github.com/BepInEx/BepInEx/releases/download/v5.4.21/BepInEx_x86_5.4.21.0.zip",
        "BEPINEX6IL2CPP64": "https://github.com/BepInEx/BepInEx/releases/download/v6.0.0-pre.1/BepInEx_UnityIL2CPP_x64_6.0.0-pre.1.zip",
        "BEPINEX6IL2CPP86": "https://github.com/BepInEx/BepInEx/releases/download/v6.0.0-pre.1/BepInEx_UnityIL2CPP_x86_6.0.0-pre.1.zip",
        "BEPINEX664": "https://github.com/BepInEx/BepInEx/releases/download/v6.0.0-pre.1/BepInEx_UnityMono_x64_6.0.0-pre.1.zip",
        "BEPINEX686": "https://github.com/BepInEx/BepInEx/releases/download/v6.0.0-pre.1/BepInEx_UnityMono_x86_6.0.0-pre.1.zip",
        "BEPINEXBEBUILD64": "https://builds.bepinex.dev/projects/bepinex_be/670/BepInEx-Unity.Mono-win-x64-6.0.0-be.670%2B42a6727.zip",
        "BEPINEXBEBUILD86": "https://builds.bepinex.dev/projects/bepinex_be/670/BepInEx-Unity.Mono-win-x86-6.0.0-be.670%2B42a6727.zip",
        "BEPINEXBEBUILDIL2CPP64": "https://builds.bepinex.dev/projects/bepinex_be/670/BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.670%2B42a6727.zip",
        "BEPINEXBEBUILDIL2CPP86": "https://builds.bepinex.dev/projects/bepinex_be/670/BepInEx-Unity.IL2CPP-win-x86-6.0.0-be.670%2B42a6727.zip",
        "UNIVERSALUNITYDEMOSAIC": "https://github.com/ManlyMarco/UniversalUnityDemosaics/releases/download/v1.5/UniversalUnityDemosaics_BepInEx5_v1.5.zip",
        "UNIVERSALUNITYDEMOSAICIL2CPP": "https://github.com/ManlyMarco/UniversalUnityDemosaics/releases/download/v1.5/UniversalUnityDemosaics_BepInEx6_IL2CPP_v1.5.zip",
        "AUTOTRANSLATOR": "https://github.com/bbepis/XUnity.AutoTranslator/releases/download/v5.0.0/XUnity.AutoTranslator-BepInEx-5.0.0.zip",
        "AUTOTRANSLATORIL2CPP": "https://github.com/bbepis/XUnity.AutoTranslator/releases/download/v5.0.0/XUnity.AutoTranslator-BepInEx-IL2CPP-5.0.0.zip",
        "UNITYEXPLORERBE5": "https://github.com/sinai-dev/UnityExplorer/releases/latest/download/UnityExplorer.BepInEx5.Mono.zip",
        "UNITYEXPLORERBE5IL2CPP": "https://github.com/sinai-dev/UnityExplorer/releases/latest/download/UnityExplorer.BepInEx.Il2Cpp.zip",
        "UNITYEXPLORERBE6": "https://github.com/sinai-dev/UnityExplorer/releases/download/4.9.0/UnityExplorer.BepInEx6.Mono.zip",
        "UNITYEXPLORERBE6IL2CPP": "https://github.com/sinai-dev/UnityExplorer/releases/download/4.9.0/UnityExplorer.BepInEx.IL2CPP.zip",
        "TEXTUREREPLACER": "https://attachments.f95zone.to/2023/06/2692158_Texture_Replacer_plugin_v1.0.5.1.zip",
        "ES3SAVEHOOKIL2CPP": "https://cdn.discordapp.com/attachments/1128766686275837963/1130514609963532381/ES3SaveHook_IL2CPP.zip",
        "ES3SAVEHOOK": "https://cdn.discordapp.com/attachments/1128766686275837963/1130513994663342221/ES3SaveHook_Mono.zip"
    }

if os.path.isfile("AutoInstaller-config.json"):
    with open("AutoInstaller-config.json", "r") as Config:
        new_links = json.load(Config)
    links |= new_links
else:
    with open("AutoInstaller-config.json", "w") as Config:
        json.dump(links, Config)

def determine_arch() -> str:
    match (os.path.isfile("GameAssembly.dll"), win32file.GetBinaryType(game_exe) != win32file.SCS_32BIT_BINARY):
        case (False, True):
            return "mono_64"
        case (False, False):
            return "mono_86"
        case (True, True):
            return "il2cpp_64"
        case (True, False):
            return "il2cpp_86"

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
    with contextlib.suppress(FileExistsError):
        os.mkdir("Bepinex/plugins")
    if arch in ["mono_64", "mono_86"]:
        download_url(links["UNIVERSALUNITYDEMOSAIC"], "UniversalDemosaic.zip")
        unzip("UniversalDemosaic.zip")
        os.system("del UniversalDemosaic.zip")
        shutil.move("DumbRendererDemosaic.dll", "BepInEx/plugins")
        os.system("del DumbTypeDemosaic.dll")
        os.system("del MaterialReplaceDemosaic.dll")
        os.system("del CubismModelDemosaic.dll")
        os.system("del CombinedMeshDemosaic.dll")
    elif arch in ["il2cpp_64", "il2cpp_86"]:
        download_url(links["UNIVERSALUNITYDEMOSAICIL2CPP"], "UniversalDemosaic.zip")
        unzip("UniversalDemosaic.zip")
        os.system("del UniversalDemosaic.zip")
        shutil.move("DumbRendererDemosaicIl2Cpp.dll", "BepInEx/plugins")
    os.system("del LICENSE")
    os.system("del README.md")
    console.print("UniversalDemosaic installed!", style="green on black")

def download_bepinex6():
    if os.path.exists("BepInEx"):
        console.print("A Bepinex version is already installed!",
                      style="yellow on black")
        return
    match arch:
        case "il2cpp_64":
            download_url(links["BEPINEX6IL2CPP64"], "Bepinex.zip")
        case "il2cpp_86":
            download_url(links["BEPINEX6IL2CPP86"], "Bepinex.zip")
        case "mono_64":
            download_url(links["BEPINEX664"], "Bepinex.zip")
        case "mono_86":
            download_url(links["BEPINEX686"], "Bepinex.zip")
    unzip("Bepinex.zip")
    os.system("del Bepinex.zip")
    console.print("Bepinex 6 installed!", style="green on black")

def download_bepinex():
    if os.path.exists("BepInEx"):
        console.print("A Bepinex version is already installed!",
                      style="yellow on black")
        return
    match arch:
        case "mono_64":
            download_url(links["BEPINEX64"], "Bepinex.zip")
        case "mono_86":
            download_url(links["BEPINEX86"], "Bepinex.zip")
        case "il2cpp_64":
            download_url(links["BEPINEXIL2CPP64"], "Bepinex.zip")
        case "il2cpp_86":
            download_url(links["BEPINEXIL2CPP86"], "Bepinex.zip")
    unzip("Bepinex.zip")
    os.system("del Bepinex.zip")
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
        download_url(links["AUTOTRANSLATOR"], "AutoTranslate.zip")
    elif arch in ["il2cpp_64", "il2cpp_86"]:
        download_url(links["AUTOTRANSLATORIL2CPP"], "AutoTranslate.zip")
    unzip("AutoTranslate.zip")
    os.system("del AutoTranslate.zip")
    console.print("AutoTranslator Plugin installed!", style="green on black")

def download_unityexplorer():
    if os.path.exists("BepInEx/plugins/sinai-dev-UnityExplorer"):
        console.print("UnityExplorer Plugin is already Installed!",
                      style="yellow on black")
        return
    try:
        if arch in ["mono_64", "mono_86"]:
            download_url(links["UNITYEXPLORERBE5"], "UnityExplorer.zip")
            unzip("UnityExplorer.zip")
            os.system("del UnityExplorer.zip")
            shutil.move("plugins/sinai-dev-UnityExplorer/", "BepInEx/plugins")
            os.rmdir("plugins")
        elif arch in ["il2cpp_64", "il2cpp_86"]:
            download_url(links["UNITYEXPLORERBE5IL2CPP"], "UnityExplorer.zip")
            unzip("UnityExplorer.zip")
            os.system("del UnityExplorer.zip")
            shutil.move("UnityExplorer.BepInEx.IL2CPP/plugins/sinai-dev-UnityExplorer/", "BepInEx/plugins")
            os.rmdir("UnityExplorer.BepInEx.IL2CPP/plugins")
            os.rmdir("UnityExplorer.BepInEx.IL2CPP")
        console.print("UnityExplorer Plugin installed!",
                      style="green on black")
    except PermissionError:
        console.print("UnityExplorer Plugin installed!",
                      style="green on black")

def install_BEBuild6():
    if os.path.exists("BepInEx"):
        console.print("Bepinex is already installed!", style="yellow on black")
        return
    match arch:
        case "mono_64":
            download_url(links["BEPINEXBEBUILD64"], "Bepinex.zip")
        case "mono_86":
            download_url(links["BEPINEXBEBUILD86"], "Bepinex.zip")
        case "il2cpp_64":
            download_url(links["BEPINEXBEBUILDIL2CPP64"], "Bepinex.zip")
        case "il2cpp_86":
            download_url(links["BEPINEXBEBUILDIL2CPP86"], "Bepinex.zip")
    unzip("Bepinex.zip")
    os.system("del Bepinex.zip")
    console.print("Bepinex 6 installed!", style="green on black")

def install_UnityExplorer6():
    if os.path.exists("BepInEx/plugins/sinai-dev-UnityExplorer"):
        console.print("UnityExplorer Plugin is already Installed!",
                      style="yellow on black")
        return
    if arch in ["mono_64", "mono_86"]:
        download_url(links["UNITYEXPLORERBE6"], "UnityExplorer.zip")
        unzip("UnityExplorer.zip")
        os.system("del UnityExplorer.zip")
        shutil.move("plugins/sinai-dev-UnityExplorer", "BepInEx/plugins")
        os.rmdir("plugins")
    elif arch in ["il2cpp_64", "il2cpp_86"]:
        download_url(links["UNITYEXPLORERBE6IL2CPP"], "UnityExplorer.zip")
        unzip("UnityExplorer.zip")
        os.system("del UnityExplorer.zip")
        shutil.move("UnityExplorer.BepInEx.IL2CPP/plugins/sinai-dev-UnityExplorer", "BepInEx/plugins")
        os.rmdir("UnityExplorer.BepInEx.IL2CPP/plugins")
        os.rmdir("UnityExplorer.BepInEx.IL2CPP")
    console.print("UnityExplorer Plugin installed!", style="green on black")

def install_TextureReplacer():
    if os.path.isfile("BepInEx/plugins/Texture_Replacer.dll") or os.path.isfile("BepInEx/plugins/Texture_Replacer_il2cpp.dll"):
        console.print("Texture Replacer Plugin is already Installed!",
                      style="yellow on black")
        return
    if arch in ["mono_64", "mono_86"]:
        download_url(links["TEXTUREREPLACER"], "Texture_Replacer.zip")
        unzip("Texture_Replacer.zip")
        os.system("del Texture_Replacer.zip")
        with contextlib.suppress(FileExistsError):
            os.mkdir("BepInEx/plugins")
        shutil.move("Texture_Replacer.dll", "BepInEx/plugins")
        os.system("del Texture_Replacer_il2cpp.dll")
    elif arch in ["il2cpp_64", "il2cpp_86"]:
        download_url(links["TEXTUREREPLACER"], "Texture_Replacer.zip")
        unzip("Texture_Replacer.zip")
        os.system("del Texture_Replacer.zip")
        with contextlib.suppress(FileExistsError):
            os.mkdir("BepInEx/plugins")
        shutil.move("Texture_Replacer_il2cpp.dll", "BepInEx/plugins")
        os.system("del Texture_Replacer.dll")
    console.print("Texture Replacer Plugin installed!", style="green on black")

def install_ES3SaveHook():
    if os.path.isfile("BepInEx/plugins/ES3SaveHook.dll"):
        console.print("ES3SaveHook Plugin is already Installed!",
                      style="yellow on black")
        return
    if arch in ["il2cpp_64", "il2cpp_86"]:
        download_url(links["ES3SAVEHOOKIL2CPP"], "ES3SaveHook.zip")
    else:
        download_url(links["ES3SAVEHOOK"], "ES3SaveHook.zip")
    unzip("ES3SaveHook.zip")
    os.system("del ES3SaveHook.zip")
    with contextlib.suppress(FileExistsError):
        os.mkdir("BepInEx/plugins")
    shutil.move("ES3SaveHook.dll", "BepInEx/plugins")
    console.print("ES3SaveHook Plugin installed!", style="green on black")

def main():
    global arch
    console.rule("[bold blue]BepInEx Installer v1.0.5")
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
    console.print("6: BepInEx 6 Latest Bleeding Edge Build & ES3SaveHook",
                  justify="center", style="yellow on black")
    console.print("7: Only Bepinex 5", justify="center", style="yellow on black")
    console.print("8: Only Bepinex 6", justify="center",
                  style="yellow on black")
    console.print("9: Only Bepinex 6 Latest Bleeding Edge Build",
                  justify="center", style="yellow on black")
    a = int(input(""))
    os.system("cls")
    match a:
        case 1:
            with console.status("Installing BepInEx 5..."):
                download_bepinex()
            with console.status("Installing AutoTranslator Plugin..."):
                download_autotranslator()
            console.print("Done!", style="green on black")
        case 2:
            with console.status("Installing BepInEx 5..."):
                download_bepinex()
            with console.status("Installing UnityExplorer Plugin..."):
                download_unityexplorer()
            console.print("Done!", style="green on black")
        case 3:
            if arch in ["mono_64", "mono_86"]:
                with console.status("Installing BepInEx 5..."):
                    download_bepinex()
            else:
                with console.status("Installing Bepinex 6..."):
                    download_bepinex6()
            with console.status("Installing DumbRendererDemosaic..."):
                download_universaldemosaic()
            console.print("Done!", style="green on black")
        case 4:
            if arch in ["mono_64", "mono_86"]:
                with console.status("Installing BepInEx 5..."):
                    download_bepinex()
            else:
                with console.status("Installing Bepinex 6..."):
                    download_bepinex6()
            with console.status("Installing Texture Replacer Plugin..."):
                install_TextureReplacer()
            console.print("Done!", style="green on black")
        case 5:
            with console.status("Installing Bepinex 6..."):
                download_bepinex6()
            with console.status("Installing UnityExplorer Plugin..."):
                install_UnityExplorer6()
            console.print("Done!", style="green on black")
        case 6:
            with console.status("Installing Bepinex 6 Latest Bleeding Edge Build..."):
                install_BEBuild6()
            with console.status("Installing ES3SaveHook Plugin..."):
                install_ES3SaveHook()
            console.print("Done!", style="green on black")
        case 7:
            with console.status("Installing BepInEx 5..."):
                download_bepinex()
            console.print("Done!", style="green on black")
        case 8:
            with console.status("Installing BepiInEx 6..."):
                download_bepinex6()
            console.print("Done!", style="green on black")
        case 9:
            with console.status("Installing Bepinex 6 Latest Bleeding Edge Build..."):
                install_BEBuild6()
            console.print("Done!", style="green on black")
        case _:
            console.print("Invalid Input!", style="red on black")
    input("Press Enter to continue...")


if __name__ == "__main__":
    os.system("cls")
    arch = determine_arch()
    main()
