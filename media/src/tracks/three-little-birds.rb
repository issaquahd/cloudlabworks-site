# Three Little Birds - Bob Marley
# Sonic Pi Cover

use_bpm 74 # Classic reggae tempo

# 1. THE REGGAE SKANK (Chords played on the off-beat)
live_loop :piano_skank do
  use_synth :piano
  
  # Chorus/Verse structure generally uses A major and D major
  # We sleep 0.5 first to hit the off-beat (the "and" of the beat)
  
  4.times do # A Major chord section
    sleep 0.5
    play_chord [:a3, :cs4, :e4], release: 0.3, amp: 0.6
    sleep 0.5
  end
  
  4.times do # D Major chord section
    sleep 0.5
    play_chord [:d3, :fs4, :a4], release: 0.3, amp: 0.6
    sleep 0.5
  end
end

# 2. THE CHORUS MELODY ("Don't worry about a thing...")
live_loop :melody do
  use_synth :blade
  
  # "Don't worry... about a thing"
  notes1 =     [:cs5, :b4, :a4, :a4, :b4, :cs5, :a4]
  durations1 = [0.5,  0.5, 0.5, 1.0, 0.5, 0.5,  2.5]
  
  # "Cause every little thing... gonna be alright"
  notes2 =     [:cs5, :cs5, :b4, :a4, :a4, :b4, :cs5, :b4, :a4]
  durations2 = [0.5,  0.5,  0.5, 0.5, 1.0, 0.5, 0.5,  0.5, 1.5]
  
  # Play Part 1
  notes1.zip(durations1).each do |n, d|
    play n, attack: 0.05, release: d * 0.8, amp: 0.7
    sleep d
  end
  
  # Play Part 2
  notes2.zip(durations2).each do |n, d|
    play n, attack: 0.05, release: d * 0.8, amp: 0.7
    sleep d
  end
  
  sleep 2 # Pause before repeating the chorus
end

# 3. THE DRUM KIT (One-Drop Reggae Beat)
live_loop :drums do
  sample :bd_haus, amp: 0.8 # Bass drum on 1
  sleep 1
  
  sample :sn_dub, amp: 0.7   # Rimshot/Snare on 2 and 4
  sample :bd_haus, amp: 0.8
  sleep 1
  
  sleep 1
  
  sample :sn_dub, amp: 0.7
  sleep 1
end

# 4. THE HI-HAT (Steady eighth notes)
live_loop :hihat do
  sample :drum_cymbal_closed, amp: 0.4, rate: 1.5
  sleep 0.5
end
