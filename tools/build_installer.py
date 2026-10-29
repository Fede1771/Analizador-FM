"""Touchline Standalone Packaging & MSI Builder.
Builds the standalone Touchline executable and packages it into a native Windows Installer (.msi).
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = uuid.UUID('4e565251-5443-4c4e-8765-202610260001')


def find_wix():
    configured = os.environ.get('WIX_EXE')
    if configured and Path(configured).is_file():
        return configured
    local = ROOT / '.tmp/wix4/wix.exe'
    if local.exists():
        return str(local)
    wix_exe = Path(os.environ.get('USERPROFILE', '')) / '.dotnet/tools/wix.exe'
    if wix_exe.exists():
        return str(wix_exe)
    wix_which = shutil.which('wix')
    if wix_which:
        return wix_which
    raise FileNotFoundError("No se encontró el ejecutable de WiX (wix.exe). Ejecutá: dotnet tool install --global wix")


def build_pyinstaller():
    print("=== PASO 1: Compilando Touchline con PyInstaller ===")
    dist_touchline = ROOT / 'dist' / 'Touchline'
    
    python_exe = sys.executable
    cmd = [
        python_exe, '-m', 'PyInstaller',
        '--noconfirm',
        '--onedir',
        '--windowed',
        '--name', 'Touchline',
        '--icon', str(ROOT / 'web/touchline.ico'),
        '--add-data', f"{ROOT / 'web'};web",
        '--add-data', f"{ROOT / 'fm_app/data'};fm_app/data",
        '--collect-all', 'webview',
        '--collect-all', 'pythonnet',
        '--collect-all', 'clr_loader',
        '--collect-all', 'fmsave',
        str(ROOT / 'app_desktop.py')
    ]
    print(f"Ejecutando: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(ROOT), check=True)
    
    # Ensure touchline.ico is also directly in Touchline folder for shortcuts
    shutil.copy2(ROOT / 'web/touchline.ico', dist_touchline / 'touchline.ico')
    print("Compilación de PyInstaller completada con éxito.")


def generate_wix_source(dist_dir: Path, out_wxs: Path, icon_path: Path, license_path: Path, version='1.0.1'):
    print("=== PASO 2: Generando archivo fuente de WiX (.wxs) ===")
    dist_dir = dist_dir.resolve()
    
    dir_ids = {'': 'INSTALLFOLDER'}
    dir_counter = 0
    
    dirs = []
    files = []
    for root, dirnames, filenames in os.walk(dist_dir):
        rel_root = os.path.relpath(root, dist_dir)
        if rel_root == '.':
            rel_root = ''
        
        for d in sorted(dirnames):
            rel_d = os.path.normpath(os.path.join(rel_root, d)) if rel_root else d
            dir_counter += 1
            d_id = f"Dir_{dir_counter}"
            dir_ids[rel_d] = d_id
            dirs.append((rel_root, d, rel_d, d_id))
            
        for f in sorted(filenames):
            rel_f = os.path.normpath(os.path.join(rel_root, f)) if rel_root else f
            full_f = os.path.join(root, f)
            files.append((rel_root, f, rel_f, full_f))

    children = {}
    for parent_rel, d, rel_d, d_id in dirs:
        children.setdefault(parent_rel, []).append((d, rel_d, d_id))

    def render_dirs(parent_rel, indent=10):
        xml = []
        for d, rel_d, d_id in children.get(parent_rel, []):
            spaces = ' ' * indent
            xml.append(f'{spaces}<Directory Id="{d_id}" Name="{d}">')
            xml.extend(render_dirs(rel_d, indent + 2))
            xml.append(f'{spaces}</Directory>')
        return xml

    dir_hierarchy_xml = '\n'.join(render_dirs(''))

    components_xml = []
    feature_refs = ['<ComponentRef Id="C_Shortcuts" />']
    
    file_counter = 0
    for parent_rel, filename, rel_f, full_f in files:
        file_counter += 1
        target_dir_id = dir_ids[parent_rel]
        comp_guid = str(uuid.uuid5(NAMESPACE, 'comp:' + rel_f.lower()))
        
        if rel_f.lower() == 'touchline.exe':
            file_id = 'TouchlineExe'
            comp_id = 'C_TouchlineExe'
        else:
            file_id = f'F_{file_counter}'
            comp_id = f'C_{file_counter}'
            
        feature_refs.append(f'<ComponentRef Id="{comp_id}" />')
        abs_source = full_f.replace('\\', '/')
        
        components_xml.append(f'''    <Component Id="{comp_id}" Directory="{target_dir_id}" Guid="{comp_guid}">
      <File Id="{file_id}" Source="{abs_source}" KeyPath="yes" />
    </Component>''')

    posix_icon = str(icon_path.resolve()).replace('\\', '/')
    posix_license = str(license_path.resolve()).replace('\\', '/')

    wxs_content = f"""<Wix xmlns="http://wixtoolset.org/schemas/v4/wxs" xmlns:ui="http://wixtoolset.org/schemas/v4/wxs/ui">
  <Package Name="Touchline · Analizador FM26"
           Manufacturer="Touchline"
           Version="{version}"
           UpgradeCode="4E565251-5443-4C4E-8765-202610260001"
           Scope="perUser">
    <MajorUpgrade DowngradeErrorMessage="Ya hay una versión más reciente de Touchline instalada." />
    <MediaTemplate EmbedCab="yes" />
    <WixVariable Id="WixUILicenseRtf" Value="{posix_license}" />

    <Icon Id="AppIcon" SourceFile="{posix_icon}" />
    <Property Id="ARPPRODUCTICON" Value="AppIcon" />
    <Property Id="ARPHELPLINK" Value="https://github.com/Fede1771/Analizador-FM" />

    <StandardDirectory Id="LocalAppDataFolder">
      <Directory Id="ProgramsFolder" Name="Programs">
        <Directory Id="INSTALLFOLDER" Name="Touchline">
{dir_hierarchy_xml}
        </Directory>
      </Directory>
    </StandardDirectory>

    <StandardDirectory Id="ProgramMenuFolder">
      <Directory Id="AppProgramMenuFolder" Name="Touchline" />
    </StandardDirectory>

    <StandardDirectory Id="DesktopFolder" />

    <Component Id="C_Shortcuts" Directory="INSTALLFOLDER" Guid="5E565251-5443-4C4E-8765-202610260002">
      <Shortcut Id="DesktopShortcut"
                Directory="DesktopFolder"
                Name="Touchline · Analizador FM26"
                Target="[!TouchlineExe]"
                WorkingDirectory="INSTALLFOLDER"
                Icon="AppIcon" />
      <Shortcut Id="StartMenuShortcut"
                Directory="AppProgramMenuFolder"
                Name="Touchline · Analizador FM26"
                Target="[!TouchlineExe]"
                WorkingDirectory="INSTALLFOLDER"
                Icon="AppIcon" />
      <RemoveFolder Id="CleanAppProgramMenuFolder" Directory="AppProgramMenuFolder" On="uninstall" />
      <RegistryValue Root="HKCU" Key="Software\\Touchline\\Install" Name="Installed" Type="integer" Value="1" KeyPath="yes" />
    </Component>

