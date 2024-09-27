import pyaudio

speaker_index = None

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    name = p.get_device_info_by_host_api_device_index(0, i).get('name')
    print(f"[{i}]: {name}")
    if "Speaker" in name: speaker_index = i

print("Output speaker index:", speaker_index)

