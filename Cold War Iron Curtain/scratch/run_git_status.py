import subprocess

r = subprocess.run(['git', 'status', '--short'], cwd='Cold War Iron Curtain', capture_output=True, text=True)
print(r.stdout)
