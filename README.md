# WALK-UP
 ESP32 based intelligent alarm clock. Communicates with Garmin servers to collect step count data thus ensuring the user got off the bed. Python/C++/Linux. Different parts communicate over MQTT.
![20220616_004233-min](https://user-images.githubusercontent.com/53534129/174028380-de6bb0cd-1685-4dac-85c3-21e8f17bcf8c.jpg)

 
 This is all the code needed to remake the alarm clock. Many more features can be added- feel free to implement them yourself or offer them.
 
 For further reading please refer to [this](http://whatimade.today/today-i-made-walk-up-the-alarm-clock-that-will-walk-you-off-the-bed-2/) blogpost.
 
### Notes:

1. When I refer to RPi, this can be any Linux running home server.. a cheap streamer, a 10M$ supercomputer, an old laptop, etc. 
2. To run the daemon constantly, please create a cron job for it. it will make the daemon start when the server boots.
3. Some DEBUG prints are commented-out for your convenience. Feel free to uncomment them to better understand the code. 

For sound samples , please refer to [XTronical's guide](https://www.xtronical.com/basics/audio/dacs-for-sound/playing-wav-files/). You can use the built in sample that comes with the library, or sample your own favorite song. Beware-after a few uses of the WALK-UP, it is guaranteed to be your most hated song.
