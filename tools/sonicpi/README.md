# Headless Sonic Pi render (TCP fix)

Sonic Pi 5.0.0 ships `headless-record.rb`, which sends `/supersonic/record/start` and
`/supersonic/record/stop` over UDP. The bundled SuperSonic engine (0.71.0) only listens on
TCP for its command plane, so start is silently dropped and stop fails with ECONNREFUSED and
no wav is written. These are patched copies: `headless_boot.rb` uses `TcpOscClient` for the
engine connection and `headless-record-tcp.rb` sends the two record calls over it. Nothing
inside the app bundle is modified.

Run from this directory:

    "/Applications/Sonic Pi.app/Contents/Resources/app/server/native/ruby/bin/ruby" \
      headless-record-tcp.rb -o out.wav -d 130 -f ../../media/src/tracks/three-little-birds.rb
    ffmpeg -i out.wav -codec:a libmp3lame -b:a 192k ../../media/track-three-little-birds.mp3

Recording is realtime (130 s takes 130 s). Sonic Pi symbol notes use `:cs4`, not `:c#4`
(`#` starts a Ruby comment); the closed hi-hat sample is `:drum_cymbal_closed`.
