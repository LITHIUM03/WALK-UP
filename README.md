# WALK-UP
 ESP32 based intelligent alarm clock. Communicates with Garmin servers to collect step count data thus ensuring the user got off the bed. Python/C++/Linux. Different parts communicate over MQTT.
 
 This is all the code needed to remake the alarm clock. Many more features can be added- feel free to implement them yourself or offer them.
 
 For further reading please refer to [this](ynet.co.il) blogpost.
 
### Notes:

1. When I refer to RPi, this can be any Linux running home server.. a cheap streamer, a 10M$ supercomputer, an old laptop, etc. 
2. To run the daemon constantly, please create a cron job for it. it will make the daemon start when the server boots.
3. Some DEBUG prints are commented-out for your convenience. Feel free to uncomment them to better understand the code. 

For sound samples , please refer to [XTronical's guide](https://www.xtronical.com/basics/audio/dacs-for-sound/playing-wav-files/). You can use the built in sample that comes with the library, or sample your own favorite song. After a few uses of the WALK_UP, it is guaranteed to be your most hated song.