{chr(10).join(components_xml)}

    <Feature Id="MainFeature" Title="Touchline · Analizador FM26" Level="1">
      {chr(10).join('      ' + r for r in feature_refs)}
    </Feature>

    <ui:WixUI Id="WixUI_InstallDir" InstallDirectory="INSTALLFOLDER" />
  </Package>
</Wix>"""

    out_wxs.parent.mkdir(parents=True, exist_ok=True)
    out_wxs.write_text(wxs_content, encoding='utf-8')
    print(f"Generado {out_wxs} con {len(files)} archivos y {len(dirs)} carpetas.")


def build_msi(wxs_file: Path, msi_output: Path):
    print("=== PASO 3: Compilando instalador .MSI con WiX ===")
    wix_cmd = find_wix()
    cmd = [
        wix_cmd, 'build',
        str(wxs_file),
        '-ext', 'WixToolset.UI.wixext',
        '-o', str(msi_output)
    ]
    print(f"Ejecutando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"¡Instalador MSI generado con éxito!\nDestino: {msi_output}\nTamaño: {msi_output.stat().st_size / (1024*1024):.2f} MB")


def main():
    parser = argparse.ArgumentParser(description="Touchline Standalone Packaging & MSI Builder")
    parser.add_argument('--skip-pyinstaller', action='store_true', help="Omitir el paso de PyInstaller si dist/Touchline ya existe")
    parser.add_argument('--version', default='1.0.1', help='Versión MSI (mayor.menor.revisión)')
    args = parser.parse_args()
    if len(args.version.split('.')) != 3 or not all(p.isdigit() and 0 <= int(p) <= 65535 for p in args.version.split('.')):
        parser.error('La versión debe tener tres números entre 0 y 65535.')

    dist_dir = ROOT / 'dist' / 'Touchline'
    if not args.skip_pyinstaller or not (dist_dir / 'Touchline.exe').exists():
        build_pyinstaller()
    else:
        print("Omitiendo PyInstaller (usando dist/Touchline existente).")

    wxs_path = ROOT / 'dist' / 'Touchline.wxs'
    icon_path = ROOT / 'web' / 'touchline.ico'
    license_path = ROOT / 'tools' / 'license.rtf'
    msi_path = ROOT / 'dist' / 'Touchline-Analizador-FM26.msi'

    generate_wix_source(dist_dir, wxs_path, icon_path, license_path, args.version)
    build_msi(wxs_path, msi_path)


if __name__ == '__main__':
    main()
