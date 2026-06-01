"""Audio nativo para Android via pyjnius (AudioTrack + AudioRecord).
Solo usa autoclass — jarray/jshort no están disponibles en el build Android.
"""

import os
import threading

import numpy as np

SAMPLE_RATE = 44100


class AndroidTonePlayer:
    """Oscilador continuo usando AudioTrack en modo STREAM con WRITE_BLOCKING."""

    def __init__(self):
        self.freq = 440.0
        self.phase = 0
        self._playing = False
        self._thread = None
        self._track = None
        self._ByteBuffer = None

    @property
    def stream(self):
        return self._track

    def start(self, freq: float):
        from jnius import autoclass
        AudioTrack  = autoclass('android.media.AudioTrack')
        AudioFormat = autoclass('android.media.AudioFormat')
        AudioManager = autoclass('android.media.AudioManager')
        self._ByteBuffer = autoclass('java.nio.ByteBuffer')

        self.stop()

        self.freq = freq
        self.phase = 0
        self._playing = True

        min_buf = AudioTrack.getMinBufferSize(
            SAMPLE_RATE,
            AudioFormat.CHANNEL_OUT_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
        )
        self._track = AudioTrack(
            AudioManager.STREAM_MUSIC,
            SAMPLE_RATE,
            AudioFormat.CHANNEL_OUT_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            min_buf * 8,
            AudioTrack.MODE_STREAM,
        )
        self._track.play()
        self._thread = threading.Thread(target=self._feed, daemon=True)
        self._thread.start()

    def _feed(self):
        CHUNK = 2048
        WRITE_BLOCKING = 0
        while self._playing:
            t = (self.phase + np.arange(CHUNK)) / SAMPLE_RATE
            samples = (0.4 * np.sin(2 * np.pi * self.freq * t) * 32767).astype(np.int16)
            self.phase += CHUNK
            raw = bytearray(samples.tobytes())
            buf = self._ByteBuffer.wrap(raw)
            self._track.write(buf, len(raw), WRITE_BLOCKING)

    def set_freq(self, freq: float):
        self.freq = freq

    def stop(self):
        self._playing = False
        if self._thread:
            self._thread.join(timeout=0.5)
            self._thread = None
        if self._track:
            try:
                self._track.stop()
                self._track.release()
            except Exception:
                pass
            self._track = None


class MicPermissionError(RuntimeError):
    pass


def _check_mic_permission():
    from jnius import autoclass
    ActivityThread = autoclass('android.app.ActivityThread')
    PackageManager = autoclass('android.content.pm.PackageManager')
    context = ActivityThread.currentApplication().getApplicationContext()
    granted = context.checkSelfPermission('android.permission.RECORD_AUDIO')
    if granted != PackageManager.PERMISSION_GRANTED:
        raise MicPermissionError("permiso_microfono")


def open_app_settings():
    from jnius import autoclass
    ActivityThread = autoclass('android.app.ActivityThread')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')
    context = ActivityThread.currentApplication().getApplicationContext()
    intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
    intent.setData(Uri.fromParts('package', context.getPackageName(), None))
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    context.startActivity(intent)


def android_record_audio() -> np.ndarray:
    from jnius import autoclass
    _check_mic_permission()
    AudioRecord = autoclass('android.media.AudioRecord')
    AudioFormat = autoclass('android.media.AudioFormat')

    DURATION = 3
    n_bytes  = SAMPLE_RATE * DURATION * 2  # int16 = 2 bytes/muestra
    chunk_sz = 8192

    min_buf = AudioRecord.getMinBufferSize(
        SAMPLE_RATE,
        AudioFormat.CHANNEL_IN_MONO,
        AudioFormat.ENCODING_PCM_16BIT,
    )
    recorder = AudioRecord(
        1,  # MediaRecorder.AudioSource.MIC
        SAMPLE_RATE,
        AudioFormat.CHANNEL_IN_MONO,
        AudioFormat.ENCODING_PCM_16BIT,
        max(min_buf, n_bytes),
    )

    raw     = bytearray()
    chunk   = bytearray(chunk_sz)
    written = 0

    recorder.startRecording()
    while written < n_bytes:
        to_read = min(chunk_sz, n_bytes - written)
        read = recorder.read(chunk, 0, to_read)
        if read > 0:
            raw    += chunk[:read]
            written += read
        elif read < 0:
            raise RuntimeError(f"Error AudioRecord: código {read}")
    recorder.stop()
    recorder.release()

    return np.frombuffer(bytes(raw[:n_bytes]), dtype=np.int16).astype(np.float32) / 32768.0
